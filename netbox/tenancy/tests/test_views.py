from tenancy.models import Tenant, TenantGroup
from utilities.testing import ViewTestCases


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

        cls.form_data = {
            'name': 'Tenant Group X',
            'slug': 'tenant-group-x',
            'description': 'A new tenant group',
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

        tags = cls.create_tags('Alpha', 'Bravo', 'Charlie')

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
