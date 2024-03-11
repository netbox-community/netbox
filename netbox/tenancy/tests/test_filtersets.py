from django.test import TestCase

from core.models import ObjectType
from dcim.models import Manufacturer, Site
from tenancy.filtersets import *
from tenancy.models import *
from utilities.testing import ChangeLoggedFilterSetTests


class TenantGroupTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = TenantGroup.objects.all()
    filterset = TenantGroupFilterSet

    @classmethod
    def setUpTestData(cls):

        parent_tenant_groups = (
            TenantGroup(name='Tenant Group 1', slug='tenant-group-1'),
            TenantGroup(name='Tenant Group 2', slug='tenant-group-2'),
            TenantGroup(name='Tenant Group 3', slug='tenant-group-3'),
        )
        for tenant_group in parent_tenant_groups:
            tenant_group.save()

        tenant_groups = (
            TenantGroup(
                name='Tenant Group 1A',
                slug='tenant-group-1a',
                parent=parent_tenant_groups[0],
                description='foobar1'
            ),
            TenantGroup(
                name='Tenant Group 2A',
                slug='tenant-group-2a',
                parent=parent_tenant_groups[1],
                description='foobar2'
            ),
            TenantGroup(
                name='Tenant Group 3A',
                slug='tenant-group-3a',
                parent=parent_tenant_groups[2],
                description='foobar3'
            ),
        )
        for tenant_group in tenant_groups:
            tenant_group.save()

        child_tenant_groups = (
            TenantGroup(name='Tenant Group 1A1', slug='tenant-group-1a1', parent=tenant_groups[0]),
            TenantGroup(name='Tenant Group 2A1', slug='tenant-group-2a1', parent=tenant_groups[1]),
            TenantGroup(name='Tenant Group 3A1', slug='tenant-group-3a1', parent=tenant_groups[2]),
        )
        for tenant_group in child_tenant_groups:
            tenant_group.save()

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Tenant Group 1', 'Tenant Group 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['tenant-group-1', 'tenant-group-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_parent(self):
        tenant_groups = TenantGroup.objects.filter(parent__isnull=True)[:2]
        params = {'parent_id': [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'parent': [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_ancestor(self):
        tenant_groups = TenantGroup.objects.filter(parent__isnull=True)[:2]
        params = {'ancestor_id': [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'ancestor': [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)


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
            Tenant(name='Tenant 1', slug='tenant-1', group=tenant_groups[0], description='foobar1'),
            Tenant(name='Tenant 2', slug='tenant-2', group=tenant_groups[1], description='foobar2'),
            Tenant(name='Tenant 3', slug='tenant-3', group=tenant_groups[2], description='foobar3'),
        )
        Tenant.objects.bulk_create(tenants)

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

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

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ContactGroupTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = ContactGroup.objects.all()
    filterset = ContactGroupFilterSet

    @classmethod
    def setUpTestData(cls):

        parent_contact_groups = (
            ContactGroup(name='Contact Group 1', slug='contact-group-1'),
            ContactGroup(name='Contact Group 2', slug='contact-group-2'),
            ContactGroup(name='Contact Group 3', slug='contact-group-3'),
        )
        for contact_group in parent_contact_groups:
            contact_group.save()

        contact_groups = (
            ContactGroup(
                name='Contact Group 1A',
                slug='contact-group-1a',
                parent=parent_contact_groups[0],
                description='foobar1'
            ),
            ContactGroup(
                name='Contact Group 2A',
                slug='contact-group-2a',
                parent=parent_contact_groups[1],
                description='foobar2'
            ),
            ContactGroup(
                name='Contact Group 3A',
                slug='contact-group-3a',
                parent=parent_contact_groups[2],
                description='foobar3'
            ),
        )
        for contact_group in contact_groups:
            contact_group.save()

        child_contact_groups = (
            ContactGroup(name='Contact Group 1A1', slug='contact-group-1a1', parent=contact_groups[0]),
            ContactGroup(name='Contact Group 2A1', slug='contact-group-2a1', parent=contact_groups[1]),
            ContactGroup(name='Contact Group 3A1', slug='contact-group-3a1', parent=contact_groups[2]),
        )
        for contact_group in child_contact_groups:
            contact_group.save()

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Contact Group 1', 'Contact Group 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['contact-group-1', 'contact-group-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_parent(self):
        contact_groups = ContactGroup.objects.filter(parent__isnull=True)[:2]
        params = {'parent_id': [contact_groups[0].pk, contact_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'parent': [contact_groups[0].slug, contact_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_ancestor(self):
        contact_groups = ContactGroup.objects.filter(parent__isnull=True)[:2]
        params = {'ancestor_id': [contact_groups[0].pk, contact_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'ancestor': [contact_groups[0].slug, contact_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)


class ContactRoleTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = ContactRole.objects.all()
    filterset = ContactRoleFilterSet

    @classmethod
    def setUpTestData(cls):

        contact_roles = (
            ContactRole(name='Contact Role 1', slug='contact-role-1', description='foobar1'),
            ContactRole(name='Contact Role 2', slug='contact-role-2', description='foobar2'),
            ContactRole(name='Contact Role 3', slug='contact-role-3', description='foobar3'),
        )
        ContactRole.objects.bulk_create(contact_roles)

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Contact Role 1', 'Contact Role 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['contact-role-1', 'contact-role-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
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
            Contact(name='Contact 1', group=contact_groups[0], description='foobar1'),
            Contact(name='Contact 2', group=contact_groups[1], description='foobar2'),
            Contact(name='Contact 3', group=contact_groups[2], description='foobar3'),
        )
        Contact.objects.bulk_create(contacts)

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Contact 1', 'Contact 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_group(self):
        group = ContactGroup.objects.all()[:2]
        params = {'group_id': [group[0].pk, group[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'group': [group[0].slug, group[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ContactAssignmentTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = ContactAssignment.objects.all()
    filterset = ContactAssignmentFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)

        contact_groups = (
            ContactGroup(name='Contact Group 1', slug='contact-group-1'),
            ContactGroup(name='Contact Group 2', slug='contact-group-2'),
            ContactGroup(name='Contact Group 3', slug='contact-group-3'),
        )
        for contactgroup in contact_groups:
            contactgroup.save()

        contact_roles = (
            ContactRole(name='Contact Role 1', slug='contact-role-1'),
            ContactRole(name='Contact Role 2', slug='contact-role-2'),
            ContactRole(name='Contact Role 3', slug='contact-role-3'),
        )
        ContactRole.objects.bulk_create(contact_roles)

        contacts = (
            Contact(name='Contact 1', group=contact_groups[0]),
            Contact(name='Contact 2', group=contact_groups[1]),
            Contact(name='Contact 3', group=contact_groups[2]),
        )
        Contact.objects.bulk_create(contacts)

        assignments = (
            ContactAssignment(object=sites[0], contact=contacts[0], role=contact_roles[0]),
            ContactAssignment(object=sites[1], contact=contacts[1], role=contact_roles[1]),
            ContactAssignment(object=sites[2], contact=contacts[2], role=contact_roles[2]),
            ContactAssignment(object=manufacturer, contact=contacts[2], role=contact_roles[2]),
        )
        ContactAssignment.objects.bulk_create(assignments)

    def test_object_type(self):
        params = {'object_type_id': ObjectType.objects.get_by_natural_key('dcim', 'site')}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_contact(self):
        contacts = Contact.objects.all()[:2]
        params = {'contact_id': [contacts[0].pk, contacts[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_group(self):
        group = ContactGroup.objects.all()[:2]
        params = {'group_id': [group[0].pk, group[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'group': [group[0].slug, group[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_role(self):
        role = ContactRole.objects.all()[:2]
        params = {'role_id': [role[0].pk, role[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'role': [role[0].slug, role[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
