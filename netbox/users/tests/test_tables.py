from django.test import tag

from users.models import Group, ObjectPermission
from users.tables import *
from utilities.testing import TableTestCases, create_test_user


class TokenTableTestCase(TableTestCases.StandardTableTestCase):
    table = TokenTable


class UserTableTestCase(TableTestCases.StandardTableTestCase):
    table = UserTable


class GroupTableTestCase(TableTestCases.StandardTableTestCase):
    table = GroupTable


class ObjectPermissionTableTestCase(TableTestCases.StandardTableTestCase):
    table = ObjectPermissionTable

    @classmethod
    def setUpTestData(cls):
        cls.users = (
            create_test_user('User 1'),
            create_test_user('User 2'),
        )
        cls.groups = (
            Group(name='Group 1'),
            Group(name='Group 2'),
        )
        Group.objects.bulk_create(cls.groups)
        permissions = (
            ObjectPermission(name='Permission 1', actions=['view']),
            ObjectPermission(name='Permission 2', actions=['view']),
            ObjectPermission(name='Permission 3', actions=['view']),
        )
        ObjectPermission.objects.bulk_create(permissions)
        permissions[0].users.set(cls.users)
        permissions[0].groups.set(cls.groups)
        permissions[1].users.set(cls.users[:1])
        permissions[1].groups.set(cls.groups[:1])

    @tag('regression')  # Ref: #23350
    def test_users_and_groups_columns(self):
        """The users and groups columns link the assignees of each permission without further queries."""
        user_url1, user_url2 = (user.get_absolute_url() for user in self.users)
        group_url1, group_url2 = (group.get_absolute_url() for group in self.groups)
        self.user.config.set('tables.ObjectPermissionTable.columns', ['name', 'users', 'groups'], commit=True)
        table = ObjectPermissionTable(ObjectPermission.objects.all())
        table.configure(self.get_request())
        rows = list(table.rows)

        with self.assertNumQueries(0):
            user_cells = {row.record.name: row.get_cell('users') for row in rows}
            group_cells = {row.record.name: row.get_cell('groups') for row in rows}

        self.assertHTMLEqual(
            user_cells['Permission 1'],
            f'<a href="{user_url1}">User 1</a>, <a href="{user_url2}">User 2</a>'
        )
        self.assertHTMLEqual(user_cells['Permission 2'], f'<a href="{user_url1}">User 1</a>')
        self.assertEqual(user_cells['Permission 3'], table.columns['users'].default)
        self.assertHTMLEqual(
            group_cells['Permission 1'],
            f'<a href="{group_url1}">Group 1</a>, <a href="{group_url2}">Group 2</a>'
        )
        self.assertHTMLEqual(group_cells['Permission 2'], f'<a href="{group_url1}">Group 1</a>')
        self.assertEqual(group_cells['Permission 3'], table.columns['groups'].default)

    @tag('regression')  # Ref: #23350
    def test_users_and_groups_export(self):
        """An export lists the assignees of each permission without further queries."""
        table = ObjectPermissionTable(ObjectPermission.objects.all())
        table.configure(self.get_request())
        # An "All Data" export prefetches for every column, hidden or not
        table._apply_prefetching(columns=table.columns.names())
        rows = list(table.rows)

        with self.assertNumQueries(0):
            values = {row.record.name: (row.get_cell_value('users'), row.get_cell_value('groups')) for row in rows}

        self.assertEqual(values, {
            'Permission 1': ('User 1, User 2', 'Group 1, Group 2'),
            'Permission 2': ('User 1', 'Group 1'),
            'Permission 3': (None, None),
        })


class OwnerGroupTableTestCase(TableTestCases.StandardTableTestCase):
    table = OwnerGroupTable


class OwnerTableTestCase(TableTestCases.StandardTableTestCase):
    table = OwnerTable
