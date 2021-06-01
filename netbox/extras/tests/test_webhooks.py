import json
import uuid
from unittest.mock import patch

import django_rq
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.urls import reverse
from requests import Session
from rest_framework import status

from dcim.models import Site
from extras.choices import ObjectChangeActionChoices
from extras.models import Tag, Webhook
from extras.webhooks import enqueue_object, generate_signature
from extras.webhooks_worker import process_webhook
from utilities.testing import APITestCase


class WebhookTest(APITestCase):

    def setUp(self):
        super().setUp()

        self.queue = django_rq.get_queue('default')
        self.queue.empty()

    @classmethod
    def setUpTestData(cls):

        site_ct = ContentType.objects.get_for_model(Site)
        DUMMY_URL = "http://localhost/"
        DUMMY_SECRET = "LOOKATMEIMASECRETSTRING"

        webhooks = Webhook.objects.bulk_create((
            Webhook(name='Webhook 1', type_create=True, payload_url=DUMMY_URL, secret=DUMMY_SECRET, additional_headers='X-Foo: Bar'),
            Webhook(name='Webhook 2', type_update=True, payload_url=DUMMY_URL, secret=DUMMY_SECRET),
            Webhook(name='Webhook 3', type_delete=True, payload_url=DUMMY_URL, secret=DUMMY_SECRET),
        ))
        for webhook in webhooks:
            webhook.content_types.set([site_ct])

        Tag.objects.bulk_create((
            Tag(name='Foo', slug='foo'),
            Tag(name='Bar', slug='bar'),
            Tag(name='Baz', slug='baz'),
        ))

    def test_enqueue_webhook_create(self):
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

        # Verify that a job was queued for the object creation webhook
        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(job.kwargs['webhook'], Webhook.objects.get(type_create=True))
        self.assertEqual(job.kwargs['data']['id'], response.data['id'])
        self.assertEqual(len(job.kwargs['data']['tags']), len(response.data['tags']))
        self.assertEqual(job.kwargs['model_name'], 'site')
        self.assertEqual(job.kwargs['event'], ObjectChangeActionChoices.ACTION_CREATE)

    def test_enqueue_webhook_update(self):
        site = Site.objects.create(name='Site 1', slug='site-1')
        site.tags.set(*Tag.objects.filter(name__in=['Foo', 'Bar']))

        # Update an object via the REST API
        data = {
            'comments': 'Updated the site',
            'tags': [
                {'name': 'Baz'}
            ]
        }
        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})
        self.add_permissions('dcim.change_site')
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        # Verify that a job was queued for the object update webhook
        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(job.kwargs['webhook'], Webhook.objects.get(type_update=True))
        self.assertEqual(job.kwargs['data']['id'], site.pk)
        self.assertEqual(len(job.kwargs['data']['tags']), len(response.data['tags']))
        self.assertEqual(job.kwargs['model_name'], 'site')
        self.assertEqual(job.kwargs['event'], ObjectChangeActionChoices.ACTION_UPDATE)

    def test_enqueue_webhook_delete(self):
        site = Site.objects.create(name='Site 1', slug='site-1')
        site.tags.set(*Tag.objects.filter(name__in=['Foo', 'Bar']))

        # Delete an object via the REST API
        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})
        self.add_permissions('dcim.delete_site')
        response = self.client.delete(url, **self.header)
        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)

        # Verify that a job was queued for the object update webhook
        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(job.kwargs['webhook'], Webhook.objects.get(type_delete=True))
        self.assertEqual(job.kwargs['data']['id'], site.pk)
        self.assertEqual(job.kwargs['model_name'], 'site')
        self.assertEqual(job.kwargs['event'], ObjectChangeActionChoices.ACTION_DELETE)

    # TODO: Replace webhook worker test
    # def test_webhooks_worker(self):
    #
    #     request_id = uuid.uuid4()
    #
    #     def dummy_send(_, request, **kwargs):
    #         """
    #         A dummy implementation of Session.send() to be used for testing.
    #         Always returns a 200 HTTP response.
    #         """
    #         webhook = Webhook.objects.get(type_create=True)
    #         signature = generate_signature(request.body, webhook.secret)
    #
    #         # Validate the outgoing request headers
    #         self.assertEqual(request.headers['Content-Type'], webhook.http_content_type)
    #         self.assertEqual(request.headers['X-Hook-Signature'], signature)
    #         self.assertEqual(request.headers['X-Foo'], 'Bar')
    #
    #         # Validate the outgoing request body
    #         body = json.loads(request.body)
    #         self.assertEqual(body['event'], 'created')
    #         self.assertEqual(body['timestamp'], job.kwargs['timestamp'])
    #         self.assertEqual(body['model'], 'site')
    #         self.assertEqual(body['username'], 'testuser')
    #         self.assertEqual(body['request_id'], str(request_id))
    #         self.assertEqual(body['data']['name'], 'Site 1')
    #
    #         return HttpResponse()
    #
    #     # Enqueue a webhook for processing
    #     site = Site.objects.create(name='Site 1', slug='site-1')
    #     enqueue_webhooks(
    #         queue=[],
    #         instance=site,
    #         user=self.user,
    #         request_id=request_id,
    #         action=ObjectChangeActionChoices.ACTION_CREATE
    #     )
    #
    #     # Retrieve the job from queue
    #     job = self.queue.jobs[0]
    #
    #     # Patch the Session object with our dummy_send() method, then process the webhook for sending
    #     with patch.object(Session, 'send', dummy_send) as mock_send:
    #         process_webhook(**job.kwargs)
