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
from extras.models import Webhook
from extras.webhooks import enqueue_webhooks, generate_signature
from extras.webhooks_worker import process_webhook
from utilities.testing import APITestCase


class WebhookTest(APITestCase):

    def setUp(self):

        super().setUp()

        self.queue = django_rq.get_queue('default')
        self.queue.empty()  # Begin each test with an empty queue

    @classmethod
    def setUpTestData(cls):

        site_ct = ContentType.objects.get_for_model(Site)
        DUMMY_URL = "http://localhost/"
        DUMMY_SECRET = "LOOKATMEIMASECRETSTRING"

        webhooks = Webhook.objects.bulk_create((
            Webhook(name='Site Create Webhook', type_create=True, payload_url=DUMMY_URL, secret=DUMMY_SECRET, additional_headers='X-Foo: Bar'),
            Webhook(name='Site Update Webhook', type_update=True, payload_url=DUMMY_URL, secret=DUMMY_SECRET),
            Webhook(name='Site Delete Webhook', type_delete=True, payload_url=DUMMY_URL, secret=DUMMY_SECRET),
        ))
        for webhook in webhooks:
            webhook.content_types.set([site_ct])

    def test_enqueue_webhook_create(self):
        # Create an object via the REST API
        data = {
            'name': 'Test Site',
            'slug': 'test-site',
        }
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.add_site')
        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Site.objects.count(), 1)

        # Verify that a job was queued for the object creation webhook
        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(job.args[0], Webhook.objects.get(type_create=True))
        self.assertEqual(job.args[1]['id'], response.data['id'])
        self.assertEqual(job.args[2], 'site')
        self.assertEqual(job.args[3], ObjectChangeActionChoices.ACTION_CREATE)

    def test_enqueue_webhook_update(self):
        # Update an object via the REST API
        site = Site.objects.create(name='Site 1', slug='site-1')
        data = {
            'comments': 'Updated the site',
        }
        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})
        self.add_permissions('dcim.change_site')
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        # Verify that a job was queued for the object update webhook
        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(job.args[0], Webhook.objects.get(type_update=True))
        self.assertEqual(job.args[1]['id'], site.pk)
        self.assertEqual(job.args[2], 'site')
        self.assertEqual(job.args[3], ObjectChangeActionChoices.ACTION_UPDATE)

    def test_enqueue_webhook_delete(self):
        # Delete an object via the REST API
        site = Site.objects.create(name='Site 1', slug='site-1')
        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})
        self.add_permissions('dcim.delete_site')
        response = self.client.delete(url, **self.header)
        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)

        # Verify that a job was queued for the object update webhook
        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(job.args[0], Webhook.objects.get(type_delete=True))
        self.assertEqual(job.args[1]['id'], site.pk)
        self.assertEqual(job.args[2], 'site')
        self.assertEqual(job.args[3], ObjectChangeActionChoices.ACTION_DELETE)

    def test_webhooks_worker(self):

        request_id = uuid.uuid4()

        def dummy_send(_, request, **kwargs):
            """
            A dummy implementation of Session.send() to be used for testing.
            Always returns a 200 HTTP response.
            """
            webhook = Webhook.objects.get(type_create=True)
            signature = generate_signature(request.body, webhook.secret)

            # Validate the outgoing request headers
            self.assertEqual(request.headers['Content-Type'], webhook.http_content_type)
            self.assertEqual(request.headers['X-Hook-Signature'], signature)
            self.assertEqual(request.headers['X-Foo'], 'Bar')

            # Validate the outgoing request body
            body = json.loads(request.body)
            self.assertEqual(body['event'], 'created')
            self.assertEqual(body['timestamp'], job.args[4])
            self.assertEqual(body['model'], 'site')
            self.assertEqual(body['username'], 'testuser')
            self.assertEqual(body['request_id'], str(request_id))
            self.assertEqual(body['data']['name'], 'Site 1')

            return HttpResponse()

        # Enqueue a webhook for processing
        site = Site.objects.create(name='Site 1', slug='site-1')
        enqueue_webhooks(
            instance=site,
            user=self.user,
            request_id=request_id,
            action=ObjectChangeActionChoices.ACTION_CREATE
        )

        # Retrieve the job from queue
        job = self.queue.jobs[0]

        # Patch the Session object with our dummy_send() method, then process the webhook for sending
        with patch.object(Session, 'send', dummy_send) as mock_send:
            process_webhook(*job.args)
