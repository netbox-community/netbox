from django.test import TestCase

from tenancy.filtersets import *
from tenancy.models import *
from utilities.testing import ChangeLoggedFilterSetTests


class TenantGroupTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = TenantGroup.objects.all()
    filterset = TenantGroupFilterSet

    @classmethod
    def setUpTestData(cls):

        parent_tenant_groups = (
            TenantGroup(name='Parent Tenant Group 1', slug='parent-tenant-group-1'),
            TenantGroup(name='Parent Tenant Group 2', slug='parent-tenant-group-2'),
            TenantGroup(name='Parent Tenant Group 3', slug='parent-tenant-group-3'),
        )
        for tenantgroup in parent_tenant_groups:
            tenantgroup.save()

        tenant_groups = (
            TenantGroup(name='Tenant Group 1', slug='tenant-group-1', parent=parent_tenant_groups[0], description='A'),
            TenantGroup(name='Tenant Group 2', slug='tenant-group-2', parent=parent_tenant_groups[1], description='B'),
            TenantGroup(name='Tenant Group 3', slug='tenant-group-3', parent=parent_tenant_groups[2], description='C'),
        )
        for tenantgroup in tenant_groups:
            tenantgroup.save()

    def test_name(self):
        params = {'name': ['Tenant Group 1', 'Tenant Group 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['tenant-group-1', 'tenant-group-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['A', 'B']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_parent(self):
        parent_groups = TenantGroup.objects.filter(name__startswith='Parent')[:2]
        params = {'parent_id': [parent_groups[0].pk, parent_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'parent': [parent_groups[0].slug, parent_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class TenantTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = Tenant.objects.all()
    filterset = TenantFilterSet

    @classmethod
    def setUpTestData(cls):

        tenant_groups = (
            TenantGroup(name='Tenant Group 1', slug='tenant-group-1'),
            TenantGroup(name='Tenant Group 2', slug='tenant-group-2'),
            TenantGroup(name='Tenant Group 3', slug='tenant-group-3'),
        )
        for tenantgroup in tenant_groups:
            tenantgroup.save()

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1', group=tenant_groups[0]),
            Tenant(name='Tenant 2', slug='tenant-2', group=tenant_groups[1]),
            Tenant(name='Tenant 3', slug='tenant-3', group=tenant_groups[2]),
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


class ContactGroupTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = ContactGroup.objects.all()
    filterset = ContactGroupFilterSet

    @classmethod
    def setUpTestData(cls):

        parent_contact_groups = (
            ContactGroup(name='Parent Contact Group 1', slug='parent-contact-group-1'),
            ContactGroup(name='Parent Contact Group 2', slug='parent-contact-group-2'),
            ContactGroup(name='Parent Contact Group 3', slug='parent-contact-group-3'),
        )
        for contactgroup in parent_contact_groups:
            contactgroup.save()

        contact_groups = (
            ContactGroup(name='Contact Group 1', slug='contact-group-1', parent=parent_contact_groups[0], description='A'),
            ContactGroup(name='Contact Group 2', slug='contact-group-2', parent=parent_contact_groups[1], description='B'),
            ContactGroup(name='Contact Group 3', slug='contact-group-3', parent=parent_contact_groups[2], description='C'),
        )
        for contactgroup in contact_groups:
            contactgroup.save()

    def test_name(self):
        params = {'name': ['Contact Group 1', 'Contact Group 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['contact-group-1', 'contact-group-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['A', 'B']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_parent(self):
        parent_groups = ContactGroup.objects.filter(parent__isnull=True)[:2]
        params = {'parent_id': [parent_groups[0].pk, parent_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'parent': [parent_groups[0].slug, parent_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ContactRoleTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = ContactRole.objects.all()
    filterset = ContactRoleFilterSet

    @classmethod
    def setUpTestData(cls):

        contact_roles = (
            ContactRole(name='Contact Role 1', slug='contact-role-1'),
            ContactRole(name='Contact Role 2', slug='contact-role-2'),
            ContactRole(name='Contact Role 3', slug='contact-role-3'),
        )
        ContactRole.objects.bulk_create(contact_roles)

    def test_name(self):
        params = {'name': ['Contact Role 1', 'Contact Role 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['contact-role-1', 'contact-role-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ContactTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = Contact.objects.all()
    filterset = ContactFilterSet

    @classmethod
    def setUpTestData(cls):

        contact_groups = (
            ContactGroup(name='Contact Group 1', slug='contact-group-1'),
            ContactGroup(name='Contact Group 2', slug='contact-group-2'),
            ContactGroup(name='Contact Group 3', slug='contact-group-3'),
        )
        for contactgroup in contact_groups:
            contactgroup.save()

        contacts = (
            Contact(name='Contact 1', group=contact_groups[0]),
            Contact(name='Contact 2', group=contact_groups[1]),
            Contact(name='Contact 3', group=contact_groups[2]),
        )
        Contact.objects.bulk_create(contacts)

    def test_name(self):
        params = {'name': ['Contact 1', 'Contact 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_group(self):
        group = ContactGroup.objects.all()[:2]
        params = {'group_id': [group[0].pk, group[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'group': [group[0].slug, group[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
