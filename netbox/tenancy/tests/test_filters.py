from django.test import TestCase

from tenancy.filters import *
from tenancy.models import Tenant, TenantGroup


class TenantGroupTestCase(TestCase):
    queryset = TenantGroup.objects.all()
    filterset = TenantGroupFilterSet

    @classmethod
    def setUpTestData(cls):

        groups = (
            TenantGroup(name='Tenant Group 1', slug='tenant-group-1'),
            TenantGroup(name='Tenant Group 2', slug='tenant-group-2'),
            TenantGroup(name='Tenant Group 3', slug='tenant-group-3'),
        )
        TenantGroup.objects.bulk_create(groups)

    def test_id(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id': [str(id) for id in id_list]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Tenant Group 1', 'Tenant Group 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['tenant-group-1', 'tenant-group-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class TenantTestCase(TestCase):
    queryset = Tenant.objects.all()
    filterset = TenantFilterSet

    @classmethod
    def setUpTestData(cls):

        groups = (
            TenantGroup(name='Tenant Group 1', slug='tenant-group-1'),
            TenantGroup(name='Tenant Group 2', slug='tenant-group-2'),
            TenantGroup(name='Tenant Group 3', slug='tenant-group-3'),
        )
        TenantGroup.objects.bulk_create(groups)

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1', group=groups[0]),
            Tenant(name='Tenant 2', slug='tenant-2', group=groups[1]),
            Tenant(name='Tenant 3', slug='tenant-3', group=groups[2]),
        )
        Tenant.objects.bulk_create(tenants)

    def test_name(self):
        params = {'name': ['Tenant 1', 'Tenant 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['tenant-1', 'tenant-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_group(self):
        group = TenantGroup.objects.all()[:2]
        params = {'group_id': [group[0].pk, group[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'group': [group[0].slug, group[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
