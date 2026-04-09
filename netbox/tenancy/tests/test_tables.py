from tenancy.tables import *
from utilities.testing import TableTestCases


class TenantGroupTableTest(TableTestCases.StandardTableTestCase):
    table = TenantGroupTable


class TenantTableTest(TableTestCases.StandardTableTestCase):
    table = TenantTable


class ContactGroupTableTest(TableTestCases.StandardTableTestCase):
    table = ContactGroupTable


class ContactRoleTableTest(TableTestCases.StandardTableTestCase):
    table = ContactRoleTable


class ContactTableTest(TableTestCases.StandardTableTestCase):
    table = ContactTable


class ContactAssignmentTableTest(TableTestCases.StandardTableTestCase):
    table = ContactAssignmentTable
