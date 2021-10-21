from tenancy.models import *
from utilities.testing import ViewTestCases, create_tags


class TenantGroupTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = TenantGroup

    @classmethod
    def setUpTestData(cls):

        tenant_groups = (
            TenantGroup(name='Tenant Group 1', slug='tenant-group-1'),
            TenantGroup(name='Tenant Group 2', slug='tenant-group-2'),
            TenantGroup(name='Tenant Group 3', slug='tenant-group-3'),
        )
        for tenanantgroup in tenant_groups:
            tenanantgroup.save()

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Tenant Group X',
            'slug': 'tenant-group-x',
            'description': 'A new tenant group',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug,description",
            "Tenant Group 4,tenant-group-4,Fourth tenant group",
            "Tenant Group 5,tenant-group-5,Fifth tenant group",
            "Tenant Group 6,tenant-group-6,Sixth tenant group",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }


class TenantTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = Tenant

    @classmethod
    def setUpTestData(cls):

        tenant_groups = (
            TenantGroup(name='Tenant Group 1', slug='tenant-group-1'),
            TenantGroup(name='Tenant Group 2', slug='tenant-group-2'),
        )
        for tenanantgroup in tenant_groups:
            tenanantgroup.save()

        Tenant.objects.bulk_create([
            Tenant(name='Tenant 1', slug='tenant-1', group=tenant_groups[0]),
            Tenant(name='Tenant 2', slug='tenant-2', group=tenant_groups[0]),
            Tenant(name='Tenant 3', slug='tenant-3', group=tenant_groups[0]),
        ])

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Tenant X',
            'slug': 'tenant-x',
            'group': tenant_groups[1].pk,
            'description': 'A new tenant',
            'comments': 'Some comments',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug",
            "Tenant 4,tenant-4",
            "Tenant 5,tenant-5",
            "Tenant 6,tenant-6",
        )

        cls.bulk_edit_data = {
            'group': tenant_groups[1].pk,
        }


class ContactGroupTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = ContactGroup

    @classmethod
    def setUpTestData(cls):

        contact_groups = (
            ContactGroup(name='Contact Group 1', slug='contact-group-1'),
            ContactGroup(name='Contact Group 2', slug='contact-group-2'),
            ContactGroup(name='Contact Group 3', slug='contact-group-3'),
        )
        for tenanantgroup in contact_groups:
            tenanantgroup.save()

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Contact Group X',
            'slug': 'contact-group-x',
            'description': 'A new contact group',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug,description",
            "Contact Group 4,contact-group-4,Fourth contact group",
            "Contact Group 5,contact-group-5,Fifth contact group",
            "Contact Group 6,contact-group-6,Sixth contact group",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }


class ContactRoleTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = ContactRole

    @classmethod
    def setUpTestData(cls):

        ContactRole.objects.bulk_create([
            ContactRole(name='Contact Role 1', slug='contact-role-1'),
            ContactRole(name='Contact Role 2', slug='contact-role-2'),
            ContactRole(name='Contact Role 3', slug='contact-role-3'),
        ])

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Devie Role X',
            'slug': 'contact-role-x',
            'description': 'New contact role',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug",
            "Contact Role 4,contact-role-4",
            "Contact Role 5,contact-role-5",
            "Contact Role 6,contact-role-6",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }


class ContactTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = Contact

    @classmethod
    def setUpTestData(cls):

        contact_groups = (
            ContactGroup(name='Contact Group 1', slug='contact-group-1'),
            ContactGroup(name='Contact Group 2', slug='contact-group-2'),
        )
        for contactgroup in contact_groups:
            contactgroup.save()

        Contact.objects.bulk_create([
            Contact(name='Contact 1', group=contact_groups[0]),
            Contact(name='Contact 2', group=contact_groups[0]),
            Contact(name='Contact 3', group=contact_groups[0]),
        ])

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Contact X',
            'group': contact_groups[1].pk,
            'comments': 'Some comments',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug",
            "Contact 4,contact-4",
            "Contact 5,contact-5",
            "Contact 6,contact-6",
        )

        cls.bulk_edit_data = {
            'group': contact_groups[1].pk,
        }
