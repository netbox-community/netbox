from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from django.urls import reverse

from tenancy.models import Tenant, TenantGroup
from users.models import Token


class TenantGroupTest(APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

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

    def test_create_tenantgroup(self):

        data = {
            'name': 'Test Tenant Group 4',
            'slug': 'test-tenant-group-4',
        }

        url = reverse('tenancy-api:tenantgroup-list')
        response = self.client.post(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TenantGroup.objects.count(), 4)

    def test_update_tenantgroup(self):

        data = {
            'name': 'Test Tenant Group X',
            'slug': 'test-tenant-group-x',
        }

        url = reverse('tenancy-api:tenantgroup-detail', kwargs={'pk': self.tenantgroup1.pk})
        response = self.client.put(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(TenantGroup.objects.count(), 3)
        self.assertEqual(TenantGroup.objects.get(pk=self.tenantgroup1.pk).name, data['name'])
        self.assertEqual(TenantGroup.objects.get(pk=self.tenantgroup1.pk).slug, data['slug'])

    def test_delete_tenantgroup(self):

        url = reverse('tenancy-api:tenantgroup-detail', kwargs={'pk': self.tenantgroup1.pk})
        response = self.client.delete(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TenantGroup.objects.count(), 2)


class TenantTest(APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

        self.tenant1 = Tenant.objects.create(name='Test Tenant 1', slug='test-tenant-1')
        self.tenant2 = Tenant.objects.create(name='Test Tenant 2', slug='test-tenant-2')
        self.tenant3 = Tenant.objects.create(name='Test Tenant 3', slug='test-tenant-3')

    def test_get_tenant(self):

        url = reverse('tenancy-api:tenant-detail', kwargs={'pk': self.tenant1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.tenant1.name)

    def test_list_tenants(self):

        url = reverse('tenancy-api:tenant-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_tenant(self):

        data = {
            'name': 'Test Tenant 4',
            'slug': 'test-tenant-4',
        }

        url = reverse('tenancy-api:tenant-list')
        response = self.client.post(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tenant.objects.count(), 4)

    def test_update_tenant(self):

        data = {
            'name': 'Test Tenant X',
            'slug': 'test-tenant-x',
        }

        url = reverse('tenancy-api:tenant-detail', kwargs={'pk': self.tenant1.pk})
        response = self.client.put(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Tenant.objects.count(), 3)
        self.assertEqual(Tenant.objects.get(pk=self.tenant1.pk).name, data['name'])
        self.assertEqual(Tenant.objects.get(pk=self.tenant1.pk).slug, data['slug'])

    def test_delete_tenant(self):

        url = reverse('tenancy-api:tenant-detail', kwargs={'pk': self.tenant1.pk})
        response = self.client.delete(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Tenant.objects.count(), 2)
