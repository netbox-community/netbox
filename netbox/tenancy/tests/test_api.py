from __future__ import unicode_literals

from django.urls import reverse
from rest_framework import status

from tenancy.models import Tenant, TenantGroup
from utilities.testing import APITestCase


class TenantGroupTest(APITestCase):

    def setUp(self):

        super(TenantGroupTest, self).setUp()

        self.tenantgroup1 = TenantGroup.objects.create(name='Test Tenant Group 1', slug='test-tenant-group-1')
        self.tenantgroup2 = TenantGroup.objects.create(name='Test Tenant Group 2', slug='test-tenant-group-2')
        self.tenantgroup3 = TenantGroup.objects.create(name='Test Tenant Group 3', slug='test-tenant-group-3')

    def test_get_tenantgroup(self):

        url = reverse('tenancy-api:tenantgroup-detail', kwargs={'pk': self.tenantgroup1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.tenantgroup1.name)

    def test_list_tenantgroups(self):

        url = reverse('tenancy-api:tenantgroup-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_tenantgroups_brief(self):

        url = reverse('tenancy-api:tenantgroup-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'slug', 'url']
        )

    def test_create_tenantgroup(self):

        data = {
            'name': 'Test Tenant Group 4',
            'slug': 'test-tenant-group-4',
        }

        url = reverse('tenancy-api:tenantgroup-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(TenantGroup.objects.count(), 4)
        tenantgroup4 = TenantGroup.objects.get(pk=response.data['id'])
        self.assertEqual(tenantgroup4.name, data['name'])
        self.assertEqual(tenantgroup4.slug, data['slug'])

    def test_create_tenantgroup_bulk(self):

        data = [
            {
                'name': 'Test Tenant Group 4',
                'slug': 'test-tenant-group-4',
            },
            {
                'name': 'Test Tenant Group 5',
                'slug': 'test-tenant-group-5',
            },
            {
                'name': 'Test Tenant Group 6',
                'slug': 'test-tenant-group-6',
            },
        ]

        url = reverse('tenancy-api:tenantgroup-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(TenantGroup.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_tenantgroup(self):

        data = {
            'name': 'Test Tenant Group X',
            'slug': 'test-tenant-group-x',
        }

        url = reverse('tenancy-api:tenantgroup-detail', kwargs={'pk': self.tenantgroup1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(TenantGroup.objects.count(), 3)
        tenantgroup1 = TenantGroup.objects.get(pk=response.data['id'])
        self.assertEqual(tenantgroup1.name, data['name'])
        self.assertEqual(tenantgroup1.slug, data['slug'])

    def test_delete_tenantgroup(self):

        url = reverse('tenancy-api:tenantgroup-detail', kwargs={'pk': self.tenantgroup1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TenantGroup.objects.count(), 2)


class TenantTest(APITestCase):

    def setUp(self):

        super(TenantTest, self).setUp()

        self.tenantgroup1 = TenantGroup.objects.create(name='Test Tenant Group 1', slug='test-tenant-group-1')
        self.tenantgroup2 = TenantGroup.objects.create(name='Test Tenant Group 2', slug='test-tenant-group-2')
        self.tenant1 = Tenant.objects.create(name='Test Tenant 1', slug='test-tenant-1', group=self.tenantgroup1)
        self.tenant2 = Tenant.objects.create(name='Test Tenant 2', slug='test-tenant-2', group=self.tenantgroup1)
        self.tenant3 = Tenant.objects.create(name='Test Tenant 3', slug='test-tenant-3', group=self.tenantgroup1)

    def test_get_tenant(self):

        url = reverse('tenancy-api:tenant-detail', kwargs={'pk': self.tenant1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.tenant1.name)

    def test_list_tenants(self):

        url = reverse('tenancy-api:tenant-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_tenants_brief(self):

        url = reverse('tenancy-api:tenant-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'slug', 'url']
        )

    def test_create_tenant(self):

        data = {
            'name': 'Test Tenant 4',
            'slug': 'test-tenant-4',
            'group': self.tenantgroup1.pk,
        }

        url = reverse('tenancy-api:tenant-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Tenant.objects.count(), 4)
        tenant4 = Tenant.objects.get(pk=response.data['id'])
        self.assertEqual(tenant4.name, data['name'])
        self.assertEqual(tenant4.slug, data['slug'])
        self.assertEqual(tenant4.group_id, data['group'])

    def test_create_tenant_bulk(self):

        data = [
            {
                'name': 'Test Tenant 4',
                'slug': 'test-tenant-4',
            },
            {
                'name': 'Test Tenant 5',
                'slug': 'test-tenant-5',
            },
            {
                'name': 'Test Tenant 6',
                'slug': 'test-tenant-6',
            },
        ]

        url = reverse('tenancy-api:tenant-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Tenant.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_tenant(self):

        data = {
            'name': 'Test Tenant X',
            'slug': 'test-tenant-x',
            'group': self.tenantgroup2.pk,
        }

        url = reverse('tenancy-api:tenant-detail', kwargs={'pk': self.tenant1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(Tenant.objects.count(), 3)
        tenant1 = Tenant.objects.get(pk=response.data['id'])
        self.assertEqual(tenant1.name, data['name'])
        self.assertEqual(tenant1.slug, data['slug'])
        self.assertEqual(tenant1.group_id, data['group'])

    def test_delete_tenant(self):

        url = reverse('tenancy-api:tenant-detail', kwargs={'pk': self.tenant1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Tenant.objects.count(), 2)
