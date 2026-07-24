import json
import logging
import uuid
from io import BytesIO
from unittest import skipIf
from unittest.mock import Mock, patch

import django_rq
from django.conf import settings
from django.http import HttpResponse
from django.test import RequestFactory, tag
from django.urls import reverse
from PIL import Image
from requests import Session
from rest_framework import status

from core.choices import ManagedFileRootPathChoices
from core.events import *
from core.models import Job, ObjectType
from dcim.choices import SiteStatusChoices
from dcim.models import DeviceType, Interface, Manufacturer, Site
from extras.choices import EventRuleActionChoices
from extras.events import enqueue_event, flush_events, serialize_for_event
from extras.models import EventRule, Script, ScriptModule, Tag, Webhook
from extras.scripts import Script as ScriptBase
from extras.signals import process_job_end_event_rules
from extras.webhooks import generate_signature, send_webhook
from netbox.context_managers import event_tracking
from utilities.testing import APITestCase, create_test_device
from utilities.testing.mixins import RQQueueTestMixin


class EventRuleTestCase(RQQueueTestMixin, APITestCase):

    def setUp(self):
        super().setUp()

        # Ensure the queue has been cleared for each test
        self.queue = django_rq.get_queue('default')
        self.queue.empty()

    def tearDown(self):
        super().tearDown()

        # Clear the queue so leftover jobs do not leak to the next test suite
        self.queue.empty()

    def test_enqueue_event_requires_saved_instance(self):
        """enqueue_event raises ValueError for an unsaved instance."""
        request = RequestFactory().get('/')
        request.id = uuid.uuid4()
        request.user = self.user
        site = Site(name='Site 1', slug='site-1')
        with patch('extras.events.has_feature', return_value=True):
            with self.assertRaises(ValueError):
                enqueue_event({}, site, request, OBJECT_CREATED)

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

    def test_eventrule_snapshot_changed_condition(self):
        """
        An event rule using the 'changed' operator fires only when the attribute
        transitions to the target value, not on subsequent updates that leave it
        unchanged.  Exercises the full process_event_rules() path.
        """
        webhook = Webhook.objects.get(name='Webhook 1')
        webhook_type = ObjectType.objects.get_for_model(Webhook)
        site_type = ObjectType.objects.get_for_model(Site)
        event_rule = EventRule.objects.create(
            name='Status Change Rule',
            event_types=[OBJECT_UPDATED],
            action_type=EventRuleActionChoices.WEBHOOK,
            action_object_type=webhook_type,
            action_object_id=webhook.pk,
            conditions={
                'and': [
                    {'attr': 'status.value', 'value': SiteStatusChoices.STATUS_ACTIVE},
                    {'attr': 'status', 'op': 'changed'},
                ]
            }
        )
        event_rule.object_types.set([site_type])

        site = Site.objects.create(name='Site Snapshot', slug='site-snapshot', status=SiteStatusChoices.STATUS_PLANNED)
        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})
        self.add_permissions('dcim.change_site')

        # planned → active: the 'changed' condition is satisfied; rule must fire
        response = self.client.patch(url, {'status': SiteStatusChoices.STATUS_ACTIVE}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        rule_jobs = [j for j in self.queue.jobs if j.kwargs['event_rule'] == event_rule]
        self.assertEqual(len(rule_jobs), 1, 'Expected rule to fire on status transition to active')
        self.queue.empty()

        # description update while status stays active: 'changed' condition fails; rule must not fire
        response = self.client.patch(url, {'description': 'Updated'}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        rule_jobs = [j for j in self.queue.jobs if j.kwargs['event_rule'] == event_rule]
        self.assertEqual(len(rule_jobs), 0, 'Expected rule not to fire when status is unchanged')

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
        self.add_permissions('dcim.add_site', 'extras.view_tag')
        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Site.objects.count(), 1)
        self.assertEqual(Site.objects.first().tags.count(), 2)

        # Verify that a background task was queued for the new object
        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(job.kwargs['event_rule'], EventRule.objects.get(name='Event Rule 1'))
        self.assertEqual(job.kwargs['event_type'], OBJECT_CREATED)
        self.assertEqual(job.kwargs['object_type'], ObjectType.objects.get_for_model(Site))
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
        self.add_permissions('dcim.add_site', 'extras.view_tag')
        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Site.objects.count(), 3)
        self.assertEqual(Site.objects.first().tags.count(), 2)

        # Verify that a background task was queued for each new object
        self.assertEqual(self.queue.count, 3)
        for i, job in enumerate(self.queue.jobs):
            self.assertEqual(job.kwargs['event_rule'], EventRule.objects.get(name='Event Rule 1'))
            self.assertEqual(job.kwargs['event_type'], OBJECT_CREATED)
            self.assertEqual(job.kwargs['object_type'], ObjectType.objects.get_for_model(Site))
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
        self.add_permissions('dcim.change_site', 'extras.view_tag')
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        # Verify that a background task was queued for the updated object
        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(job.kwargs['event_rule'], EventRule.objects.get(name='Event Rule 2'))
        self.assertEqual(job.kwargs['event_type'], OBJECT_UPDATED)
        self.assertEqual(job.kwargs['object_type'], ObjectType.objects.get_for_model(Site))
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
        self.add_permissions('dcim.change_site', 'extras.view_tag')
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        # Verify that a background task was queued for each updated object
        self.assertEqual(self.queue.count, 3)
        for i, job in enumerate(self.queue.jobs):
            self.assertEqual(job.kwargs['event_rule'], EventRule.objects.get(name='Event Rule 2'))
            self.assertEqual(job.kwargs['event_type'], OBJECT_UPDATED)
            self.assertEqual(job.kwargs['object_type'], ObjectType.objects.get_for_model(Site))
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
        self.assertEqual(job.kwargs['object_type'], ObjectType.objects.get_for_model(Site))
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
            self.assertEqual(job.kwargs['object_type'], ObjectType.objects.get_for_model(Site))
            self.assertEqual(job.kwargs['data']['id'], sites[i].pk)
            self.assertEqual(job.kwargs['data']['foo'], 3)
            self.assertEqual(job.kwargs['snapshots']['prechange']['name'], sites[i].name)
            self.assertEqual(job.kwargs['snapshots']['prechange']['tags'], ['Bar', 'Foo'])

    @skipIf('netbox.tests.dummy_plugin' not in settings.PLUGINS, 'dummy_plugin not in settings.PLUGINS')
    def test_send_webhook(self):
        request_id = uuid.uuid4()
        url_path = reverse('dcim:site_add')

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

            # The webhook does not define its own timeout, so the global default should be used
            self.assertEqual(kwargs['timeout'], settings.WEBHOOK_DEFAULT_TIMEOUT)

            # Validate the outgoing request body
            body = json.loads(request.body)
            self.assertEqual(body['event'], 'created')
            self.assertEqual(body['timestamp'], job.kwargs['timestamp'])
            self.assertEqual(body['object_type'], 'dcim.site')
            self.assertEqual(body['data']['name'], 'Site 1')
            self.assertEqual(body['data']['foo'], 1)
            self.assertEqual(body['context']['foo'], 123)  # From netbox.tests.dummy_plugin
            self.assertEqual(body['request']['id'], str(request_id))
            self.assertEqual(body['request']['method'], 'GET')
            self.assertEqual(body['request']['path'], url_path)
            self.assertEqual(body['request']['user'], 'testuser')

            return HttpResponse()

        # Create a dummy request
        request = RequestFactory().get(url_path)
        request.id = request_id
        request.user = self.user

        # Enqueue a webhook for processing
        webhooks_queue = {}
        site = Site.objects.create(name='Site 1', slug='site-1')
        enqueue_event(
            webhooks_queue,
            instance=site,
            request=request,
            event_type=OBJECT_CREATED,
        )
        flush_events(list(webhooks_queue.values()))

        # Retrieve the job from queue
        job = self.queue.jobs[0]

        # Patch the Session object with our dummy_send() method, then process the webhook for sending
        with patch.object(Session, 'send', dummy_send):
            send_webhook(**job.kwargs)

    def test_send_webhook_per_webhook_timeout(self):
        """
        A webhook which defines its own timeout should use that value in preference to the
        global WEBHOOK_DEFAULT_TIMEOUT.
        """
        webhook = Webhook.objects.get(name='Webhook 1')
        webhook.timeout = 5
        webhook.save()

        def dummy_send(_, request, **kwargs):
            self.assertEqual(kwargs['timeout'], 5)
            return HttpResponse()

        request = RequestFactory().get(reverse('dcim:site_add'))
        request.id = uuid.uuid4()
        request.user = self.user

        webhooks_queue = {}
        site = Site.objects.create(name='Site 1', slug='site-1')
        enqueue_event(
            webhooks_queue,
            instance=site,
            request=request,
            event_type=OBJECT_CREATED,
        )
        flush_events(list(webhooks_queue.values()))

        job = self.queue.jobs[0]
        with patch.object(Session, 'send', dummy_send):
            send_webhook(**job.kwargs)

    def test_job_completed_webhook_without_request(self):
        """
        Ensure job_end event processing can enqueue a webhook even when the EventContext
        lacks a request context.

        The job_start/job_end signal receivers only populate `user` and `data`, so webhook
        processing must tolerate the absence of a request.
        """
        script_type = ObjectType.objects.get_for_model(Script)
        webhook_type = ObjectType.objects.get_for_model(Webhook)
        webhook = Webhook.objects.get(name='Webhook 1')
        event_rule = EventRule.objects.create(
            name='Event Rule Job Completed',
            event_types=[JOB_COMPLETED],
            action_type=EventRuleActionChoices.WEBHOOK,
            action_object_type=webhook_type,
            action_object_id=webhook.pk,
        )
        event_rule.object_types.set([script_type])
        # Mimic the `core.job_end` signal sender expected by extras.signals.process_job_end_event_rules
        # (notably: no request, and thus no legacy `username`)
        sender = Mock(object_type=script_type, data={}, user=self.user)
        process_job_end_event_rules(sender)
        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(job.kwargs['event_rule'], event_rule)
        self.assertEqual(job.kwargs['event_type'], JOB_COMPLETED)
        self.assertEqual(job.kwargs['object_type'], script_type)
        self.assertNotIn('request', job.kwargs)

    def test_duplicate_enqueue_refreshes_lazy_payload(self):
        """
        When the same object is enqueued more than once in a single request,
        lazy serialization should use the most recently enqueued instance while
        preserving the original event['object'] reference.
        """
        request = RequestFactory().get(reverse('dcim:site_add'))
        request.id = uuid.uuid4()
        request.user = self.user

        site = Site.objects.create(name='Site 1', slug='site-1')
        stale_site = Site.objects.get(pk=site.pk)

        queue = {}
        enqueue_event(queue, stale_site, request, OBJECT_UPDATED)

        event = queue[f'dcim.site:{site.pk}']

        # Data should not be materialized yet (lazy serialization)
        self.assertNotIn('data', event.data)

        fresh_site = Site.objects.get(pk=site.pk)
        fresh_site.description = 'foo'
        fresh_site.save()

        enqueue_event(queue, fresh_site, request, OBJECT_UPDATED)

        # The original object reference should be preserved
        self.assertIs(event['object'], stale_site)

        # But serialized data should reflect the fresher instance
        self.assertEqual(event['data']['description'], 'foo')
        self.assertEqual(event['snapshots']['postchange']['description'], 'foo')

    def test_duplicate_enqueue_invalidates_materialized_data(self):
        """
        If event['data'] has already been materialized before a second enqueue
        for the same object, the stale payload should be discarded and rebuilt
        from the fresher instance on next access.
        """
        request = RequestFactory().get(reverse('dcim:site_add'))
        request.id = uuid.uuid4()
        request.user = self.user

        site = Site.objects.create(name='Site 1', slug='site-1')

        queue = {}
        enqueue_event(queue, site, request, OBJECT_UPDATED)

        event = queue[f'dcim.site:{site.pk}']

        # Force early materialization
        self.assertEqual(event['data']['description'], '')

        # Now update and re-enqueue
        fresh_site = Site.objects.get(pk=site.pk)
        fresh_site.description = 'updated'
        fresh_site.save()

        enqueue_event(queue, fresh_site, request, OBJECT_UPDATED)

        # Stale data should have been invalidated; new access should reflect update
        self.assertEqual(event['data']['description'], 'updated')

    def test_update_then_delete_enqueue_freezes_payload(self):
        """
        When an update event is coalesced with a subsequent delete, the event
        type should be promoted to OBJECT_DELETED and the payload should be
        eagerly frozen (since the object will be inaccessible after deletion).
        """
        request = RequestFactory().get(reverse('dcim:site_add'))
        request.id = uuid.uuid4()
        request.user = self.user

        site = Site.objects.create(name='Site 1', slug='site-1')

        queue = {}
        enqueue_event(queue, site, request, OBJECT_UPDATED)

        event = queue[f'dcim.site:{site.pk}']

        enqueue_event(queue, site, request, OBJECT_DELETED)

        # Event type should have been promoted
        self.assertEqual(event['event_type'], OBJECT_DELETED)

        # Data should already be materialized (frozen), not lazy
        self.assertIn('data', event.data)
        self.assertEqual(event['data']['name'], 'Site 1')
        self.assertIsNone(event['snapshots']['postchange'])

    @tag('regression')  # #21338
    def test_cable_creation_event_payload_includes_connected_endpoints(self):
        """
        Interface update events queued during cable creation must include the
        peer interface in connected_endpoints and link_peers.
        """
        webhook = Webhook.objects.get(name='Webhook 1')
        event_rule = EventRule.objects.create(
            name='Interface Update Rule',
            event_types=[OBJECT_UPDATED],
            action_type=EventRuleActionChoices.WEBHOOK,
            action_object_type=ObjectType.objects.get_for_model(Webhook),
            action_object_id=webhook.id,
        )
        event_rule.object_types.set([ObjectType.objects.get_for_model(Interface)])

        device = create_test_device('Device 1')
        interface_a = Interface.objects.create(device=device, name='eth0')
        interface_b = Interface.objects.create(device=device, name='eth1')

        # Create a cable between the two interfaces via the REST API
        data = {
            'a_terminations': [{'object_type': 'dcim.interface', 'object_id': interface_a.pk}],
            'b_terminations': [{'object_type': 'dcim.interface', 'object_id': interface_b.pk}],
        }
        url = reverse('dcim-api:cable-list')
        self.add_permissions('dcim.add_cable')
        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        # One update event was queued for each interface
        self.assertEqual(self.queue.count, 2)
        payloads = {job.kwargs['data']['id']: job.kwargs['data'] for job in self.queue.jobs}
        peers = {interface_a.pk: interface_b.pk, interface_b.pk: interface_a.pk}
        self.assertEqual(set(payloads), set(peers))
        for interface_id, payload in payloads.items():
            peer_id = peers[interface_id]
            self.assertIsNotNone(payload['connected_endpoints'])
            self.assertEqual([endpoint['id'] for endpoint in payload['connected_endpoints']], [peer_id])
            self.assertEqual([peer['id'] for peer in payload['link_peers']], [peer_id])
            self.assertTrue(payload['connected_endpoints_reachable'])

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

    def test_non_dict_action_data_does_not_crash_flush(self):
        """
        Pre-existing non-dict action_data must not cause flush_events() to
        raise.
        """
        site_type = ObjectType.objects.get_for_model(Site)
        webhook = Webhook.objects.get(name='Webhook 1')
        webhook_type = ObjectType.objects.get_for_model(Webhook)

        bad_rule = EventRule.objects.create(
            name='Bad action_data rule',
            event_types=[OBJECT_CREATED],
            action_type=EventRuleActionChoices.WEBHOOK,
            action_object_type=webhook_type,
            action_object_id=webhook.pk,
            action_data={},
        )
        bad_rule.object_types.set([site_type])

        # Simulate a legacy row that predates model validation.
        EventRule.objects.filter(pk=bad_rule.pk).update(action_data='not a dict')

        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.add_site')
        response = self.client.post(url, {'name': 'Site X', 'slug': 'site-x'}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

    @tag('regression')
    def test_eventrule_script_action_with_object_image_files(self):
        """
        Verify that a Script event-rule action can be enqueued and executed cleanly when the
        triggering object carries uploaded files (e.g. DeviceType images).
        This is a regression test for issue #22376.

        """
        # Create a dummy script class and an instance of it
        class DummyScript(ScriptBase):
            class Meta:
                name = "Dummy Script"

            def run(self, data, commit=True):
                return "finished successfully"

        dummy_script = DummyScript()

        # Create ScriptModule and Script
        with patch.object(ScriptModule, 'sync_classes'):
            module = ScriptModule.objects.create(
                file_root=ManagedFileRootPathChoices.SCRIPTS,
                file_path='dummy_script.py',
            )
        script = Script.objects.create(
            module=module,
            name='Dummy Script',
            is_executable=True,
        )
        script_type = ObjectType.objects.get_for_model(Script)

        # Create an event rule that triggers on DeviceType update with Script action
        devicetype_type = ObjectType.objects.get_for_model(DeviceType)
        event_rule = EventRule.objects.create(
            name='Test Script Event Rule with Files',
            event_types=[OBJECT_UPDATED],
            action_type=EventRuleActionChoices.SCRIPT,
            action_object_type=script_type,
            action_object_id=script.pk,
        )
        event_rule.object_types.set([devicetype_type])

        # Create a manufacturer and DeviceType
        manufacturer = Manufacturer.objects.create(
            name='Test Manufacturer',
            slug='test-manufacturer',
        )
        devicetype = DeviceType.objects.create(
            model='Test DeviceType',
            slug="test-devicetype",
            manufacturer=manufacturer,
        )

        # Create an image file
        image = BytesIO()
        Image.new('RGB', (1, 1)).save(image, format='PNG')
        image.name = 'test_image.png'
        image.seek(0)

        # PATCH the DeviceType via REST API to add the image
        data = {
            'front_image': image,
        }
        url = reverse('dcim-api:devicetype-detail', kwargs={'pk': devicetype.pk})
        self.add_permissions('dcim.change_devicetype')

        # Mock the script's python_class to prevent the test from trying to load from disk
        with patch.object(Script, 'python_class') as mock:
            mock.return_value = dummy_script
            # Since in core/models/jobs.py Jobs are enqueued with a transaction.on_commit-handler
            # we simulate commit by using captureOnCommitCallbacks context manager
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.patch(url, data, format='multipart', **self.header)
            self.assertHttpStatus(response, status.HTTP_200_OK)

            # Assert that the script job was enqueued cleanly and is waiting for execution
            self.assertEqual(self.queue.count, 1)
            script_job = Job.objects.filter(name=dummy_script.name).last()
            self.assertEqual(script_job.status, "pending")

            # silence rqworker (cleaner output) and trigger job execution
            logging.getLogger('rq.worker').setLevel(logging.ERROR)
            self.run_rq_jobs('default')

        # Assert that our script was executed without any errors
        script_job.refresh_from_db()
        self.assertEqual(script_job.status, "completed")
        self.assertEqual(script_job.data.get('output', ''), "finished successfully")

    @tag('regression')
    def test_eventrule_webhook_action_with_object_image_files(self):
        """
        Verify that a Webhook event-rule action can be enqueued and executed cleanly when
        the triggering object carries uploaded files (e.g. DeviceType images).
        This is a regression test for issue #20873.
        """
        # Create an event rule that triggers on DeviceType update with Script action
        webhook = Webhook.objects.get(name='Webhook 1')
        webhook_type = ObjectType.objects.get_for_model(Webhook)
        devicetype_type = ObjectType.objects.get_for_model(DeviceType)
        event_rule = EventRule.objects.create(
            name='Test Webhook Event Rule with Files',
            event_types=[OBJECT_UPDATED],
            action_type=EventRuleActionChoices.WEBHOOK,
            action_object_type=webhook_type,
            action_object_id=webhook.pk,
        )
        event_rule.object_types.set([devicetype_type])

        # Create a manufacturer and DeviceType
        manufacturer = Manufacturer.objects.create(
            name='Test Manufacturer',
            slug='test-manufacturer',
        )
        devicetype = DeviceType.objects.create(
            model='Test DeviceType',
            slug="test-devicetype",
            manufacturer=manufacturer,
        )

        # Create an image file
        image = BytesIO()
        Image.new('RGB', (1, 1)).save(image, format='PNG')
        image.name = 'test_image.png'
        image.seek(0)

        # PATCH the DeviceType via REST API to add the image
        data = {
            'front_image': image,
        }
        url = reverse('dcim-api:devicetype-detail', kwargs={'pk': devicetype.pk})
        self.add_permissions('dcim.change_devicetype')

        response = self.client.patch(url, data, format='multipart', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        # Assert that the webhook job was enqueued cleanly
        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(job.kwargs['event_rule'], event_rule)
        self.assertEqual(job.kwargs['event_type'], OBJECT_UPDATED)
