from django.test import tag

from tenancy.models import Contact, ContactAssignment, ContactRole, Tenant
from tenancy.tables import *
from utilities.testing import TableTestCases


class TenantGroupTableTestCase(TableTestCases.StandardTableTestCase):
    table = TenantGroupTable


class TenantTableTestCase(TableTestCases.StandardTableTestCase):
    table = TenantTable

    @classmethod
    def setUpTestData(cls):
        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1'),
            Tenant(name='Tenant 2', slug='tenant-2'),
            Tenant(name='Tenant 3', slug='tenant-3'),
        )
        Tenant.objects.bulk_create(tenants)
        cls.contacts = (
            Contact(name='Contact 1'),
            Contact(name='Contact 2'),
        )
        Contact.objects.bulk_create(cls.contacts)
        role = ContactRole.objects.create(name='Contact Role 1', slug='contact-role-1')
        ContactAssignment.objects.bulk_create((
            ContactAssignment(object=tenants[0], contact=cls.contacts[0], role=role),
            ContactAssignment(object=tenants[0], contact=cls.contacts[1], role=role),
            ContactAssignment(object=tenants[1], contact=cls.contacts[0], role=role),
        ))

    @tag('regression')  # Ref: #23349
    def test_contacts_column(self):
        """The contacts column links the contacts of each tenant without further queries."""
        url1, url2 = (contact.get_absolute_url() for contact in self.contacts)
        self.user.config.set('tables.TenantTable.columns', ['name', 'contacts'], commit=True)
        table = TenantTable(Tenant.objects.all())
        table.configure(self.get_request())
        rows = list(table.rows)

        with self.assertNumQueries(0):
            cells = {row.record.name: row.get_cell('contacts') for row in rows}

        self.assertHTMLEqual(cells['Tenant 1'], f'<a href="{url1}">Contact 1</a>, <a href="{url2}">Contact 2</a>')
        self.assertHTMLEqual(cells['Tenant 2'], f'<a href="{url1}">Contact 1</a>')
        self.assertEqual(cells['Tenant 3'], table.columns['contacts'].default)

    @tag('regression')  # Ref: #23349
    def test_contacts_export(self):
        """An export lists the contacts of each tenant without further queries."""
        table = TenantTable(Tenant.objects.all())
        table.configure(self.get_request())
        # An "All Data" export prefetches for every column, hidden or not
        table._apply_prefetching(columns=table.columns.names())
        rows = list(table.rows)

        with self.assertNumQueries(0):
            values = {row.record.name: row.get_cell_value('contacts') for row in rows}

        self.assertEqual(values, {'Tenant 1': 'Contact 1, Contact 2', 'Tenant 2': 'Contact 1', 'Tenant 3': None})


class ContactGroupTableTestCase(TableTestCases.StandardTableTestCase):
    table = ContactGroupTable


class ContactRoleTableTestCase(TableTestCases.StandardTableTestCase):
    table = ContactRoleTable


class ContactTableTestCase(TableTestCases.StandardTableTestCase):
    table = ContactTable


class ContactAssignmentTableTestCase(TableTestCases.StandardTableTestCase):
    table = ContactAssignmentTable
