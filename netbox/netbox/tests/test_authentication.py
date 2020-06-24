from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.test import Client
from django.test.utils import override_settings
from django.urls import reverse
from netaddr import IPNetwork
from rest_framework.test import APIClient

from dcim.models import Site
from ipam.choices import PrefixStatusChoices
from ipam.models import Prefix
from users.models import ObjectPermission, Token
from utilities.testing import TestCase


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
        self.assertEqual(int(self.client.session.get('_auth_user_id')), self.user.pk, msg='Authentication failed')

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
        self.assertEqual(int(self.client.session.get('_auth_user_id')), self.user.pk, msg='Authentication failed')

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
        self.assertEqual(int(self.client.session.get('_auth_user_id')), new_user.pk, msg='Authentication failed')

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
        self.assertEqual(settings.REMOTE_AUTH_DEFAULT_GROUPS, ['Group 1', 'Group 2'])

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
        self.assertEqual(int(self.client.session.get('_auth_user_id')), new_user.pk, msg='Authentication failed')
        self.assertListEqual(
            [groups[0], groups[1]],
            list(new_user.groups.all())
        )

    @override_settings(
        REMOTE_AUTH_ENABLED=True,
        REMOTE_AUTH_AUTO_CREATE_USER=True,
        REMOTE_AUTH_DEFAULT_PERMISSIONS={'dcim.add_site': None, 'dcim.change_site': None},
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
        self.assertEqual(settings.REMOTE_AUTH_DEFAULT_PERMISSIONS, {'dcim.add_site': None, 'dcim.change_site': None})

        response = self.client.get(reverse('home'), follow=True, **headers)
        self.assertEqual(response.status_code, 200)

        new_user = User.objects.get(username='remoteuser2')
        self.assertEqual(int(self.client.session.get('_auth_user_id')), new_user.pk, msg='Authentication failed')
        self.assertTrue(new_user.has_perms(['dcim.add_site', 'dcim.change_site']))


class ObjectPermissionViewTestCase(TestCase):

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

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_get_object(self):

        # Attempt to retrieve object without permission
        response = self.client.get(self.prefixes[0].get_absolute_url())
        self.assertHttpStatus(response, 403)

        # Assign object permission
        obj_perm = ObjectPermission(
            constraints={'site__name': 'Site 1'},
            actions=['view']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(Prefix))

        # Retrieve permitted object
        response = self.client.get(self.prefixes[0].get_absolute_url())
        self.assertHttpStatus(response, 200)

        # Attempt to retrieve non-permitted object
        response = self.client.get(self.prefixes[3].get_absolute_url())
        self.assertHttpStatus(response, 404)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_list_objects(self):

        # Attempt to list objects without permission
        response = self.client.get(reverse('ipam:prefix_list'))
        self.assertHttpStatus(response, 403)

        # Assign object permission
        obj_perm = ObjectPermission(
            constraints={'site__name': 'Site 1'},
            actions=['view']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(Prefix))

        # Retrieve all objects. Only permitted objects should be returned.
        response = self.client.get(reverse('ipam:prefix_list'))
        self.assertHttpStatus(response, 200)
        self.assertIn(str(self.prefixes[0].prefix), str(response.content))
        self.assertNotIn(str(self.prefixes[3].prefix), str(response.content))

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_create_object(self):
        initial_count = Prefix.objects.count()
        form_data = {
            'prefix': '10.0.9.0/24',
            'site': self.sites[1].pk,
            'status': PrefixStatusChoices.STATUS_ACTIVE,
        }

        # Attempt to create an object without permission
        request = {
            'path': reverse('ipam:prefix_add'),
            'data': form_data,
            'follow': False,  # Do not follow 302 redirects
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 403)
        self.assertEqual(initial_count, Prefix.objects.count())

        # Assign object permission
        obj_perm = ObjectPermission(
            constraints={'site__name': 'Site 1'},
            actions=['view', 'add']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(Prefix))

        # Attempt to create a non-permitted object
        request = {
            'path': reverse('ipam:prefix_add'),
            'data': form_data,
            'follow': True,  # Follow 302 redirects
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 200)
        self.assertEqual(Prefix.objects.count(), initial_count)

        # Create a permitted object
        form_data['site'] = self.sites[0].pk
        request = {
            'path': reverse('ipam:prefix_add'),
            'data': form_data,
            'follow': True,  # Follow 302 redirects
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 200)
        self.assertEqual(Prefix.objects.count(), initial_count + 1)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_edit_object(self):
        form_data = {
            'prefix': '10.0.9.0/24',
            'site': self.sites[0].pk,
            'status': PrefixStatusChoices.STATUS_RESERVED,
        }

        # Attempt to edit an object without permission
        request = {
            'path': reverse('ipam:prefix_edit', kwargs={'pk': self.prefixes[0].pk}),
            'data': form_data,
            'follow': False,  # Do not follow 302 redirects
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 403)

        # Assign object permission
        obj_perm = ObjectPermission(
            constraints={'site__name': 'Site 1'},
            actions=['view', 'change']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(Prefix))

        # Attempt to edit a non-permitted object
        request = {
            'path': reverse('ipam:prefix_edit', kwargs={'pk': self.prefixes[3].pk}),
            'data': form_data,
            'follow': True,  # Follow 302 redirects
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 404)

        # Edit a permitted object
        request = {
            'path': reverse('ipam:prefix_edit', kwargs={'pk': self.prefixes[0].pk}),
            'data': form_data,
            'follow': True,  # Follow 302 redirects
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 200)
        prefix = Prefix.objects.get(pk=self.prefixes[0].pk)
        self.assertEqual(prefix.status, PrefixStatusChoices.STATUS_RESERVED)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_delete_object(self):
        form_data = {
            'confirm': True
        }

        # Attempt to delete object without permission
        request = {
            'path': reverse('ipam:prefix_delete', kwargs={'pk': self.prefixes[0].pk}),
            'data': form_data,
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 403)

        # Assign object permission
        obj_perm = ObjectPermission(
            constraints={'site__name': 'Site 1'},
            actions=['view', 'delete']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(Prefix))

        # Delete permitted object
        request = {
            'path': reverse('ipam:prefix_delete', kwargs={'pk': self.prefixes[0].pk}),
            'data': form_data,
            'follow': True,  # Follow 302 redirects
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 200)
        self.assertFalse(Prefix.objects.filter(pk=self.prefixes[0].pk).exists())

        # Attempt to delete non-permitted object
        request = {
            'path': reverse('ipam:prefix_delete', kwargs={'pk': self.prefixes[3].pk}),
            'data': form_data,
            'follow': True,  # Follow 302 redirects
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 404)
        self.assertTrue(Prefix.objects.filter(pk=self.prefixes[3].pk).exists())

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_bulk_import_objects(self):
        initial_count = Prefix.objects.count()
        form_data = {
            'csv': "prefix,status,site\n"
                   "10.0.9.0/24,Active,Site 1\n"
                   "10.0.10.0/24,Active,Site 2\n"
                   "10.0.11.0/24,Active,Site 3\n",
        }

        # Attempt to import objects without permission
        request = {
            'path': reverse('ipam:prefix_import'),
            'data': form_data,
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 403)
        self.assertEqual(initial_count, Prefix.objects.count())

        # Assign object permission
        obj_perm = ObjectPermission(
            constraints={'site__name': 'Site 1'},
            actions=['add']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(Prefix))

        # Attempt to create non-permitted objects
        request = {
            'path': reverse('ipam:prefix_import'),
            'data': form_data,
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 200)
        self.assertEqual(Prefix.objects.count(), initial_count)

        # Create a permitted object
        form_data = {
            'csv': "prefix,status,site\n"
                   "10.0.9.0/24,Active,Site 1\n"
                   "10.0.10.0/24,Active,Site 1\n"
                   "10.0.11.0/24,Active,Site 1\n",
        }
        request = {
            'path': reverse('ipam:prefix_import'),
            'data': form_data,
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 200)
        self.assertEqual(Prefix.objects.count(), initial_count + 3)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_bulk_edit_objects(self):
        form_data = {
            'pk': [p.pk for p in self.prefixes],
            'status': 'reserved',
            '_apply': True,
        }

        # Attempt to edit objects without permission
        request = {
            'path': reverse('ipam:prefix_bulk_edit'),
            'data': form_data,
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 403)

        # Assign object permission
        obj_perm = ObjectPermission(
            constraints={'site__name': 'Site 1'},
            actions=['change']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(Prefix))

        # Attempt to edit non-permitted objects
        request = {
            'path': reverse('ipam:prefix_bulk_edit'),
            'data': form_data,
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 302)
        self.assertEqual(Prefix.objects.get(pk=self.prefixes[3].pk).status, 'active')

        # Edit permitted objects
        form_data['pk'] = [p.pk for p in self.prefixes[:3]]
        request = {
            'path': reverse('ipam:prefix_bulk_edit'),
            'data': form_data,
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 302)
        self.assertEqual(Prefix.objects.get(pk=self.prefixes[0].pk).status, 'reserved')

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_bulk_delete_objects(self):
        form_data = {
            'pk': [p.pk for p in self.prefixes],
            'confirm': True,
            '_confirm': True,
        }

        # Attempt to delete objects without permission
        request = {
            'path': reverse('ipam:prefix_bulk_delete'),
            'data': form_data,
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 403)

        # Assign object permission
        obj_perm = ObjectPermission(
            constraints={'site__name': 'Site 1'},
            actions=['view', 'delete']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(Prefix))

        # Attempt to delete non-permitted object
        request = {
            'path': reverse('ipam:prefix_bulk_delete'),
            'data': form_data,
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 200)
        self.assertTrue(Prefix.objects.filter(pk=self.prefixes[3].pk).exists())

        # Delete permitted objects
        form_data['pk'] = [p.pk for p in self.prefixes[:3]]
        request = {
            'path': reverse('ipam:prefix_bulk_delete'),
            'data': form_data,
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 302)
        self.assertFalse(Prefix.objects.filter(pk=self.prefixes[0].pk).exists())


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
        url = reverse('ipam-api:prefix-detail', kwargs={'pk': self.prefixes[0].pk})
        response = self.client.get(url, **self.header)
        self.assertEqual(response.status_code, 403)

        # Assign object permission
        obj_perm = ObjectPermission(
            constraints={'site__name': 'Site 1'},
            actions=['view']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(Prefix))

        # Retrieve permitted object
        url = reverse('ipam-api:prefix-detail', kwargs={'pk': self.prefixes[0].pk})
        response = self.client.get(url, **self.header)
        self.assertEqual(response.status_code, 200)

        # Attempt to retrieve non-permitted object
        url = reverse('ipam-api:prefix-detail', kwargs={'pk': self.prefixes[3].pk})
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
        url = reverse('ipam-api:prefix-detail', kwargs={'pk': self.prefixes[0].pk})
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 403)

        # Assign object permission
        obj_perm = ObjectPermission(
            constraints={'site__name': 'Site 1'},
            actions=['change']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(Prefix))

        # Attempt to edit a non-permitted object
        data = {'site': self.sites[0].pk}
        url = reverse('ipam-api:prefix-detail', kwargs={'pk': self.prefixes[3].pk})
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 404)

        # Edit a permitted object
        data['status'] = 'reserved'
        url = reverse('ipam-api:prefix-detail', kwargs={'pk': self.prefixes[0].pk})
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 200)

        # Attempt to modify a permitted object to a non-permitted object
        data['site'] = self.sites[1].pk
        url = reverse('ipam-api:prefix-detail', kwargs={'pk': self.prefixes[0].pk})
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 403)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_delete_object(self):

        # Attempt to delete an object without permission
        url = reverse('ipam-api:prefix-detail', kwargs={'pk': self.prefixes[0].pk})
        response = self.client.delete(url, format='json', **self.header)
        self.assertEqual(response.status_code, 403)

        # Assign object permission
        obj_perm = ObjectPermission(
            constraints={'site__name': 'Site 1'},
            actions=['delete']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(Prefix))

        # Attempt to delete a non-permitted object
        url = reverse('ipam-api:prefix-detail', kwargs={'pk': self.prefixes[3].pk})
        response = self.client.delete(url, format='json', **self.header)
        self.assertEqual(response.status_code, 404)

        # Delete a permitted object
        url = reverse('ipam-api:prefix-detail', kwargs={'pk': self.prefixes[0].pk})
        response = self.client.delete(url, format='json', **self.header)
        self.assertEqual(response.status_code, 204)
