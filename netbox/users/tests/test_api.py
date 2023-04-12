from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from users.models import ObjectPermission, Token
from utilities.testing import APIViewTestCases, APITestCase
from utilities.utils import deepmerge


class AppTest(APITestCase):

    def test_root(self):

        url = reverse('users-api:api-root')
        response = self.client.get(f'{url}?format=api', **self.header)

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
    bulk_update_data = {
        'email': 'test@example.com',
    }

    @classmethod
    def setUpTestData(cls):

        users = (
            User(username='User_1', password='password1'),
            User(username='User_2', password='password2'),
            User(username='User_3', password='password3'),
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

    def test_bulk_update_objects(self):
        """
        Disabled test. There's no attribute we can set in bulk for Groups.
        """
        return


class TokenTest(
    # No GraphQL support for Token
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase
):
    model = Token
    brief_fields = ['display', 'id', 'key', 'url', 'write_enabled']
    bulk_update_data = {
        'description': 'New description',
    }

    def setUp(self):
        super().setUp()

        tokens = (
            # We already start with one Token, created by the test class
            Token(user=self.user),
            Token(user=self.user),
        )
        # Use save() instead of bulk_create() to ensure keys get automatically generated
        for token in tokens:
            token.save()

        self.create_data = [
            {
                'user': self.user.pk,
            },
            {
                'user': self.user.pk,
            },
            {
                'user': self.user.pk,
            },
        ]

    def test_provision_token_valid(self):
        """
        Test the provisioning of a new REST API token given a valid username and password.
        """
        data = {
            'username': 'user1',
            'password': 'abc123',
        }
        user = User.objects.create_user(**data)
        url = reverse('users-api:token_provision')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 201)
        self.assertIn('key', response.data)
        self.assertEqual(len(response.data['key']), 40)
        token = Token.objects.get(user=user)
        self.assertEqual(token.key, response.data['key'])

    def test_provision_token_invalid(self):
        """
        Test the behavior of the token provisioning view when invalid credentials are supplied.
        """
        data = {
            'username': 'nonexistentuser',
            'password': 'abc123',
        }
        url = reverse('users-api:token_provision')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 403)

    def test_provision_token_other_user(self):
        """
        Test provisioning a Token for a different User with & without the grant_token permission.
        """
        self.add_permissions('users.add_token')
        user2 = User.objects.create_user(username='testuser2')
        data = {
            'user': user2.id,
        }
        url = reverse('users-api:token-list')

        # Attempt to create a new Token for User2 *without* the grant_token permission
        response = self.client.post(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 403)

        # Assign grant_token permission and successfully create a new Token for User2
        self.add_permissions('users.grant_token')
        response = self.client.post(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 201)


class ObjectPermissionTest(
    # No GraphQL support for ObjectPermission
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase
):
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
