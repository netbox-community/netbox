from tenancy.tables import *
from utilities.testing import TableTestCases


class TenantGroupTableTestCase(TableTestCases.StandardTableTestCase):
    table = TenantGroupTable


class TenantTableTestCase(TableTestCases.StandardTableTestCase):
    table = TenantTable


class ContactGroupTableTestCase(TableTestCases.StandardTableTestCase):
    table = ContactGroupTable


class ContactRoleTableTestCase(TableTestCases.StandardTableTestCase):
    table = ContactRoleTable


class ContactTableTestCase(TableTestCases.StandardTableTestCase):
    table = ContactTable


class ContactAssignmentTableTestCase(TableTestCases.StandardTableTestCase):
    table = ContactAssignmentTable
