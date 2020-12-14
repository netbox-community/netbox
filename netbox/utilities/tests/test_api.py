import urllib.parse

from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from dcim.models import Region, Site
from extras.choices import CustomFieldTypeChoices
from extras.models import CustomField
from ipam.models import VLAN
from utilities.testing import APITestCase, disable_warnings


class WritableNestedSerializerTest(APITestCase):
    """
    Test the operation of WritableNestedSerializer using VLANSerializer as our test subject.
    """

    def setUp(self):
        super().setUp()

        self.region_a = Region.objects.create(name='Region A', slug='region-a')
        self.site1 = Site.objects.create(region=self.region_a, name='Site 1', slug='site-1')
        self.site2 = Site.objects.create(region=self.region_a, name='Site 2', slug='site-2')

    def test_related_by_pk(self):
        data = {
            'vid': 100,
            'name': 'Test VLAN 100',
            'site': self.site1.pk,
        }
        url = reverse('ipam-api:vlan-list')
        self.add_permissions('ipam.add_vlan')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data['site']['id'], self.site1.pk)
        vlan = VLAN.objects.get(pk=response.data['id'])
        self.assertEqual(vlan.site, self.site1)

    def test_related_by_pk_no_match(self):
        data = {
            'vid': 100,
            'name': 'Test VLAN 100',
            'site': 999,
        }
        url = reverse('ipam-api:vlan-list')
        self.add_permissions('ipam.add_vlan')

        with disable_warnings('django.request'):
            response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(VLAN.objects.count(), 0)
        self.assertTrue(response.data['site'][0].startswith("Related object not found"))

    def test_related_by_attributes(self):
        data = {
            'vid': 100,
            'name': 'Test VLAN 100',
            'site': {
                'name': 'Site 1'
            },
        }
        url = reverse('ipam-api:vlan-list')
        self.add_permissions('ipam.add_vlan')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data['site']['id'], self.site1.pk)
        vlan = VLAN.objects.get(pk=response.data['id'])
        self.assertEqual(vlan.site, self.site1)

    def test_related_by_attributes_no_match(self):
        data = {
            'vid': 100,
            'name': 'Test VLAN 100',
            'site': {
                'name': 'Site X'
            },
        }
        url = reverse('ipam-api:vlan-list')
        self.add_permissions('ipam.add_vlan')

        with disable_warnings('django.request'):
            response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(VLAN.objects.count(), 0)
        self.assertTrue(response.data['site'][0].startswith("Related object not found"))

    def test_related_by_attributes_multiple_matches(self):
        data = {
            'vid': 100,
            'name': 'Test VLAN 100',
            'site': {
                'region': {
                    "name": "Region A",
                },
            },
        }
        url = reverse('ipam-api:vlan-list')
        self.add_permissions('ipam.add_vlan')

        with disable_warnings('django.request'):
            response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(VLAN.objects.count(), 0)
        self.assertTrue(response.data['site'][0].startswith("Multiple objects match"))

    def test_related_by_invalid(self):
        data = {
            'vid': 100,
            'name': 'Test VLAN 100',
            'site': 'XXX',
        }
        url = reverse('ipam-api:vlan-list')
        self.add_permissions('ipam.add_vlan')

        with disable_warnings('django.request'):
            response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(VLAN.objects.count(), 0)


class APIDocsTestCase(TestCase):

    def setUp(self):
        self.client = Client()

        # Populate a CustomField to activate CustomFieldSerializer
        content_type = ContentType.objects.get_for_model(Site)
        self.cf_text = CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='test')
        self.cf_text.save()
        self.cf_text.content_types.set([content_type])
        self.cf_text.save()

    def test_api_docs(self):

        url = reverse('api_docs')
        params = {
            "format": "openapi",
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)
