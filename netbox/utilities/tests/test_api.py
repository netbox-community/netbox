from django.test import Client, TestCase, override_settings
from django.urls import reverse
from rest_framework import status

from core.models import ObjectType
from dcim.models import Region, Site
from extras.choices import CustomFieldTypeChoices
from extras.models import CustomField
from ipam.models import VLAN
from netbox.config import get_config
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


class APIPaginationTestCase(APITestCase):
    user_permissions = ('dcim.view_site',)

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('dcim-api:site-list')

        # Create a large number of Sites for testing
        Site.objects.bulk_create([
            Site(name=f'Site {i}', slug=f'site-{i}') for i in range(1, 101)
        ])

    def test_default_page_size(self):
        response = self.client.get(self.url, format='json', **self.header)
        page_size = get_config().PAGINATE_COUNT
        self.assertLess(page_size, 100, "Default page size not sufficient for data set")

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 100)
        self.assertTrue(response.data['next'].endswith(f'?limit={page_size}&offset={page_size}'))
        self.assertIsNone(response.data['previous'])
        self.assertEqual(len(response.data['results']), page_size)

    def test_custom_page_size(self):
        response = self.client.get(f'{self.url}?limit=10', format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 100)
        self.assertTrue(response.data['next'].endswith(f'?limit=10&offset=10'))
        self.assertIsNone(response.data['previous'])
        self.assertEqual(len(response.data['results']), 10)

    @override_settings(MAX_PAGE_SIZE=20)
    def test_max_page_size(self):
        response = self.client.get(f'{self.url}?limit=0', format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 100)
        self.assertTrue(response.data['next'].endswith(f'?limit=20&offset=20'))
        self.assertIsNone(response.data['previous'])
        self.assertEqual(len(response.data['results']), 20)

    @override_settings(MAX_PAGE_SIZE=0)
    def test_max_page_size_disabled(self):
        response = self.client.get(f'{self.url}?limit=0', format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 100)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(len(response.data['results']), 100)


class APIOrderingTestCase(APITestCase):
    user_permissions = ('dcim.view_site',)

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('dcim-api:site-list')

        sites = (
            Site(name='Site 1', slug='site-1', facility='C', description='Z'),
            Site(name='Site 2', slug='site-2', facility='C', description='Y'),
            Site(name='Site 3', slug='site-3', facility='B', description='X'),
            Site(name='Site 4', slug='site-4', facility='B', description='W'),
            Site(name='Site 5', slug='site-5', facility='A', description='V'),
            Site(name='Site 6', slug='site-6', facility='A', description='U'),
        )
        Site.objects.bulk_create(sites)

    def test_default_order(self):
        response = self.client.get(self.url, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 6)
        self.assertListEqual(
            [s['name'] for s in response.data['results']],
            ['Site 1', 'Site 2', 'Site 3', 'Site 4', 'Site 5', 'Site 6']
        )

    def test_order_single_field(self):
        response = self.client.get(f'{self.url}?ordering=description', format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 6)
        self.assertListEqual(
            [s['name'] for s in response.data['results']],
            ['Site 6', 'Site 5', 'Site 4', 'Site 3', 'Site 2', 'Site 1']
        )

    def test_order_reversed(self):
        response = self.client.get(f'{self.url}?ordering=-name', format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 6)
        self.assertListEqual(
            [s['name'] for s in response.data['results']],
            ['Site 6', 'Site 5', 'Site 4', 'Site 3', 'Site 2', 'Site 1']
        )

    def test_order_multiple_fields(self):
        response = self.client.get(f'{self.url}?ordering=facility,name', format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 6)
        self.assertListEqual(
            [s['name'] for s in response.data['results']],
            ['Site 5', 'Site 6', 'Site 3', 'Site 4', 'Site 1', 'Site 2']
        )


class APIDocsTestCase(TestCase):

    def setUp(self):
        self.client = Client()

        # Populate a CustomField to activate CustomFieldSerializer
        object_type = ObjectType.objects.get_for_model(Site)
        self.cf_text = CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='test')
        self.cf_text.save()
        self.cf_text.object_types.set([object_type])
        self.cf_text.save()

    def test_api_docs(self):

        url = reverse('api_docs')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse('schema')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
