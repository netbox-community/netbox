import django_rq
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import status

from dcim.models import Site
from extras.choices import ObjectChangeActionChoices
from extras.models import Webhook
from utilities.testing import APITestCase


class WebhookTest(APITestCase):

    def setUp(self):

        super().setUp()

        self.queue = django_rq.get_queue('default')
        self.queue.empty()  # Begin each test with an empty queue

    @classmethod
    def setUpTestData(cls):

        site_ct = ContentType.objects.get_for_model(Site)
        PAYLOAD_URL = "http://localhost/"
        webhooks = Webhook.objects.bulk_create((
            Webhook(name='Site Create Webhook', type_create=True, payload_url=PAYLOAD_URL),
            Webhook(name='Site Update Webhook', type_update=True, payload_url=PAYLOAD_URL),
            Webhook(name='Site Delete Webhook', type_delete=True, payload_url=PAYLOAD_URL),
        ))
        for webhook in webhooks:
            webhook.obj_type.set([site_ct])

    def test_enqueue_webhook_create(self):

        # Create an object via the REST API
        data = {
            'name': 'Test Site',
            'slug': 'test-site',
        }
        url = reverse('dcim-api:site-list')
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

        site = Site.objects.create(name='Site 1', slug='site-1')

        # Update an object via the REST API
        data = {
            'comments': 'Updated the site',
        }
        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})
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

        site = Site.objects.create(name='Site 1', slug='site-1')

        # Delete an object via the REST API
        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})
        response = self.client.delete(url, **self.header)
        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)

        # Verify that a job was queued for the object update webhook
        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(job.args[0], Webhook.objects.get(type_delete=True))
        self.assertEqual(job.args[1]['id'], site.pk)
        self.assertEqual(job.args[2], 'site')
        self.assertEqual(job.args[3], ObjectChangeActionChoices.ACTION_DELETE)
