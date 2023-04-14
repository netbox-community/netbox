import datetime

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.test import Client
from django.test.utils import override_settings
from django.urls import reverse
from netaddr import IPNetwork
from rest_framework.test import APIClient

from dcim.models import Site
from ipam.models import Prefix
from users.models import ObjectPermission, Token
from utilities.testing import TestCase
from utilities.testing.api import APITestCase


class TokenAuthenticationTestCase(APITestCase):

    @override_settings(LOGIN_REQUIRED=True, EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_token_authentication(self):
        url = reverse('dcim-api:site-list')

        # Request without a token should return a 403
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # Valid token should return a 200
        token = Token.objects.create(user=self.user)
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertEqual(response.status_code, 200)

        # Check that the token's last_used time has been updated
        token.refresh_from_db()
        self.assertIsNotNone(token.last_used)

    @override_settings(LOGIN_REQUIRED=True, EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_token_expiration(self):
        url = reverse('dcim-api:site-list')

        # Request without a non-expired token should succeed
        token = Token.objects.create(user=self.user)
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertEqual(response.status_code, 200)

        # Request with an expired token should fail
        token.expires = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)
        token.save()
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertEqual(response.status_code, 403)

    @override_settings(LOGIN_REQUIRED=True, EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_token_write_enabled(self):
        url = reverse('dcim-api:site-list')
        data = {
            'name': 'Site 1',
            'slug': 'site-1',
        }

        # Request with a write-disabled token should fail
        token = Token.objects.create(user=self.user, write_enabled=False)
        response = self.client.post(url, data, format='json', HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertEqual(response.status_code, 403)

        # Request with a write-enabled token should succeed
        token.write_enabled = True
        token.save()
        response = self.client.post(url, data, format='json', HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertEqual(response.status_code, 403)

    @override_settings(LOGIN_REQUIRED=True, EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_token_allowed_ips(self):
        url = reverse('dcim-api:site-list')

        # Request from a non-allowed client IP should fail
        token = Token.objects.create(user=self.user, allowed_ips=['192.0.2.0/24'])
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Token {token.key}', REMOTE_ADDR='127.0.0.1')
        self.assertEqual(response.status_code, 403)

        # Request with an expired token should fail
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Token {token.key}', REMOTE_ADDR='192.0.2.1')
        self.assertEqual(response.status_code, 200)


class ExternalAuthenticationTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='remoteuser1')

    def setUp(self):
        self.client = Client()

    @override_settings(
        LOGIN_REQUIRED=True
    )
    def test_remote_auth_disabled(self):
        """
        Test enabling remote authentication with the default configuration.
        """
        headers = {
            'HTTP_REMOTE_USER': 'remoteuser1',
        }

        self.assertFalse(settings.REMOTE_AUTH_ENABLED)
        self.assertEqual(settings.REMOTE_AUTH_HEADER, 'HTTP_REMOTE_USER')

        # Client should not be authenticated
        response = self.client.get(reverse('home'), follow=True, **headers)
        self.assertNotIn('_auth_user_id', self.client.session)

    @override_settings(
        REMOTE_AUTH_ENABLED=True,
        LOGIN_REQUIRED=True
    )
    def test_remote_auth_enabled(self):
        """
        Test enabling remote authentication with the default configuration.
        """
        headers = {
            'HTTP_REMOTE_USER': 'remoteuser1',
        }

        self.assertTrue(settings.REMOTE_AUTH_ENABLED)
        self.assertEqual(settings.REMOTE_AUTH_HEADER, 'HTTP_REMOTE_USER')

        response = self.client.get(reverse('home'), follow=True, **headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(self.client.session.get(
            '_auth_user_id')), self.user.pk, msg='Authentication failed')

    @override_settings(
        REMOTE_AUTH_ENABLED=True,
        REMOTE_AUTH_HEADER='HTTP_FOO',
        LOGIN_REQUIRED=True
    )
    def test_remote_auth_custom_header(self):
        """
        Test enabling remote authentication with a custom HTTP header.
        """
        headers = {
            'HTTP_FOO': 'remoteuser1',
        }

        self.assertTrue(settings.REMOTE_AUTH_ENABLED)
        self.assertEqual(settings.REMOTE_AUTH_HEADER, 'HTTP_FOO')

        response = self.client.get(reverse('home'), follow=True, **headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(self.client.session.get(
            '_auth_user_id')), self.user.pk, msg='Authentication failed')

    @override_settings(
        REMOTE_AUTH_ENABLED=True,
        LOGIN_REQUIRED=True
    )
    def test_remote_auth_user_profile(self):
        """
        Test remote authentication with user profile details.
        """
        headers = {
            'HTTP_REMOTE_USER': 'remoteuser1',
            'HTTP_REMOTE_USER_FIRST_NAME': 'John',
            'HTTP_REMOTE_USER_LAST_NAME': 'Smith',
            'HTTP_REMOTE_USER_EMAIL': 'johnsmith@example.com',
        }

        response = self.client.get(reverse('home'), follow=True, **headers)
        self.assertEqual(response.status_code, 200)

        self.user = User.objects.get(username='remoteuser1')
        self.assertEqual(self.user.first_name, "John", msg='User first name was not updated')
        self.assertEqual(self.user.last_name, "Smith", msg='User last name was not updated')
        self.assertEqual(self.user.email, "johnsmith@example.com", msg='User email was not updated')

    @override_settings(
        REMOTE_AUTH_ENABLED=True,
        REMOTE_AUTH_AUTO_CREATE_USER=True,
        LOGIN_REQUIRED=True
    )
    def test_remote_auth_auto_create(self):
        """
        Test enabling remote authentication with automatic user creation disabled.
        """
        headers = {
            'HTTP_REMOTE_USER': 'remoteuser2',
        }

        self.assertTrue(settings.REMOTE_AUTH_ENABLED)
        self.assertTrue(settings.REMOTE_AUTH_AUTO_CREATE_USER)
        self.assertEqual(settings.REMOTE_AUTH_HEADER, 'HTTP_REMOTE_USER')

        response = self.client.get(reverse('home'), follow=True, **headers)
        self.assertEqual(response.status_code, 200)

        # Local user should have been automatically created
        new_user = User.objects.get(username='remoteuser2')
        self.assertEqual(int(self.client.session.get(
            '_auth_user_id')), new_user.pk, msg='Authentication failed')

    @override_settings(
        REMOTE_AUTH_ENABLED=True,
        REMOTE_AUTH_AUTO_CREATE_USER=True,
        REMOTE_AUTH_DEFAULT_GROUPS=['Group 1', 'Group 2'],
        LOGIN_REQUIRED=True
    )
    def test_remote_auth_default_groups(self):
        """
        Test enabling remote authentication with the default configuration.
        """
        headers = {
            'HTTP_REMOTE_USER': 'remoteuser2',
        }

        self.assertTrue(settings.REMOTE_AUTH_ENABLED)
        self.assertTrue(settings.REMOTE_AUTH_AUTO_CREATE_USER)
        self.assertEqual(settings.REMOTE_AUTH_HEADER, 'HTTP_REMOTE_USER')
        self.assertEqual(settings.REMOTE_AUTH_DEFAULT_GROUPS,
                         ['Group 1', 'Group 2'])

        # Create required groups
        groups = (
            Group(name='Group 1'),
            Group(name='Group 2'),
            Group(name='Group 3'),
        )
        Group.objects.bulk_create(groups)

        response = self.client.get(reverse('home'), follow=True, **headers)
        self.assertEqual(response.status_code, 200)

        new_user = User.objects.get(username='remoteuser2')
        self.assertEqual(int(self.client.session.get(
            '_auth_user_id')), new_user.pk, msg='Authentication failed')
        self.assertListEqual(
            [groups[0], groups[1]],
            list(new_user.groups.all())
        )

    @override_settings(
        REMOTE_AUTH_ENABLED=True,
        REMOTE_AUTH_AUTO_CREATE_USER=True,
        REMOTE_AUTH_DEFAULT_PERMISSIONS={
            'dcim.add_site': None, 'dcim.change_site': None},
        LOGIN_REQUIRED=True
    )
    def test_remote_auth_default_permissions(self):
        """
        Test enabling remote authentication with the default configuration.
        """
        headers = {
            'HTTP_REMOTE_USER': 'remoteuser2',
        }

        self.assertTrue(settings.REMOTE_AUTH_ENABLED)
        self.assertTrue(settings.REMOTE_AUTH_AUTO_CREATE_USER)
        self.assertEqual(settings.REMOTE_AUTH_HEADER, 'HTTP_REMOTE_USER')
        self.assertEqual(settings.REMOTE_AUTH_DEFAULT_PERMISSIONS, {
                         'dcim.add_site': None, 'dcim.change_site': None})

        response = self.client.get(reverse('home'), follow=True, **headers)
        self.assertEqual(response.status_code, 200)

        new_user = User.objects.get(username='remoteuser2')
        self.assertEqual(int(self.client.session.get(
            '_auth_user_id')), new_user.pk, msg='Authentication failed')
        self.assertTrue(new_user.has_perms(
            ['dcim.add_site', 'dcim.change_site']))

    @override_settings(
        REMOTE_AUTH_ENABLED=True,
        REMOTE_AUTH_AUTO_CREATE_USER=True,
        REMOTE_AUTH_GROUP_SYNC_ENABLED=True,
        LOGIN_REQUIRED=True
    )
    def test_remote_auth_remote_groups_default(self):
        """
        Test enabling remote authentication with group sync enabled with the default configuration.
        """
        headers = {
            'HTTP_REMOTE_USER': 'remoteuser2',
            'HTTP_REMOTE_USER_GROUP': 'Group 1|Group 2',
        }

        self.assertTrue(settings.REMOTE_AUTH_ENABLED)
        self.assertTrue(settings.REMOTE_AUTH_AUTO_CREATE_USER)
        self.assertTrue(settings.REMOTE_AUTH_GROUP_SYNC_ENABLED)
        self.assertEqual(settings.REMOTE_AUTH_HEADER, 'HTTP_REMOTE_USER')
        self.assertEqual(settings.REMOTE_AUTH_GROUP_HEADER,
                         'HTTP_REMOTE_USER_GROUP')
        self.assertEqual(settings.REMOTE_AUTH_GROUP_SEPARATOR, '|')

        # Create required groups
        groups = (
            Group(name='Group 1'),
            Group(name='Group 2'),
            Group(name='Group 3'),
        )
        Group.objects.bulk_create(groups)

        response = self.client.get(reverse('home'), follow=True, **headers)
        self.assertEqual(response.status_code, 200)

        new_user = User.objects.get(username='remoteuser2')
        self.assertEqual(int(self.client.session.get(
            '_auth_user_id')), new_user.pk, msg='Authentication failed')
        self.assertListEqual(
            [groups[0], groups[1]],
            list(new_user.groups.all())
        )

    @override_settings(
        REMOTE_AUTH_ENABLED=True,
        REMOTE_AUTH_AUTO_CREATE_USER=True,
        REMOTE_AUTH_GROUP_SYNC_ENABLED=True,
        REMOTE_AUTH_HEADER='HTTP_FOO',
        REMOTE_AUTH_GROUP_HEADER='HTTP_BAR',
        LOGIN_REQUIRED=True
    )
    def test_remote_auth_remote_groups_custom_header(self):
        """
        Test enabling remote authentication with group sync enabled with the default configuration.
        """
        headers = {
            'HTTP_FOO': 'remoteuser2',
            'HTTP_BAR': 'Group 1|Group 2',
        }

        self.assertTrue(settings.REMOTE_AUTH_ENABLED)
        self.assertTrue(settings.REMOTE_AUTH_AUTO_CREATE_USER)
        self.assertTrue(settings.REMOTE_AUTH_GROUP_SYNC_ENABLED)
        self.assertEqual(settings.REMOTE_AUTH_HEADER, 'HTTP_FOO')
        self.assertEqual(settings.REMOTE_AUTH_GROUP_HEADER, 'HTTP_BAR')
        self.assertEqual(settings.REMOTE_AUTH_GROUP_SEPARATOR, '|')

        # Create required groups
        groups = (
            Group(name='Group 1'),
            Group(name='Group 2'),
            Group(name='Group 3'),
        )
        Group.objects.bulk_create(groups)

        response = self.client.get(reverse('home'), follow=True, **headers)
        self.assertEqual(response.status_code, 200)

        new_user = User.objects.get(username='remoteuser2')
        self.assertEqual(int(self.client.session.get(
            '_auth_user_id')), new_user.pk, msg='Authentication failed')
        self.assertListEqual(
            [groups[0], groups[1]],
            list(new_user.groups.all())
        )


class ObjectPermissionAPIViewTestCase(TestCase):
    client_class = APIClient

    @classmethod
    def setUpTestData(cls):

        cls.sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(cls.sites)

        cls.prefixes = (
            Prefix(prefix=IPNetwork('10.0.0.0/24'), site=cls.sites[0]),
            Prefix(prefix=IPNetwork('10.0.1.0/24'), site=cls.sites[0]),
            Prefix(prefix=IPNetwork('10.0.2.0/24'), site=cls.sites[0]),
            Prefix(prefix=IPNetwork('10.0.3.0/24'), site=cls.sites[1]),
            Prefix(prefix=IPNetwork('10.0.4.0/24'), site=cls.sites[1]),
            Prefix(prefix=IPNetwork('10.0.5.0/24'), site=cls.sites[1]),
            Prefix(prefix=IPNetwork('10.0.6.0/24'), site=cls.sites[2]),
            Prefix(prefix=IPNetwork('10.0.7.0/24'), site=cls.sites[2]),
            Prefix(prefix=IPNetwork('10.0.8.0/24'), site=cls.sites[2]),
        )
        Prefix.objects.bulk_create(cls.prefixes)

    def setUp(self):
        """
        Create a test user and token for API calls.
        """
        self.user = User.objects.create(username='testuser')
        self.token = Token.objects.create(user=self.user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(self.token.key)}

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_get_object(self):

        # Attempt to retrieve object without permission
        url = reverse('ipam-api:prefix-detail',
                      kwargs={'pk': self.prefixes[0].pk})
        response = self.client.get(url, **self.header)
        self.assertEqual(response.status_code, 403)

        # Assign object permission
        obj_perm = ObjectPermission(
            name='Test permission',
            constraints={'site__name': 'Site 1'},
            actions=['view']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(Prefix))

        # Retrieve permitted object
        url = reverse('ipam-api:prefix-detail',
                      kwargs={'pk': self.prefixes[0].pk})
        response = self.client.get(url, **self.header)
        self.assertEqual(response.status_code, 200)

        # Attempt to retrieve non-permitted object
        url = reverse('ipam-api:prefix-detail',
                      kwargs={'pk': self.prefixes[3].pk})
        response = self.client.get(url, **self.header)
        self.assertEqual(response.status_code, 404)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_list_objects(self):
        url = reverse('ipam-api:prefix-list')

        # Attempt to list objects without permission
        response = self.client.get(url, **self.header)
        self.assertEqual(response.status_code, 403)

        # Assign object permission
        obj_perm = ObjectPermission(
            name='Test permission',
            constraints={'site__name': 'Site 1'},
            actions=['view']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(Prefix))

        # Retrieve all objects. Only permitted objects should be returned.
        response = self.client.get(url, **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 3)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_create_object(self):
        url = reverse('ipam-api:prefix-list')
        data = {
            'prefix': '10.0.9.0/24',
            'site': self.sites[1].pk,
        }
        initial_count = Prefix.objects.count()

        # Attempt to create an object without permission
        response = self.client.post(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 403)

        # Assign object permission
        obj_perm = ObjectPermission(
            name='Test permission',
            constraints={'site__name': 'Site 1'},
            actions=['add']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(Prefix))

        # Attempt to create a non-permitted object
        response = self.client.post(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Prefix.objects.count(), initial_count)

        # Create a permitted object
        data['site'] = self.sites[0].pk
        response = self.client.post(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Prefix.objects.count(), initial_count + 1)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_edit_object(self):

        # Attempt to edit an object without permission
        data = {'site': self.sites[0].pk}
        url = reverse('ipam-api:prefix-detail',
                      kwargs={'pk': self.prefixes[0].pk})
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 403)

        # Assign object permission
        obj_perm = ObjectPermission(
            name='Test permission',
            constraints={'site__name': 'Site 1'},
            actions=['change']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(Prefix))

        # Attempt to edit a non-permitted object
        data = {'site': self.sites[0].pk}
        url = reverse('ipam-api:prefix-detail',
                      kwargs={'pk': self.prefixes[3].pk})
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 404)

        # Edit a permitted object
        data['status'] = 'reserved'
        url = reverse('ipam-api:prefix-detail',
                      kwargs={'pk': self.prefixes[0].pk})
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 200)

        # Attempt to modify a permitted object to a non-permitted object
        data['site'] = self.sites[1].pk
        url = reverse('ipam-api:prefix-detail',
                      kwargs={'pk': self.prefixes[0].pk})
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 403)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_delete_object(self):

        # Attempt to delete an object without permission
        url = reverse('ipam-api:prefix-detail',
                      kwargs={'pk': self.prefixes[0].pk})
        response = self.client.delete(url, format='json', **self.header)
        self.assertEqual(response.status_code, 403)

        # Assign object permission
        obj_perm = ObjectPermission(
            name='Test permission',
            constraints={'site__name': 'Site 1'},
            actions=['delete']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(Prefix))

        # Attempt to delete a non-permitted object
        url = reverse('ipam-api:prefix-detail',
                      kwargs={'pk': self.prefixes[3].pk})
        response = self.client.delete(url, format='json', **self.header)
        self.assertEqual(response.status_code, 404)

        # Delete a permitted object
        url = reverse('ipam-api:prefix-detail',
                      kwargs={'pk': self.prefixes[0].pk})
        response = self.client.delete(url, format='json', **self.header)
        self.assertEqual(response.status_code, 204)
