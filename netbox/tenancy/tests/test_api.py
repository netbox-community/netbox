from django.urls import reverse

from dcim.models import Site
from tenancy.choices import *
from tenancy.models import *
from utilities.testing import APITestCase, APIViewTestCases


class AppTest(APITestCase):

    def test_root(self):

        url = reverse('tenancy-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class TenantGroupTest(APIViewTestCases.APIViewTestCase):
    model = TenantGroup
    brief_fields = ['_depth', 'display', 'id', 'name', 'slug', 'tenant_count', 'url']
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
    brief_fields = ['display', 'id', 'name', 'slug', 'url']
    bulk_update_data = {
        'group': None,
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


class ContactGroupTest(APIViewTestCases.APIViewTestCase):
    model = ContactGroup
    brief_fields = ['_depth', 'contact_count', 'display', 'id', 'name', 'slug', 'url']
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        parent_contact_groups = (
            ContactGroup.objects.create(name='Parent Contact Group 1', slug='parent-contact-group-1'),
            ContactGroup.objects.create(name='Parent Contact Group 2', slug='parent-contact-group-2'),
        )

        ContactGroup.objects.create(name='Contact Group 1', slug='contact-group-1', parent=parent_contact_groups[0])
        ContactGroup.objects.create(name='Contact Group 2', slug='contact-group-2', parent=parent_contact_groups[0])
        ContactGroup.objects.create(name='Contact Group 3', slug='contact-group-3', parent=parent_contact_groups[0])

        cls.create_data = [
            {
                'name': 'Contact Group 4',
                'slug': 'contact-group-4',
                'parent': parent_contact_groups[1].pk,
            },
            {
                'name': 'Contact Group 5',
                'slug': 'contact-group-5',
                'parent': parent_contact_groups[1].pk,
            },
            {
                'name': 'Contact Group 6',
                'slug': 'contact-group-6',
                'parent': parent_contact_groups[1].pk,
            },
        ]


class ContactRoleTest(APIViewTestCases.APIViewTestCase):
    model = ContactRole
    brief_fields = ['display', 'id', 'name', 'slug', 'url']
    create_data = [
        {
            'name': 'Contact Role 4',
            'slug': 'contact-role-4',
        },
        {
            'name': 'Contact Role 5',
            'slug': 'contact-role-5',
        },
        {
            'name': 'Contact Role 6',
            'slug': 'contact-role-6',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        contact_roles = (
            ContactRole(name='Contact Role 1', slug='contact-role-1'),
            ContactRole(name='Contact Role 2', slug='contact-role-2'),
            ContactRole(name='Contact Role 3', slug='contact-role-3'),
        )
        ContactRole.objects.bulk_create(contact_roles)


class ContactTest(APIViewTestCases.APIViewTestCase):
    model = Contact
    brief_fields = ['display', 'id', 'name', 'url']
    bulk_update_data = {
        'group': None,
        'comments': 'New comments',
    }

    @classmethod
    def setUpTestData(cls):

        contact_groups = (
            ContactGroup.objects.create(name='Contact Group 1', slug='contact-group-1'),
            ContactGroup.objects.create(name='Contact Group 2', slug='contact-group-2'),
        )

        contacts = (
            Contact(name='Contact 1', group=contact_groups[0]),
            Contact(name='Contact 2', group=contact_groups[0]),
            Contact(name='Contact 3', group=contact_groups[0]),
        )
        Contact.objects.bulk_create(contacts)

        cls.create_data = [
            {
                'name': 'Contact 4',
                'group': contact_groups[1].pk,
            },
            {
                'name': 'Contact 5',
                'group': contact_groups[1].pk,
            },
            {
                'name': 'Contact 6',
                'group': contact_groups[1].pk,
            },
        ]


class ContactAssignmentTest(APIViewTestCases.APIViewTestCase):
    model = ContactAssignment
    brief_fields = ['contact', 'display', 'id', 'priority', 'role', 'url']
    bulk_update_data = {
        'priority': ContactPriorityChoices.PRIORITY_INACTIVE,
    }

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        contacts = (
            Contact(name='Contact 1'),
            Contact(name='Contact 2'),
            Contact(name='Contact 3'),
            Contact(name='Contact 4'),
            Contact(name='Contact 5'),
            Contact(name='Contact 6'),
        )
        Contact.objects.bulk_create(contacts)

        contact_roles = (
            ContactRole(name='Contact Role 1', slug='contact-role-1'),
            ContactRole(name='Contact Role 2', slug='contact-role-2'),
            ContactRole(name='Contact Role 3', slug='contact-role-3'),
        )
        ContactRole.objects.bulk_create(contact_roles)

        contact_assignments = (
            ContactAssignment(object=sites[0], contact=contacts[0], role=contact_roles[0], priority=ContactPriorityChoices.PRIORITY_PRIMARY),
            ContactAssignment(object=sites[0], contact=contacts[1], role=contact_roles[1], priority=ContactPriorityChoices.PRIORITY_SECONDARY),
            ContactAssignment(object=sites[0], contact=contacts[2], role=contact_roles[2], priority=ContactPriorityChoices.PRIORITY_TERTIARY),
        )
        ContactAssignment.objects.bulk_create(contact_assignments)

        cls.create_data = [
            {
                'content_type': 'dcim.site',
                'object_id': sites[1].pk,
                'contact': contacts[3].pk,
                'role': contact_roles[0].pk,
                'priority': ContactPriorityChoices.PRIORITY_PRIMARY,
            },
            {
                'content_type': 'dcim.site',
                'object_id': sites[1].pk,
                'contact': contacts[4].pk,
                'role': contact_roles[1].pk,
                'priority': ContactPriorityChoices.PRIORITY_SECONDARY,
            },
            {
                'content_type': 'dcim.site',
                'object_id': sites[1].pk,
                'contact': contacts[5].pk,
                'role': contact_roles[2].pk,
                'priority': ContactPriorityChoices.PRIORITY_TERTIARY,
            },
        ]
