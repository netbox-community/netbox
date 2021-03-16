from django.urls import reverse

from tenancy.models import Tenant, TenantGroup
from utilities.testing import APITestCase, APIViewTestCases


class AppTest(APITestCase):

    def test_root(self):

        url = reverse('tenancy-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class TenantGroupTest(APIViewTestCases.APIViewTestCase):
    model = TenantGroup
    brief_fields = ['_depth', 'id', 'name', 'slug', 'tenant_count', 'url']
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        parent_tenant_groups = (
            TenantGroup.objects.create(name='Parent Tenant Group 1', slug='parent-tenant-group-1'),
            TenantGroup.objects.create(name='Parent Tenant Group 2', slug='parent-tenant-group-2'),
        )

        TenantGroup.objects.create(name='Tenant Group 1', slug='tenant-group-1', parent=parent_tenant_groups[0])
        TenantGroup.objects.create(name='Tenant Group 2', slug='tenant-group-2', parent=parent_tenant_groups[0])
        TenantGroup.objects.create(name='Tenant Group 3', slug='tenant-group-3', parent=parent_tenant_groups[0])

        cls.create_data = [
            {
                'name': 'Tenant Group 4',
                'slug': 'tenant-group-4',
                'parent': parent_tenant_groups[1].pk,
            },
            {
                'name': 'Tenant Group 5',
                'slug': 'tenant-group-5',
                'parent': parent_tenant_groups[1].pk,
            },
            {
                'name': 'Tenant Group 6',
                'slug': 'tenant-group-6',
                'parent': parent_tenant_groups[1].pk,
            },
        ]


class TenantTest(APIViewTestCases.APIViewTestCase):
    model = Tenant
    brief_fields = ['id', 'name', 'slug', 'url']
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        tenant_groups = (
            TenantGroup.objects.create(name='Tenant Group 1', slug='tenant-group-1'),
            TenantGroup.objects.create(name='Tenant Group 2', slug='tenant-group-2'),
        )

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1', group=tenant_groups[0]),
            Tenant(name='Tenant 2', slug='tenant-2', group=tenant_groups[0]),
            Tenant(name='Tenant 3', slug='tenant-3', group=tenant_groups[0]),
        )
        Tenant.objects.bulk_create(tenants)

        cls.create_data = [
            {
                'name': 'Tenant 4',
                'slug': 'tenant-4',
                'group': tenant_groups[1].pk,
            },
            {
                'name': 'Tenant 5',
                'slug': 'tenant-5',
                'group': tenant_groups[1].pk,
            },
            {
                'name': 'Tenant 6',
                'slug': 'tenant-6',
                'group': tenant_groups[1].pk,
            },
        ]
