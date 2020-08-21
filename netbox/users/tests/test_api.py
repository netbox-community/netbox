from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from users.models import ObjectPermission
from utilities.testing import APIViewTestCases, APITestCase, disable_warnings


class AppTest(APITestCase):

    def test_root(self):

        url = reverse('users-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class UserTest(APIViewTestCases.APIViewTestCase):
    model = User
    view_namespace = 'users'
    brief_fields = ['id', 'url', 'username']
    create_data = [
        {
            'username': 'User_4',
        },
        {
            'username': 'User_5',
        },
        {
            'username': 'User_6',
        },
    ]

    @classmethod
    def setUpTestData(cls):

        users = (
            User(username='User_1'),
            User(username='User_2'),
            User(username='User_3'),
        )
        User.objects.bulk_create(users)


class GroupTest(APIViewTestCases.APIViewTestCase):
    model = Group
    view_namespace = 'users'
    brief_fields = ['id', 'name', 'url']
    create_data = [
        {
            'name': 'Group 4',
        },
        {
            'name': 'Group 5',
        },
        {
            'name': 'Group 6',
        },
    ]

    @classmethod
    def setUpTestData(cls):

        users = (
            Group(name='Group 1'),
            Group(name='Group 2'),
            Group(name='Group 3'),
        )
        Group.objects.bulk_create(users)


class ObjectPermissionTest(APIViewTestCases.APIViewTestCase):
    model = ObjectPermission
    brief_fields = ['actions', 'enabled', 'groups', 'id', 'name', 'object_types', 'url', 'users']

    @classmethod
    def setUpTestData(cls):

        groups = (
            Group(name='Group 1'),
            Group(name='Group 2'),
            Group(name='Group 3'),
        )
        Group.objects.bulk_create(groups)

        users = (
            User(username='User 1', is_active=True),
            User(username='User 2', is_active=True),
            User(username='User 3', is_active=True),
        )
        User.objects.bulk_create(users)

        object_type = ContentType.objects.get(app_label='dcim', model='device')

        for i in range(0, 3):
            objectpermission = ObjectPermission(
                name=f'Permission {i+1}',
                actions=['view', 'add', 'change', 'delete'],
                constraints={'name': f'TEST{i+1}'}
            )
            objectpermission.save()
            objectpermission.object_types.add(object_type)
            objectpermission.groups.add(groups[i])
            objectpermission.users.add(users[i])

        cls.create_data = [
            {
                'name': 'Permission 4',
                'object_types': ['dcim.site'],
                'groups': [groups[0].pk],
                'users': [users[0].pk],
                'actions': ['view', 'add', 'change', 'delete'],
                'constraints': {'name': 'TEST4'},
            },
            {
                'name': 'Permission 5',
                'object_types': ['dcim.site'],
                'groups': [groups[1].pk],
                'users': [users[1].pk],
                'actions': ['view', 'add', 'change', 'delete'],
                'constraints': {'name': 'TEST5'},
            },
            {
                'name': 'Permission 6',
                'object_types': ['dcim.site'],
                'groups': [groups[2].pk],
                'users': [users[2].pk],
                'actions': ['view', 'add', 'change', 'delete'],
                'constraints': {'name': 'TEST6'},
            },
        ]
