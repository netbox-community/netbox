import json
import uuid
from unittest.mock import patch

import django_rq
from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import reverse
from requests import Session
from rest_framework import status

from core.events import *
from core.models import ObjectType
from dcim.choices import SiteStatusChoices
from dcim.models import Site
from extras.choices import EventRuleActionChoices
from extras.events import enqueue_event, flush_events, serialize_for_event
from extras.models import EventRule, Tag, Webhook
from extras.webhooks import generate_signature, send_webhook
from netbox.context_managers import event_tracking
from utilities.testing import APITestCase


class EventRuleTest(APITestCase):

    def setUp(self):
        super().setUp()

        # Ensure the queue has been cleared for each test
        self.queue = django_rq.get_queue('default')
        self.queue.empty()

    @classmethod
    def setUpTestData(cls):

        site_type = ObjectType.objects.get_for_model(Site)
        DUMMY_URL = 'http://localhost:9000/'
        DUMMY_SECRET = 'LOOKATMEIMASECRETSTRING'

        webhooks = Webhook.objects.bulk_create((
            Webhook(name='Webhook 1', payload_url=DUMMY_URL, secret=DUMMY_SECRET, additional_headers='X-Foo: Bar'),
            Webhook(name='Webhook 2', payload_url=DUMMY_URL, secret=DUMMY_SECRET),
            Webhook(name='Webhook 3', payload_url=DUMMY_URL, secret=DUMMY_SECRET),
        ))

        webhook_type = ObjectType.objects.get(app_label='extras', model='webhook')
        event_rules = EventRule.objects.bulk_create((
            EventRule(
                name='Event Rule 1',
                event_types=[OBJECT_CREATED],
                action_type=EventRuleActionChoices.WEBHOOK,
                action_object_type=webhook_type,
                action_object_id=webhooks[0].id,
                action_data={"foo": 1},
            ),
            EventRule(
                name='Event Rule 2',
                event_types=[OBJECT_UPDATED],
                action_type=EventRuleActionChoices.WEBHOOK,
                action_object_type=webhook_type,
                action_object_id=webhooks[0].id,
                action_data={"foo": 2},
            ),
            EventRule(
                name='Event Rule 3',
                event_types=[OBJECT_DELETED],
                action_type=EventRuleActionChoices.WEBHOOK,
                action_object_type=webhook_type,
                action_object_id=webhooks[0].id,
                action_data={"foo": 3},
            ),
        ))
        for event_rule in event_rules:
            event_rule.object_types.set([site_type])

        Tag.objects.bulk_create((
            Tag(name='Foo', slug='foo'),
            Tag(name='Bar', slug='bar'),
            Tag(name='Baz', slug='baz'),
        ))

    def test_eventrule_conditions(self):
        """
        Test evaluation of EventRule conditions.
        """
        event_rule = EventRule(
            name='Event Rule 1',
            event_types=[OBJECT_CREATED, OBJECT_UPDATED],
            conditions={
                'and': [
                    {
                        'attr': 'status.value',
                        'value': 'active',
                    }
                ]
            }
        )

        # Create a Site to evaluate
        site = Site.objects.create(name='Site 1', slug='site-1', status=SiteStatusChoices.STATUS_STAGING)
        data = serialize_for_event(site)

        # Evaluate the conditions (status='staging')
        self.assertFalse(event_rule.eval_conditions(data))

        # Change the site's status
        site.status = SiteStatusChoices.STATUS_ACTIVE
        data = serialize_for_event(site)

        # Evaluate the conditions (status='active')
        self.assertTrue(event_rule.eval_conditions(data))

    def test_single_create_process_eventrule(self):
        """
        Check that creating an object with an applicable EventRule queues a background task for the rule's action.
        """
        # Create an object via the REST API
        data = {
            'name': 'Site 1',
            'slug': 'site-1',
            'tags': [
                {'name': 'Foo'},
                {'name': 'Bar'},
            ]
        }
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.add_site')
        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Site.objects.count(), 1)
        self.assertEqual(Site.objects.first().tags.count(), 2)

        # Verify that a background task was queued for the new object
        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(job.kwargs['event_rule'], EventRule.objects.get(name='Event Rule 1'))
        self.assertEqual(job.kwargs['event_type'], OBJECT_CREATED)
        self.assertEqual(job.kwargs['model_name'], 'site')
        self.assertEqual(job.kwargs['data']['id'], response.data['id'])
        self.assertEqual(job.kwargs['data']['foo'], 1)
        self.assertEqual(len(job.kwargs['data']['tags']), len(response.data['tags']))
        self.assertEqual(job.kwargs['snapshots']['postchange']['name'], 'Site 1')
        self.assertEqual(job.kwargs['snapshots']['postchange']['tags'], ['Bar', 'Foo'])

    def test_bulk_create_process_eventrule(self):
        """
        Check that bulk creating multiple objects with an applicable EventRule queues a background task for each
        new object.
        """
        # Create multiple objects via the REST API
        data = [
            {
                'name': 'Site 1',
                'slug': 'site-1',
                'tags': [
                    {'name': 'Foo'},
                    {'name': 'Bar'},
                ]
            },
            {
                'name': 'Site 2',
                'slug': 'site-2',
                'tags': [
                    {'name': 'Foo'},
                    {'name': 'Bar'},
                ]
            },
            {
                'name': 'Site 3',
                'slug': 'site-3',
                'tags': [
                    {'name': 'Foo'},
                    {'name': 'Bar'},
                ]
            },
        ]
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.add_site')
        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Site.objects.count(), 3)
        self.assertEqual(Site.objects.first().tags.count(), 2)

        # Verify that a background task was queued for each new object
        self.assertEqual(self.queue.count, 3)
        for i, job in enumerate(self.queue.jobs):
            self.assertEqual(job.kwargs['event_rule'], EventRule.objects.get(name='Event Rule 1'))
            self.assertEqual(job.kwargs['event_type'], OBJECT_CREATED)
            self.assertEqual(job.kwargs['model_name'], 'site')
            self.assertEqual(job.kwargs['data']['id'], response.data[i]['id'])
            self.assertEqual(job.kwargs['data']['foo'], 1)
            self.assertEqual(len(job.kwargs['data']['tags']), len(response.data[i]['tags']))
            self.assertEqual(job.kwargs['snapshots']['postchange']['name'], response.data[i]['name'])
            self.assertEqual(job.kwargs['snapshots']['postchange']['tags'], ['Bar', 'Foo'])

    def test_single_update_process_eventrule(self):
        """
        Check that updating an object with an applicable EventRule queues a background task for the rule's action.
        """
        site = Site.objects.create(name='Site 1', slug='site-1')
        site.tags.set(Tag.objects.filter(name__in=['Foo', 'Bar']))

        # Update an object via the REST API
        data = {
            'name': 'Site X',
            'comments': 'Updated the site',
            'tags': [
                {'name': 'Baz'}
            ]
        }
        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})
        self.add_permissions('dcim.change_site')
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        # Verify that a background task was queued for the updated object
        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(job.kwargs['event_rule'], EventRule.objects.get(name='Event Rule 2'))
        self.assertEqual(job.kwargs['event_type'], OBJECT_UPDATED)
        self.assertEqual(job.kwargs['model_name'], 'site')
        self.assertEqual(job.kwargs['data']['id'], site.pk)
        self.assertEqual(job.kwargs['data']['foo'], 2)
        self.assertEqual(len(job.kwargs['data']['tags']), len(response.data['tags']))
        self.assertEqual(job.kwargs['snapshots']['prechange']['name'], 'Site 1')
        self.assertEqual(job.kwargs['snapshots']['prechange']['tags'], ['Bar', 'Foo'])
        self.assertEqual(job.kwargs['snapshots']['postchange']['name'], 'Site X')
        self.assertEqual(job.kwargs['snapshots']['postchange']['tags'], ['Baz'])

    def test_bulk_update_process_eventrule(self):
        """
        Check that bulk updating multiple objects with an applicable EventRule queues a background task for each
        updated object.
        """
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)
        for site in sites:
            site.tags.set(Tag.objects.filter(name__in=['Foo', 'Bar']))

        # Update three objects via the REST API
        data = [
            {
                'id': sites[0].pk,
                'name': 'Site X',
                'tags': [
                    {'name': 'Baz'}
                ]
            },
            {
                'id': sites[1].pk,
                'name': 'Site Y',
                'tags': [
                    {'name': 'Baz'}
                ]
            },
            {
                'id': sites[2].pk,
                'name': 'Site Z',
                'tags': [
                    {'name': 'Baz'}
                ]
            },
        ]
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.change_site')
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        # Verify that a background task was queued for each updated object
        self.assertEqual(self.queue.count, 3)
        for i, job in enumerate(self.queue.jobs):
            self.assertEqual(job.kwargs['event_rule'], EventRule.objects.get(name='Event Rule 2'))
            self.assertEqual(job.kwargs['event_type'], OBJECT_UPDATED)
            self.assertEqual(job.kwargs['model_name'], 'site')
            self.assertEqual(job.kwargs['data']['id'], data[i]['id'])
            self.assertEqual(job.kwargs['data']['foo'], 2)
            self.assertEqual(len(job.kwargs['data']['tags']), len(response.data[i]['tags']))
            self.assertEqual(job.kwargs['snapshots']['prechange']['name'], sites[i].name)
            self.assertEqual(job.kwargs['snapshots']['prechange']['tags'], ['Bar', 'Foo'])
            self.assertEqual(job.kwargs['snapshots']['postchange']['name'], response.data[i]['name'])
            self.assertEqual(job.kwargs['snapshots']['postchange']['tags'], ['Baz'])

    def test_single_delete_process_eventrule(self):
        """
        Check that deleting an object with an applicable EventRule queues a background task for the rule's action.
        """
        site = Site.objects.create(name='Site 1', slug='site-1')
        site.tags.set(Tag.objects.filter(name__in=['Foo', 'Bar']))

        # Delete an object via the REST API
        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})
        self.add_permissions('dcim.delete_site')
        response = self.client.delete(url, **self.header)
        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)

        # Verify that a task was queued for the deleted object
        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(job.kwargs['event_rule'], EventRule.objects.get(name='Event Rule 3'))
        self.assertEqual(job.kwargs['event_type'], OBJECT_DELETED)
        self.assertEqual(job.kwargs['model_name'], 'site')
        self.assertEqual(job.kwargs['data']['id'], site.pk)
        self.assertEqual(job.kwargs['data']['foo'], 3)
        self.assertEqual(job.kwargs['snapshots']['prechange']['name'], 'Site 1')
        self.assertEqual(job.kwargs['snapshots']['prechange']['tags'], ['Bar', 'Foo'])

    def test_bulk_delete_process_eventrule(self):
        """
        Check that bulk deleting multiple objects with an applicable EventRule queues a background task for each
        deleted object.
        """
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)
        for site in sites:
            site.tags.set(Tag.objects.filter(name__in=['Foo', 'Bar']))

        # Delete three objects via the REST API
        data = [
            {'id': site.pk} for site in sites
        ]
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.delete_site')
        response = self.client.delete(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)

        # Verify that a background task was queued for each deleted object
        self.assertEqual(self.queue.count, 3)
        for i, job in enumerate(self.queue.jobs):
            self.assertEqual(job.kwargs['event_rule'], EventRule.objects.get(name='Event Rule 3'))
            self.assertEqual(job.kwargs['event_type'], OBJECT_DELETED)
            self.assertEqual(job.kwargs['model_name'], 'site')
            self.assertEqual(job.kwargs['data']['id'], sites[i].pk)
            self.assertEqual(job.kwargs['data']['foo'], 3)
            self.assertEqual(job.kwargs['snapshots']['prechange']['name'], sites[i].name)
            self.assertEqual(job.kwargs['snapshots']['prechange']['tags'], ['Bar', 'Foo'])

    def test_send_webhook(self):
        request_id = uuid.uuid4()

        def dummy_send(_, request, **kwargs):
            """
            A dummy implementation of Session.send() to be used for testing.
            Always returns a 200 HTTP response.
            """
            event = EventRule.objects.get(name='Event Rule 1')
            webhook = event.action_object
            signature = generate_signature(request.body, webhook.secret)

            # Validate the outgoing request headers
            self.assertEqual(request.headers['Content-Type'], webhook.http_content_type)
            self.assertEqual(request.headers['X-Hook-Signature'], signature)
            self.assertEqual(request.headers['X-Foo'], 'Bar')

            # Validate the outgoing request body
            body = json.loads(request.body)
            self.assertEqual(body['event'], 'created')
            self.assertEqual(body['timestamp'], job.kwargs['timestamp'])
            self.assertEqual(body['model'], 'site')
            self.assertEqual(body['username'], 'testuser')
            self.assertEqual(body['request_id'], str(request_id))
            self.assertEqual(body['data']['name'], 'Site 1')
            self.assertEqual(body['data']['foo'], 1)

            return HttpResponse()

        # Enqueue a webhook for processing
        webhooks_queue = {}
        site = Site.objects.create(name='Site 1', slug='site-1')
        enqueue_event(
            webhooks_queue,
            instance=site,
            user=self.user,
            request_id=request_id,
            event_type=OBJECT_CREATED
        )
        flush_events(list(webhooks_queue.values()))

        # Retrieve the job from queue
        job = self.queue.jobs[0]

        # Patch the Session object with our dummy_send() method, then process the webhook for sending
        with patch.object(Session, 'send', dummy_send):
            send_webhook(**job.kwargs)

    def test_duplicate_triggers(self):
        """
        Test for erroneous duplicate event triggers resulting from saving an object multiple times
        within the span of a single request.
        """
        url = reverse('dcim:site_add')
        request = RequestFactory().get(url)
        request.id = uuid.uuid4()
        request.user = self.user

        # Test create & update
        with event_tracking(request):
            site = Site(name='Site 1', slug='site-1')
            site.save()
            site.description = 'foo'
            site.save()
        self.assertEqual(self.queue.count, 1, msg="Duplicate jobs found in queue")
        job = self.queue.get_jobs()[0]
        self.assertEqual(job.kwargs['event_type'], OBJECT_CREATED)
        self.queue.empty()

        # Test multiple updates
        site = Site.objects.create(name='Site 2', slug='site-2')
        with event_tracking(request):
            site.description = 'foo'
            site.save()
            site.description = 'bar'
            site.save()
        self.assertEqual(self.queue.count, 1, msg="Duplicate jobs found in queue")
        job = self.queue.get_jobs()[0]
        self.assertEqual(job.kwargs['event_type'], OBJECT_UPDATED)
        self.queue.empty()

        # Test update & delete
        site = Site.objects.create(name='Site 3', slug='site-3')
        with event_tracking(request):
            site.description = 'foo'
            site.save()
            site.delete()
        self.assertEqual(self.queue.count, 1, msg="Duplicate jobs found in queue")
        job = self.queue.get_jobs()[0]
        self.assertEqual(job.kwargs['event_type'], OBJECT_DELETED)
        self.queue.empty()
