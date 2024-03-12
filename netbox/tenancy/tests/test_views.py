from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from dcim.models import Site
from tenancy.choices import ContactPriorityChoices
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

        cls.csv_update_data = (
            "id,name,description",
            f"{tenant_groups[0].pk},Tenant Group 7,Fourth tenant group7",
            f"{tenant_groups[1].pk},Tenant Group 8,Fifth tenant group8",
            f"{tenant_groups[2].pk},Tenant Group 0,Sixth tenant group9",
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

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1', group=tenant_groups[0]),
            Tenant(name='Tenant 2', slug='tenant-2', group=tenant_groups[0]),
            Tenant(name='Tenant 3', slug='tenant-3', group=tenant_groups[0]),
        )
        Tenant.objects.bulk_create(tenants)

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

        cls.csv_update_data = (
            "id,name,description",
            f"{tenants[0].pk},Tenant 7,New description 7",
            f"{tenants[1].pk},Tenant 8,New description 8",
            f"{tenants[2].pk},Tenant 9,New description 9",
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

        cls.csv_update_data = (
            "id,name,description",
            f"{contact_groups[0].pk},Contact Group 7,Fourth contact group7",
            f"{contact_groups[1].pk},Contact Group 8,Fifth contact group8",
            f"{contact_groups[2].pk},Contact Group 0,Sixth contact group9",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }


class ContactRoleTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = ContactRole

    @classmethod
    def setUpTestData(cls):

        contact_roles = (
            ContactRole(name='Contact Role 1', slug='contact-role-1'),
            ContactRole(name='Contact Role 2', slug='contact-role-2'),
            ContactRole(name='Contact Role 3', slug='contact-role-3'),
        )
        ContactRole.objects.bulk_create(contact_roles)

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

        cls.csv_update_data = (
            "id,name,description",
            f"{contact_roles[0].pk},Contact Role 7,New description 7",
            f"{contact_roles[1].pk},Contact Role 8,New description 8",
            f"{contact_roles[2].pk},Contact Role 9,New description 9",
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

        contacts = (
            Contact(name='Contact 1', group=contact_groups[0]),
            Contact(name='Contact 2', group=contact_groups[0]),
            Contact(name='Contact 3', group=contact_groups[0]),
        )
        Contact.objects.bulk_create(contacts)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Contact X',
            'group': contact_groups[1].pk,
            'comments': 'Some comments',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "group,name",
            "Contact Group 1,Contact 4",
            "Contact Group 1,Contact 5",
            "Contact Group 1,Contact 6",
        )

        cls.csv_update_data = (
            "id,name,comments",
            f"{contacts[0].pk},Contact Group 7,New comments 7",
            f"{contacts[1].pk},Contact Group 8,New comments 8",
            f"{contacts[2].pk},Contact Group 9,New comments 9",
        )

        cls.bulk_edit_data = {
            'group': contact_groups[1].pk,
        }


class ContactAssignmentTestCase(
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase
):
    model = ContactAssignment

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
            Site(name='Site 4', slug='site-4'),
        )
        Site.objects.bulk_create(sites)

        contacts = (
            Contact(name='Contact 1'),
            Contact(name='Contact 2'),
            Contact(name='Contact 3'),
            Contact(name='Contact 4'),
        )
        Contact.objects.bulk_create(contacts)

        contact_roles = (
            ContactRole(name='Contact Role 1', slug='contact-role-1'),
            ContactRole(name='Contact Role 2', slug='contact-role-2'),
            ContactRole(name='Contact Role 3', slug='contact-role-3'),
            ContactRole(name='Contact Role 4', slug='contact-role-4'),
        )
        ContactRole.objects.bulk_create(contact_roles)

        assignments = (
            ContactAssignment(
                object=sites[0],
                contact=contacts[0],
                role=contact_roles[0],
                priority=ContactPriorityChoices.PRIORITY_PRIMARY
            ),
            ContactAssignment(
                object=sites[1],
                contact=contacts[1],
                role=contact_roles[1],
                priority=ContactPriorityChoices.PRIORITY_SECONDARY
            ),
            ContactAssignment(
                object=sites[2],
                contact=contacts[2],
                role=contact_roles[2],
                priority=ContactPriorityChoices.PRIORITY_TERTIARY
            ),
        )
        ContactAssignment.objects.bulk_create(assignments)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'object_type': ContentType.objects.get_for_model(Site).pk,
            'object_id': sites[3].pk,
            'contact': contacts[3].pk,
            'role': contact_roles[3].pk,
            'priority': ContactPriorityChoices.PRIORITY_INACTIVE,
            'tags': [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            'role': contact_roles[3].pk,
            'priority': ContactPriorityChoices.PRIORITY_INACTIVE,
        }

    def _get_url(self, action, instance=None):
        # Override creation URL to append object_type & object_id parameters
        if action == 'add':
            url = reverse('tenancy:contactassignment_add')
            content_type = ContentType.objects.get_for_model(Site).pk
            object_id = Site.objects.first().pk
            return f"{url}?object_type={content_type}&object_id={object_id}"

        return super()._get_url(action, instance=instance)
