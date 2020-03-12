from django.urls import reverse
from rest_framework import status

from tenancy.models import Tenant, TenantGroup
from utilities.testing import APITestCase


class AppTest(APITestCase):

    def test_root(self):

        url = reverse('tenancy-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)

    def test_choices(self):

        url = reverse('tenancy-api:field-choice-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.status_code, 200)


class TenantGroupTest(APITestCase):

    def setUp(self):

        super().setUp()

        self.parent_tenant_groups = (
            TenantGroup(name='Parent Tenant Group 1', slug='parent-tenant-group-1'),
            TenantGroup(name='Parent Tenant Group 2', slug='parent-tenant-group-2'),
        )
        for tenantgroup in self.parent_tenant_groups:
            tenantgroup.save()

        self.tenant_groups = (
            TenantGroup(name='Tenant Group 1', slug='tenant-group-1', parent=self.parent_tenant_groups[0]),
            TenantGroup(name='Tenant Group 2', slug='tenant-group-2', parent=self.parent_tenant_groups[0]),
            TenantGroup(name='Tenant Group 3', slug='tenant-group-3', parent=self.parent_tenant_groups[0]),
        )
        for tenantgroup in self.tenant_groups:
            tenantgroup.save()

    def test_get_tenantgroup(self):

        url = reverse('tenancy-api:tenantgroup-detail', kwargs={'pk': self.tenant_groups[0].pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.tenant_groups[0].name)

    def test_list_tenantgroups(self):

        url = reverse('tenancy-api:tenantgroup-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 5)

    def test_list_tenantgroups_brief(self):

        url = reverse('tenancy-api:tenantgroup-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'slug', 'tenant_count', 'url']
        )

    def test_create_tenantgroup(self):

        data = {
            'name': 'Tenant Group 4',
            'slug': 'tenant-group-4',
            'parent': self.parent_tenant_groups[0].pk,
        }

        url = reverse('tenancy-api:tenantgroup-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(TenantGroup.objects.count(), 6)
        tenantgroup4 = TenantGroup.objects.get(pk=response.data['id'])
        self.assertEqual(tenantgroup4.name, data['name'])
        self.assertEqual(tenantgroup4.slug, data['slug'])
        self.assertEqual(tenantgroup4.parent_id, data['parent'])

    def test_create_tenantgroup_bulk(self):

        data = [
            {
                'name': 'Tenant Group 4',
                'slug': 'tenant-group-4',
                'parent': self.parent_tenant_groups[0].pk,
            },
            {
                'name': 'Tenant Group 5',
                'slug': 'tenant-group-5',
                'parent': self.parent_tenant_groups[0].pk,
            },
            {
                'name': 'Tenant Group 6',
                'slug': 'tenant-group-6',
                'parent': self.parent_tenant_groups[0].pk,
            },
        ]

        url = reverse('tenancy-api:tenantgroup-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(TenantGroup.objects.count(), 8)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_tenantgroup(self):

        data = {
            'name': 'Tenant Group X',
            'slug': 'tenant-group-x',
            'parent': self.parent_tenant_groups[1].pk,
        }

        url = reverse('tenancy-api:tenantgroup-detail', kwargs={'pk': self.tenant_groups[0].pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(TenantGroup.objects.count(), 5)
        tenantgroup1 = TenantGroup.objects.get(pk=response.data['id'])
        self.assertEqual(tenantgroup1.name, data['name'])
        self.assertEqual(tenantgroup1.slug, data['slug'])
        self.assertEqual(tenantgroup1.parent_id, data['parent'])

    def test_delete_tenantgroup(self):

        url = reverse('tenancy-api:tenantgroup-detail', kwargs={'pk': self.tenant_groups[0].pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TenantGroup.objects.count(), 4)


class TenantTest(APITestCase):

    def setUp(self):

        super().setUp()

        self.tenant_groups = (
            TenantGroup(name='Tenant Group 1', slug='tenant-group-1'),
            TenantGroup(name='Tenant Group 2', slug='tenant-group-2'),
        )
        for tenantgroup in self.tenant_groups:
            tenantgroup.save()

        self.tenants = (
            Tenant(name='Test Tenant 1', slug='test-tenant-1', group=self.tenant_groups[0]),
            Tenant(name='Test Tenant 2', slug='test-tenant-2', group=self.tenant_groups[0]),
            Tenant(name='Test Tenant 3', slug='test-tenant-3', group=self.tenant_groups[0]),
        )
        Tenant.objects.bulk_create(self.tenants)

    def test_get_tenant(self):

        url = reverse('tenancy-api:tenant-detail', kwargs={'pk': self.tenants[0].pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.tenants[0].name)

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
            'group': self.tenant_groups[0].pk,
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
            'group': self.tenant_groups[1].pk,
        }

        url = reverse('tenancy-api:tenant-detail', kwargs={'pk': self.tenants[0].pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(Tenant.objects.count(), 3)
        tenant1 = Tenant.objects.get(pk=response.data['id'])
        self.assertEqual(tenant1.name, data['name'])
        self.assertEqual(tenant1.slug, data['slug'])
        self.assertEqual(tenant1.group_id, data['group'])

    def test_delete_tenant(self):

        url = reverse('tenancy-api:tenant-detail', kwargs={'pk': self.tenants[0].pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Tenant.objects.count(), 2)
