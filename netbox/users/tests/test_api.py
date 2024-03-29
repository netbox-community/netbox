from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import ObjectType
from users.models import Group, ObjectPermission, Token
from utilities.data import deepmerge
from utilities.testing import APIViewTestCases, APITestCase, create_test_user


User = get_user_model()


class AppTest(APITestCase):

    def test_root(self):

        url = reverse('users-api:api-root')
        response = self.client.get(f'{url}?format=api', **self.header)
        self.assertEqual(response.status_code, 200)


class UserTest(APIViewTestCases.APIViewTestCase):
    model = User
    brief_fields = ['display', 'id', 'url', 'username']
    validation_excluded_fields = ['password']
    bulk_update_data = {
        'email': 'test@example.com',
    }

    @classmethod
    def setUpTestData(cls):

        permissions = (
            ObjectPermission(name='Permission 1', actions=['view']),
            ObjectPermission(name='Permission 2', actions=['view']),
            ObjectPermission(name='Permission 3', actions=['view']),
        )
        ObjectPermission.objects.bulk_create(permissions)
        permissions[0].object_types.add(ObjectType.objects.get_by_natural_key('dcim', 'site'))
        permissions[1].object_types.add(ObjectType.objects.get_by_natural_key('dcim', 'location'))
        permissions[2].object_types.add(ObjectType.objects.get_by_natural_key('dcim', 'rack'))

        users = (
            User(username='User1', password='password1'),
            User(username='User2', password='password2'),
            User(username='User3', password='password3'),
        )
        User.objects.bulk_create(users)

        cls.create_data = [
            {
                'username': 'User4',
                'password': 'password4',
                'permissions': [permissions[0].pk],
            },
            {
                'username': 'User5',
                'password': 'password5',
                'permissions': [permissions[1].pk],
            },
            {
                'username': 'User6',
                'password': 'password6',
                'permissions': [permissions[2].pk],
            },
        ]

    def test_that_password_is_changed(self):
        """
        Test that password is changed
        """

        obj_perm = ObjectPermission(
            name='Test permission',
            actions=['change']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

        user_credentials = {
            'username': 'newuser',
            'password': 'abc123',
        }
        user = User.objects.create_user(**user_credentials)

        data = {
            'password': 'newpassword'
        }
        url = reverse('users-api:user-detail', kwargs={'pk': user.id})
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.check_password(data['password']))


class GroupTest(APIViewTestCases.APIViewTestCase):
    model = Group
    brief_fields = ['display', 'id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):

        permissions = (
            ObjectPermission(name='Permission 1', actions=['view']),
            ObjectPermission(name='Permission 2', actions=['view']),
            ObjectPermission(name='Permission 3', actions=['view']),
        )
        ObjectPermission.objects.bulk_create(permissions)
        permissions[0].object_types.add(ObjectType.objects.get_by_natural_key('dcim', 'site'))
        permissions[1].object_types.add(ObjectType.objects.get_by_natural_key('dcim', 'location'))
        permissions[2].object_types.add(ObjectType.objects.get_by_natural_key('dcim', 'rack'))

        groups = (
            Group(name='Group 1'),
            Group(name='Group 2'),
            Group(name='Group 3'),
        )
        Group.objects.bulk_create(groups)

        cls.create_data = [
            {
                'name': 'Group 4',
                'permissions': [permissions[0].pk],
            },
            {
                'name': 'Group 5',
                'permissions': [permissions[1].pk],
            },
            {
                'name': 'Group 6',
                'permissions': [permissions[2].pk],
            },
        ]

    def model_to_dict(self, instance, *args, **kwargs):
        # Overwrite permissions attr to work around the serializer field having a different name
        data = super().model_to_dict(instance, *args, **kwargs)
        data['permissions'] = list(instance.object_permissions.values_list('id', flat=True))
        return data

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
    brief_fields = ['description', 'display', 'id', 'key', 'url', 'write_enabled']
    bulk_update_data = {
        'description': 'New description',
    }

    def setUp(self):
        super().setUp()

        # Apply grant_token permission to enable the creation of Tokens for other Users
        self.add_permissions('users.grant_token')

    @classmethod
    def setUpTestData(cls):
        users = (
            create_test_user('User1'),
            create_test_user('User2'),
            create_test_user('User3'),
        )

        tokens = (
            Token(user=users[0]),
            Token(user=users[1]),
            Token(user=users[2]),
        )
        # Use save() instead of bulk_create() to ensure keys get automatically generated
        for token in tokens:
            token.save()

        cls.create_data = [
            {
                'user': users[0].pk,
            },
            {
                'user': users[1].pk,
            },
            {
                'user': users[2].pk,
            },
        ]

    def test_provision_token_valid(self):
        """
        Test the provisioning of a new REST API token given a valid username and password.
        """
        user_credentials = {
            'username': 'user1',
            'password': 'abc123',
        }
        user = User.objects.create_user(**user_credentials)

        data = {
            **user_credentials,
            'description': 'My API token',
            'expires': '2099-12-31T23:59:59Z',
        }
        url = reverse('users-api:token_provision')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 201)
        self.assertIn('key', response.data)
        self.assertEqual(len(response.data['key']), 40)
        self.assertEqual(response.data['description'], data['description'])
        self.assertEqual(response.data['expires'], data['expires'])
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
        # Clear grant_token permission assigned by setUpTestData
        ObjectPermission.objects.filter(users=self.user).delete()

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
    brief_fields = ['actions', 'description', 'display', 'enabled', 'id', 'name', 'object_types', 'url']

    @classmethod
    def setUpTestData(cls):

        groups = (
            Group(name='Group 1'),
            Group(name='Group 2'),
            Group(name='Group 3'),
        )
        Group.objects.bulk_create(groups)

        users = (
            User(username='User1', is_active=True),
            User(username='User2', is_active=True),
            User(username='User3', is_active=True),
        )
        User.objects.bulk_create(users)

        object_type = ObjectType.objects.get(app_label='dcim', model='device')

        for i in range(3):
            objectpermission = ObjectPermission(
                name=f'Permission {i + 1}',
                actions=['view', 'add', 'change', 'delete'],
                constraints={'name': f'TEST{i + 1}'}
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
