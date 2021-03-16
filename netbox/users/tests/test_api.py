from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from users.models import ObjectPermission
from utilities.testing import APIViewTestCases, APITestCase
from utilities.utils import deepmerge


class AppTest(APITestCase):

    def test_root(self):

        url = reverse('users-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class UserTest(APIViewTestCases.APIViewTestCase):
    model = User
    view_namespace = 'users'
    brief_fields = ['display', 'id', 'url', 'username']
    validation_excluded_fields = ['password']
    create_data = [
        {
            'username': 'User_4',
            'password': 'password4',
        },
        {
            'username': 'User_5',
            'password': 'password5',
        },
        {
            'username': 'User_6',
            'password': 'password6',
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
    brief_fields = ['display', 'id', 'name', 'url']
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
    brief_fields = ['actions', 'display', 'enabled', 'groups', 'id', 'name', 'object_types', 'url', 'users']

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

        for i in range(3):
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

        cls.bulk_update_data = {
            'description': 'New description',
        }


class UserConfigTest(APITestCase):

    def test_get(self):
        """
        Retrieve user configuration via GET request.
        """
        userconfig = self.user.config
        url = reverse('users-api:userconfig-list')

        response = self.client.get(url, **self.header)
        self.assertEqual(response.data, {})

        data = {
            "a": 123,
            "b": 456,
            "c": 789,
        }
        userconfig.data = data
        userconfig.save()
        response = self.client.get(url, **self.header)
        self.assertEqual(response.data, data)

    def test_patch(self):
        """
        Set user config via PATCH requests.
        """
        userconfig = self.user.config
        url = reverse('users-api:userconfig-list')

        data = {
            "a": {
                "a1": "X",
                "a2": "Y",
            },
            "b": {
                "b1": "Z",
            }
        }
        response = self.client.patch(url, data=data, format='json', **self.header)
        self.assertDictEqual(response.data, data)
        userconfig.refresh_from_db()
        self.assertDictEqual(userconfig.data, data)

        update_data = {
            "c": 123
        }
        response = self.client.patch(url, data=update_data, format='json', **self.header)
        new_data = deepmerge(data, update_data)
        self.assertDictEqual(response.data, new_data)
        userconfig.refresh_from_db()
        self.assertDictEqual(userconfig.data, new_data)
