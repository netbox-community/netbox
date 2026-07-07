import datetime
from unittest.mock import MagicMock

from django.conf import settings
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import Client, RequestFactory, SimpleTestCase
from django.test.utils import override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from social_core.exceptions import AuthFailed

from core.choices import ManagedFileRootPathChoices
from core.models import ManagedFile, ObjectType
from dcim.models import Rack, Site
from extras.models import ScriptModule
from netbox.authentication.misc import _mirror_groups
from netbox.middleware import SocialAuthExceptionMiddleware
from users.constants import TOKEN_PREFIX
from users.models import Group, ObjectPermission, Token, User
from utilities.testing import TestCase
from utilities.testing.api import APITestCase


class TokenAuthenticationTestCase(APITestCase):

    @override_settings(LOGIN_REQUIRED=True, EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_no_token(self):
        # Request without a token should return a 403
        response = self.client.get(reverse('dcim-api:site-list'))
        self.assertEqual(response.status_code, 403)

    @override_settings(LOGIN_REQUIRED=True, EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_v1_token_valid(self):
        # Create a v1 token
        token = Token.objects.create(version=1, user=self.user)

        # Valid token should return a 200
        header = f'Token {token.token}'
        response = self.client.get(reverse('dcim-api:site-list'), HTTP_AUTHORIZATION=header)
        self.assertEqual(response.status_code, 200, response.data)

        # Check that the token's last_used time has been updated
        token.refresh_from_db()
        self.assertIsNotNone(token.last_used)

    @override_settings(LOGIN_REQUIRED=True, EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_v1_token_invalid(self):
        # Invalid token should return a 403
        header = 'Token XXXXXXXXXX'
        response = self.client.get(reverse('dcim-api:site-list'), HTTP_AUTHORIZATION=header)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], "Invalid v1 token")

    @override_settings(LOGIN_REQUIRED=True, EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_v2_token_valid(self):
        # Create a v2 token
        token = Token.objects.create(version=2, user=self.user)

        # Valid token should return a 200
        header = f'Bearer {TOKEN_PREFIX}{token.key}.{token.token}'
        response = self.client.get(reverse('dcim-api:site-list'), HTTP_AUTHORIZATION=header)
        self.assertEqual(response.status_code, 200, response.data)

        # Check that the token's last_used time has been updated
        token.refresh_from_db()
        self.assertIsNotNone(token.last_used)

    @override_settings(LOGIN_REQUIRED=True, EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_v2_token_invalid(self):
        # Invalid token should return a 403
        header = f'Bearer {TOKEN_PREFIX}XXXXXX.XXXXXXXXXX'
        response = self.client.get(reverse('dcim-api:site-list'), HTTP_AUTHORIZATION=header)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], "Invalid v2 token")

    @override_settings(LOGIN_REQUIRED=True, EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_token_enabled(self):
        url = reverse('dcim-api:site-list')

        # Create v1 & v2 tokens
        token1 = Token.objects.create(version=1, user=self.user, enabled=True)
        token2 = Token.objects.create(version=2, user=self.user, enabled=True)

        # Request with an enabled token should succeed
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Token {token1.token}')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {TOKEN_PREFIX}{token2.key}.{token2.token}')
        self.assertEqual(response.status_code, 200)

        # Request with a disabled token should fail
        token1.enabled = False
        token1.save()
        token2.enabled = False
        token2.save()
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Token {token1.token}')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], 'Token disabled')
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {TOKEN_PREFIX}{token2.key}.{token2.token}')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], 'Token disabled')

    @override_settings(LOGIN_REQUIRED=True, EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_token_expiration(self):
        url = reverse('dcim-api:site-list')

        # Create v1 & v2 tokens
        future = datetime.datetime(2100, 1, 1, tzinfo=datetime.UTC)
        token1 = Token.objects.create(version=1, user=self.user, expires=future)
        token2 = Token.objects.create(version=2, user=self.user, expires=future)

        # Request with a non-expired token should succeed
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Token {token1.token}')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {TOKEN_PREFIX}{token2.key}.{token2.token}')
        self.assertEqual(response.status_code, 200)

        # Request with an expired token should fail
        past = datetime.datetime(2020, 1, 1, tzinfo=datetime.UTC)
        token1.expires = past
        token1.save()
        token2.expires = past
        token2.save()
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Token {token1.key}')
        self.assertEqual(response.status_code, 403)
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {TOKEN_PREFIX}{token2.key}')
        self.assertEqual(response.status_code, 403)

    @override_settings(LOGIN_REQUIRED=True, EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_token_write_enabled(self):
        url = reverse('dcim-api:site-list')
        data = [
            {
                'name': 'Site 1',
                'slug': 'site-1',
            },
            {
                'name': 'Site 2',
                'slug': 'site-2',
            },
        ]
        self.add_permissions('dcim.view_site', 'dcim.add_site')

        # Create v1 & v2 tokens
        token1 = Token.objects.create(version=1, user=self.user, write_enabled=False)
        token2 = Token.objects.create(version=2, user=self.user, write_enabled=False)

        token1_header = f'Token {token1.token}'
        token2_header = f'Bearer {TOKEN_PREFIX}{token2.key}.{token2.token}'

        # GET request with a write-disabled token should succeed
        response = self.client.get(url, HTTP_AUTHORIZATION=token1_header)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(url, HTTP_AUTHORIZATION=token2_header)
        self.assertEqual(response.status_code, 200)

        # POST request with a write-disabled token should fail
        response = self.client.post(url, data[0], format='json', HTTP_AUTHORIZATION=token1_header)
        self.assertEqual(response.status_code, 403)
        response = self.client.post(url, data[1], format='json', HTTP_AUTHORIZATION=token2_header)
        self.assertEqual(response.status_code, 403)

        # POST request with a write-enabled token should succeed
        token1.write_enabled = True
        token1.save()
        token2.write_enabled = True
        token2.save()
        response = self.client.post(url, data[0], format='json', HTTP_AUTHORIZATION=token1_header)
        self.assertEqual(response.status_code, 201)
        response = self.client.post(url, data[1], format='json', HTTP_AUTHORIZATION=token2_header)
        self.assertEqual(response.status_code, 201)

    @override_settings(LOGIN_REQUIRED=True, EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_token_allowed_ips(self):
        url = reverse('dcim-api:site-list')

        # Create v1 & v2 tokens
        token1 = Token.objects.create(version=1, user=self.user, allowed_ips=['192.0.2.0/24'])
        token2 = Token.objects.create(version=2, user=self.user, allowed_ips=['192.0.2.0/24'])

        # Request from a non-allowed client IP should fail
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=f'Token {token1.token}',
            REMOTE_ADDR='127.0.0.1'
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=f'Bearer {TOKEN_PREFIX}{token2.key}.{token2.token}',
            REMOTE_ADDR='127.0.0.1'
        )
        self.assertEqual(response.status_code, 403)

        # Request from an allowed client IP should succeed
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=f'Token {token1.token}',
            REMOTE_ADDR='192.0.2.1'
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=f'Bearer {TOKEN_PREFIX}{token2.key}.{token2.token}',
            REMOTE_ADDR='192.0.2.1'
        )
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
        self.client.get(reverse('home'), follow=True, **headers)
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
        REMOTE_AUTH_AUTO_CREATE_GROUPS=True,
        LOGIN_REQUIRED=True,
    )
    def test_remote_auth_remote_groups_autocreate(self):
        """
        Test enabling remote authentication with group sync and autocreate
        enabled with the default configuration.
        """
        headers = {
            "HTTP_REMOTE_USER": "remoteuser2",
            "HTTP_REMOTE_USER_GROUP": "Group 1|Group 2",
        }

        self.assertTrue(settings.REMOTE_AUTH_ENABLED)
        self.assertTrue(settings.REMOTE_AUTH_AUTO_CREATE_USER)
        self.assertTrue(settings.REMOTE_AUTH_AUTO_CREATE_GROUPS)
        self.assertTrue(settings.REMOTE_AUTH_GROUP_SYNC_ENABLED)
        self.assertEqual(settings.REMOTE_AUTH_HEADER, "HTTP_REMOTE_USER")
        self.assertEqual(settings.REMOTE_AUTH_GROUP_HEADER, "HTTP_REMOTE_USER_GROUP")
        self.assertEqual(settings.REMOTE_AUTH_GROUP_SEPARATOR, "|")

        groups = (
            Group(name="Group 1"),
            Group(name="Group 2"),
        )

        response = self.client.get(reverse("home"), follow=True, **headers)
        self.assertEqual(response.status_code, 200)

        new_user = User.objects.get(username="remoteuser2")
        self.assertEqual(
            int(self.client.session.get("_auth_user_id")),
            new_user.pk,
            msg="Authentication failed",
        )
        self.assertListEqual(
            [group.name for group in groups],
            [group.name for group in list(new_user.groups.all())],
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


class LDAPMirrorGroupsTestCase(TestCase):
    """
    Test the custom _mirror_groups() patched onto django-auth-ldap's _LDAPUser.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='ldapuser')
        Group.objects.create(name='Group 1')

    def _build_ldap_user(self, group_names):
        """
        Construct a mock _LDAPUser whose LDAP group search returns the given names.
        """
        ldap_user = MagicMock()
        ldap_user._user = self.user
        ldap_user._get_groups.return_value.get_group_names.return_value = group_names
        # Disable allow/deny list handling
        ldap_user.settings.MIRROR_GROUPS_EXCEPT = None
        ldap_user.settings.MIRROR_GROUPS = None
        return ldap_user

    def test_mirror_groups_ignores_empty_names(self):
        """
        An LDAP group search returning an empty or null name must not attempt to
        create a Group with a null name (see #21310).
        """
        ldap_user = self._build_ldap_user({'Group 1', '', None})

        _mirror_groups(ldap_user)

        # No group with a null or empty name should have been created
        self.assertFalse(Group.objects.filter(name__isnull=True).exists())
        self.assertFalse(Group.objects.filter(name='').exists())
        # The user should be mirrored into the one valid, matching group
        self.assertListEqual(
            ['Group 1'],
            list(self.user.groups.values_list('name', flat=True))
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

        cls.racks = (
            Rack(name='Rack 1', site=cls.sites[0]),
            Rack(name='Rack 2', site=cls.sites[0]),
            Rack(name='Rack 3', site=cls.sites[0]),
            Rack(name='Rack 4', site=cls.sites[1]),
            Rack(name='Rack 5', site=cls.sites[1]),
            Rack(name='Rack 6', site=cls.sites[1]),
            Rack(name='Rack 7', site=cls.sites[2]),
            Rack(name='Rack 8', site=cls.sites[2]),
            Rack(name='Rack 9', site=cls.sites[2]),
        )
        Rack.objects.bulk_create(cls.racks)

    def setUp(self):
        """
        Create a test user and token for API calls.
        """
        self.user = User.objects.create(username='testuser')
        self.token = Token.objects.create(user=self.user)
        self.header = {'HTTP_AUTHORIZATION': f'Bearer {TOKEN_PREFIX}{self.token.key}.{self.token.token}'}

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_get_object(self):

        # Attempt to retrieve object without permission
        url = reverse('dcim-api:rack-detail', kwargs={'pk': self.racks[0].pk})
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
        obj_perm.object_types.add(ObjectType.objects.get_for_model(Rack))

        # Retrieve permitted object
        url = reverse('dcim-api:rack-detail', kwargs={'pk': self.racks[0].pk})
        response = self.client.get(url, **self.header)
        self.assertEqual(response.status_code, 200)

        # Attempt to retrieve non-permitted object
        url = reverse('dcim-api:rack-detail', kwargs={'pk': self.racks[3].pk})
        response = self.client.get(url, **self.header)
        self.assertEqual(response.status_code, 404)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_list_objects(self):
        url = reverse('dcim-api:rack-list')

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
        obj_perm.object_types.add(ObjectType.objects.get_for_model(Rack))

        # Retrieve all objects. Only permitted objects should be returned.
        response = self.client.get(url, **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 3)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_create_object(self):
        url = reverse('dcim-api:rack-list')
        data = {
            'name': 'Rack 10',
            'site': self.sites[1].pk,
        }
        initial_count = Rack.objects.count()

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
        obj_perm.object_types.add(ObjectType.objects.get_for_model(Rack))

        # Attempt to create a non-permitted object
        response = self.client.post(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Rack.objects.count(), initial_count)

        # Create a permitted object
        data['site'] = self.sites[0].pk
        response = self.client.post(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Rack.objects.count(), initial_count + 1)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_edit_object(self):

        # Attempt to edit an object without permission
        data = {'site': self.sites[0].pk}
        url = reverse('dcim-api:rack-detail', kwargs={'pk': self.racks[0].pk})
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
        obj_perm.object_types.add(ObjectType.objects.get_for_model(Rack))

        # Attempt to edit a non-permitted object
        data = {'site': self.sites[0].pk}
        url = reverse('dcim-api:rack-detail', kwargs={'pk': self.racks[3].pk})
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 404)

        # Edit a permitted object
        data['status'] = 'reserved'
        url = reverse('dcim-api:rack-detail', kwargs={'pk': self.racks[0].pk})
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 200)

        # Attempt to modify a permitted object to a non-permitted object
        data['site'] = self.sites[1].pk
        url = reverse('dcim-api:rack-detail', kwargs={'pk': self.racks[0].pk})
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 403)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_delete_object(self):

        # Attempt to delete an object without permission
        url = reverse('dcim-api:rack-detail', kwargs={'pk': self.racks[0].pk})
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
        obj_perm.object_types.add(ObjectType.objects.get_for_model(Rack))

        # Attempt to delete a non-permitted object
        url = reverse('dcim-api:rack-detail', kwargs={'pk': self.racks[3].pk})
        response = self.client.delete(url, format='json', **self.header)
        self.assertEqual(response.status_code, 404)

        # Delete a permitted object
        url = reverse('dcim-api:rack-detail', kwargs={'pk': self.racks[0].pk})
        response = self.client.delete(url, format='json', **self.header)
        self.assertEqual(response.status_code, 204)


class ObjectPermissionProxyModelTestCase(TestCase):
    """
    Object-level permission checks against proxy models (e.g. extras.ScriptModule proxying
    core.ManagedFile) must evaluate the permission rather than raise ValueError.
    """
    @classmethod
    def setUpTestData(cls):
        cls.managed_file = ManagedFile.objects.create(
            file_root=ManagedFileRootPathChoices.SCRIPTS,
            file_path='proxy_permission_test.py'
        )
        cls.script_module = ScriptModule.objects.get(pk=cls.managed_file.pk)

    def _grant_scriptmodule_permission(self, constraints=None):
        obj_perm = ObjectPermission(name='ScriptModule change', actions=['change'], constraints=constraints)
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(ScriptModule, for_concrete_model=False))

    def test_has_perm_cross_app_proxy_model(self):
        """An unconstrained proxy-model permission grants access to a proxy instance."""
        self._grant_scriptmodule_permission()
        self.assertTrue(self.user.has_perm('extras.change_scriptmodule', self.script_module))

    def test_has_perm_cross_app_proxy_model_matching_constraints(self):
        """A constrained proxy-model permission grants access when the instance matches."""
        self._grant_scriptmodule_permission(constraints={'file_path': 'proxy_permission_test.py'})
        self.assertTrue(self.user.has_perm('extras.change_scriptmodule', self.script_module))

    def test_has_perm_cross_app_proxy_model_nonmatching_constraints(self):
        """A constrained proxy-model permission denies access when the instance does not match."""
        self._grant_scriptmodule_permission(constraints={'file_path': 'other.py'})
        self.assertFalse(self.user.has_perm('extras.change_scriptmodule', self.script_module))

    def test_has_perm_invalid_permission_object_pair(self):
        """A permission checked against an object of an unrelated model denies instead of raising."""
        site = Site.objects.create(name='Proxy Test Site', slug='proxy-test-site')
        self._grant_scriptmodule_permission()
        self.assertFalse(self.user.has_perm('extras.change_scriptmodule', site))

    @override_settings(DEFAULT_PERMISSIONS={'extras.change_nosuchmodel': None})
    def test_has_perm_unknown_model_permission(self):
        """A permission naming a nonexistent model denies and logs a warning instead of raising."""
        self._grant_scriptmodule_permission()
        with self.assertLogs('netbox.auth.ObjectPermissionBackend', level='WARNING'):
            self.assertFalse(self.user.has_perm('extras.change_nosuchmodel', self.script_module))


class SocialAuthExceptionMiddlewareTestCase(SimpleTestCase):
    """
    Verify that SSO/SAML authentication failures are surfaced as a login-page message rather than
    bubbling up as an HTTP 500 (see #22346).
    """
    GENERIC_MESSAGE = "Single sign-on failed. Please try again or contact your administrator."

    class FakeStrategy:
        # Mirror social_core's DjangoStrategy.setting(), which reads SOCIAL_AUTH_<NAME> from Django
        # settings. This ensures the test exercises the real configured values (e.g.
        # SOCIAL_AUTH_LOGIN_ERROR_URL) rather than hardcoded stand-ins.
        def setting(self, name, default=None, backend=None):
            return getattr(settings, f'SOCIAL_AUTH_{name}', default)

    class FakeBackend:
        name = 'saml'

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = SocialAuthExceptionMiddleware(lambda request: None)

    def _make_request(self):
        request = self.factory.get('/')
        request.social_strategy = self.FakeStrategy()
        request.backend = self.FakeBackend()
        # Attach message storage (normally provided by MessageMiddleware)
        setattr(request, 'session', {})
        request._messages = FallbackStorage(request)
        return request

    def test_generic_message(self):
        """
        The raw exception text should never be surfaced to the user.
        """
        request = self._make_request()
        exception = AuthFailed(self.FakeBackend(), 'raw internal SAML detail')
        self.assertEqual(self.middleware.get_message(request, exception), self.GENERIC_MESSAGE)

    def test_redirect_on_failure(self):
        """
        A SocialAuthBaseException should redirect to the login page with the generic message set.
        """
        request = self._make_request()
        exception = AuthFailed(self.FakeBackend(), 'raw internal SAML detail')
        response = self.middleware.process_exception(request, exception)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, settings.SOCIAL_AUTH_LOGIN_ERROR_URL)
        self.assertEqual(response.url, settings.LOGIN_URL)
        messages = [str(m) for m in request._messages]
        self.assertEqual(messages, [self.GENERIC_MESSAGE])
