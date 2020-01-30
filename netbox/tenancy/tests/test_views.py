import urllib.parse

from django.urls import reverse

from tenancy.models import Tenant, TenantGroup
from utilities.testing import TestCase


class TenantGroupTestCase(TestCase):
    user_permissions = (
        'tenancy.view_tenantgroup',
    )

    @classmethod
    def setUpTestData(cls):

        TenantGroup.objects.bulk_create([
            TenantGroup(name='Tenant Group 1', slug='tenant-group-1'),
            TenantGroup(name='Tenant Group 2', slug='tenant-group-2'),
            TenantGroup(name='Tenant Group 3', slug='tenant-group-3'),
        ])

    def test_tenantgroup_list(self):

        url = reverse('tenancy:tenantgroup_list')

        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_tenantgroup_import(self):
        self.add_permissions('tenancy.add_tenantgroup')

        csv_data = (
            "name,slug",
            "Tenant Group 4,tenant-group-4",
            "Tenant Group 5,tenant-group-5",
            "Tenant Group 6,tenant-group-6",
        )

        response = self.client.post(reverse('tenancy:tenantgroup_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(TenantGroup.objects.count(), 6)


class TenantTestCase(TestCase):
    user_permissions = (
        'tenancy.view_tenant',
    )

    @classmethod
    def setUpTestData(cls):

        tenantgroup = TenantGroup(name='Tenant Group 1', slug='tenant-group-1')
        tenantgroup.save()

        Tenant.objects.bulk_create([
            Tenant(name='Tenant 1', slug='tenant-1', group=tenantgroup),
            Tenant(name='Tenant 2', slug='tenant-2', group=tenantgroup),
            Tenant(name='Tenant 3', slug='tenant-3', group=tenantgroup),
        ])

    def test_tenant_list(self):

        url = reverse('tenancy:tenant_list')
        params = {
            "group": TenantGroup.objects.first().slug,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_tenant(self):

        tenant = Tenant.objects.first()
        response = self.client.get(tenant.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_tenant_import(self):
        self.add_permissions('tenancy.add_tenant')

        csv_data = (
            "name,slug",
            "Tenant 4,tenant-4",
            "Tenant 5,tenant-5",
            "Tenant 6,tenant-6",
        )

        response = self.client.post(reverse('tenancy:tenant_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Tenant.objects.count(), 6)
