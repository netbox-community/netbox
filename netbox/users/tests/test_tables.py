from users.tables import *
from utilities.testing import TableTestCases


class TokenTableTest(TableTestCases.StandardTableTestCase):
    table = TokenTable


class UserTableTest(TableTestCases.StandardTableTestCase):
    table = UserTable


class GroupTableTest(TableTestCases.StandardTableTestCase):
    table = GroupTable


class ObjectPermissionTableTest(TableTestCases.StandardTableTestCase):
    table = ObjectPermissionTable


class OwnerGroupTableTest(TableTestCases.StandardTableTestCase):
    table = OwnerGroupTable


class OwnerTableTest(TableTestCases.StandardTableTestCase):
    table = OwnerTable
