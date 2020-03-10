from django.contrib.auth.models import Group, Permission, User
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse


class ExternalAuthenticationTestCase(TestCase):

    @override_settings(
        REMOTE_AUTH_ENABLED=True,
        LOGIN_REQUIRED=True
    )
    def test_remote_auth(self):
        """
        Test enabling remote authentication with the default configuration.
        """
        headers = {
            'HTTP_REMOTE_USER': 'remoteuser1',
        }

        self.client = Client()
        response = self.client.get(reverse('home'), follow=True, **headers)
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(username='remoteuser1')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk, msg='Authentication failed')

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

        self.client = Client()
        response = self.client.get(reverse('home'), follow=True, **headers)
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(username='remoteuser1')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk, msg='Authentication failed')

    @override_settings(
        REMOTE_AUTH_ENABLED=True,
        REMOTE_AUTH_AUTO_CREATE_USER=False,
        LOGIN_REQUIRED=True
    )
    def test_remote_auth_no_auto_create(self):
        """
        Test enabling remote authentication with automatic user creation disabled.
        """
        headers = {
            'HTTP_REMOTE_USER': 'remoteuser1',
        }

        self.client = Client()

        # First attempt should fail as the user does not exist
        self.client.get(reverse('home'), **headers)
        self.assertNotIn('_auth_user_id', self.client.session)

        # Create the user locally and try again
        user = User.objects.create(username='remoteuser1')
        response = self.client.get(reverse('home'), follow=True, **headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk, msg='Authentication failed')

    @override_settings(
        REMOTE_AUTH_ENABLED=True,
        REMOTE_AUTH_DEFAULT_GROUPS=['Group 1', 'Group 2'],
        LOGIN_REQUIRED=True
    )
    def test_remote_auth_default_groups(self):
        """
        Test enabling remote authentication with the default configuration.
        """
        headers = {
            'HTTP_REMOTE_USER': 'remoteuser1',
        }

        # Create required groups
        groups = (
            Group(name='Group 1'),
            Group(name='Group 2'),
            Group(name='Group 3'),
        )
        Group.objects.bulk_create(groups)

        self.client = Client()
        response = self.client.get(reverse('home'), follow=True, **headers)
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(username='remoteuser1')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk, msg='Authentication failed')
        self.assertListEqual(
            [groups[0], groups[1]],
            list(user.groups.all())
        )

    @override_settings(
        REMOTE_AUTH_ENABLED=True,
        REMOTE_AUTH_DEFAULT_PERMISSIONS=['dcim.add_site', 'dcim.change_site'],
        LOGIN_REQUIRED=True
    )
    def test_remote_auth_default_permissions(self):
        """
        Test enabling remote authentication with the default configuration.
        """
        headers = {
            'HTTP_REMOTE_USER': 'remoteuser1',
        }

        self.client = Client()
        response = self.client.get(reverse('home'), follow=True, **headers)
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(username='remoteuser1')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk, msg='Authentication failed')
        self.assertTrue(user.has_perms(['dcim.add_site', 'dcim.change_site']))
