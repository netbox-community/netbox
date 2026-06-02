from users.tables import *
from utilities.testing import TableTestCases


class TokenTableTestCase(TableTestCases.StandardTableTestCase):
    table = TokenTable


class UserTableTestCase(TableTestCases.StandardTableTestCase):
    table = UserTable


class GroupTableTestCase(TableTestCases.StandardTableTestCase):
    table = GroupTable


class ObjectPermissionTableTestCase(TableTestCases.StandardTableTestCase):
    table = ObjectPermissionTable


class OwnerGroupTableTestCase(TableTestCases.StandardTableTestCase):
    table = OwnerGroupTable


class OwnerTableTestCase(TableTestCases.StandardTableTestCase):
    table = OwnerTable
