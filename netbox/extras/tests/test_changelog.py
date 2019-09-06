from django.urls import reverse
from rest_framework import status

from dcim.models import Site
from extras.constants import OBJECTCHANGE_ACTION_CREATE, OBJECTCHANGE_ACTION_UPDATE, OBJECTCHANGE_ACTION_DELETE
from extras.models import ObjectChange
from utilities.testing import APITestCase


class ChangeLogTest(APITestCase):

    def test_create_object(self):

        data = {
            'name': 'Test Site 1',
            'slug': 'test-site-1',
        }

        self.assertEqual(ObjectChange.objects.count(), 0)

        url = reverse('dcim-api:site-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ObjectChange.objects.count(), 1)

        oc = ObjectChange.objects.first()
        site = Site.objects.get(pk=response.data['id'])
        self.assertEqual(oc.changed_object, site)
        self.assertEqual(oc.action, OBJECTCHANGE_ACTION_CREATE)

    def test_update_object(self):

        site = Site(name='Test Site 1', slug='test-site-1')
        site.save()

        data = {
            'name': 'Test Site X',
            'slug': 'test-site-x',
        }

        self.assertEqual(ObjectChange.objects.count(), 0)

        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(ObjectChange.objects.count(), 1)
        site = Site.objects.get(pk=response.data['id'])
        self.assertEqual(site.name, data['name'])

        oc = ObjectChange.objects.first()
        self.assertEqual(oc.changed_object, site)
        self.assertEqual(oc.action, OBJECTCHANGE_ACTION_UPDATE)

    def test_delete_object(self):

        site = Site(name='Test Site 1', slug='test-site-1')
        site.save()

        self.assertEqual(ObjectChange.objects.count(), 0)

        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Site.objects.count(), 0)

        oc = ObjectChange.objects.first()
        self.assertEqual(oc.changed_object, None)
        self.assertEqual(oc.object_repr, site.name)
        self.assertEqual(oc.action, OBJECTCHANGE_ACTION_DELETE)
