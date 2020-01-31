from django.contrib.auth.models import Permission, User
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase as _TestCase, override_settings
from django.urls import reverse, NoReverseMatch
from rest_framework.test import APIClient

from users.models import Token
from .utils import disable_warnings, model_to_dict, post_data


class TestCase(_TestCase):
    user_permissions = ()

    def setUp(self):

        # Create the test user and assign permissions
        self.user = User.objects.create_user(username='testuser')
        self.add_permissions(*self.user_permissions)

        # Initialize the test client
        self.client = Client()
        self.client.force_login(self.user)

    #
    # Permissions management
    #

    def add_permissions(self, *names):
        """
        Assign a set of permissions to the test user. Accepts permission names in the form <app>.<action>_<model>.
        """
        for name in names:
            app, codename = name.split('.')
            perm = Permission.objects.get(content_type__app_label=app, codename=codename)
            self.user.user_permissions.add(perm)

    def remove_permissions(self, *names):
        """
        Remove a set of permissions from the test user, if assigned.
        """
        for name in names:
            app, codename = name.split('.')
            perm = Permission.objects.get(content_type__app_label=app, codename=codename)
            self.user.user_permissions.remove(perm)

    #
    # Convenience methods
    #

    def assertHttpStatus(self, response, expected_status):
        """
        TestCase method. Provide more detail in the event of an unexpected HTTP response.
        """
        err_message = "Expected HTTP status {}; received {}: {}"
        self.assertEqual(response.status_code, expected_status, err_message.format(
            expected_status, response.status_code, getattr(response, 'data', 'No data')
        ))


class APITestCase(TestCase):
    client_class = APIClient

    def setUp(self):
        """
        Create a superuser and token for API calls.
        """
        self.user = User.objects.create(username='testuser', is_superuser=True)
        self.token = Token.objects.create(user=self.user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(self.token.key)}


class StandardTestCases:
    """
    We keep any TestCases with test_* methods inside a class to prevent unittest from trying to run them.
    """

    class Views(TestCase):
        """
        Stock TestCase suitable for testing all standard View functions:
            - List objects
            - View single object
            - Create new object
            - Modify existing object
            - Delete existing object
            - Import multiple new objects
        """
        model = None
        form_data = {}
        csv_data = {}

        maxDiff = None

        def __init__(self, *args, **kwargs):

            super().__init__(*args, **kwargs)

            if self.model is None:
                raise Exception("Test case requires model to be defined")

        def _get_url(self, action, instance=None):
            """
            Return the URL name for a specific action. An instance must be specified for
            get/edit/delete views.
            """
            url_format = '{}:{}_{{}}'.format(
                self.model._meta.app_label,
                self.model._meta.model_name
            )

            if action in ('list', 'add', 'import'):
                return reverse(url_format.format(action))

            elif action in ('get', 'edit', 'delete'):
                if instance is None:
                    raise Exception("Resolving {} URL requires specifying an instance".format(action))
                # Attempt to resolve using slug first
                if hasattr(self.model, 'slug'):
                    try:
                        return reverse(url_format.format(action), kwargs={'slug': instance.slug})
                    except NoReverseMatch:
                        pass
                return reverse(url_format.format(action), kwargs={'pk': instance.pk})

            else:
                raise Exception("Invalid action for URL resolution: {}".format(action))

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_list_objects(self):
            # Attempt to make the request without required permissions
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.get(self._get_url('list')), 403)

            # Assign the required permission and submit again
            self.add_permissions(
                '{}.view_{}'.format(self.model._meta.app_label, self.model._meta.model_name)
            )
            response = self.client.get(self._get_url('list'))
            self.assertHttpStatus(response, 200)

            # Built-in CSV export
            if hasattr(self.model, 'csv_headers'):
                response = self.client.get('{}?export'.format(self._get_url('list')))
                self.assertHttpStatus(response, 200)
                self.assertEqual(response.get('Content-Type'), 'text/csv')

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_get_object(self):
            instance = self.model.objects.first()

            # Attempt to make the request without required permissions
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.get(instance.get_absolute_url()), 403)

            # Assign the required permission and submit again
            self.add_permissions(
                '{}.view_{}'.format(self.model._meta.app_label, self.model._meta.model_name)
            )
            response = self.client.get(instance.get_absolute_url())
            self.assertHttpStatus(response, 200)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_create_object(self):
            initial_count = self.model.objects.count()
            request = {
                'path': self._get_url('add'),
                'data': post_data(self.form_data),
                'follow': False,  # Do not follow 302 redirects
            }

            # Attempt to make the request without required permissions
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.post(**request), 403)

            # Assign the required permission and submit again
            self.add_permissions(
                '{}.add_{}'.format(self.model._meta.app_label, self.model._meta.model_name)
            )
            response = self.client.post(**request)
            self.assertHttpStatus(response, 302)

            self.assertEqual(initial_count + 1, self.model.objects.count())
            instance = self.model.objects.order_by('-pk').first()
            self.assertDictEqual(model_to_dict(instance), self.form_data)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_edit_object(self):
            instance = self.model.objects.first()

            request = {
                'path': self._get_url('edit', instance),
                'data': post_data(self.form_data),
                'follow': False,  # Do not follow 302 redirects
            }

            # Attempt to make the request without required permissions
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.post(**request), 403)

            # Assign the required permission and submit again
            self.add_permissions(
                '{}.change_{}'.format(self.model._meta.app_label, self.model._meta.model_name)
            )
            response = self.client.post(**request)
            self.assertHttpStatus(response, 302)

            instance = self.model.objects.get(pk=instance.pk)
            self.assertDictEqual(model_to_dict(instance), self.form_data)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_delete_object(self):
            instance = self.model.objects.first()

            request = {
                'path': self._get_url('delete', instance),
                'data': {'confirm': True},
                'follow': False,  # Do not follow 302 redirects
            }

            # Attempt to make the request without required permissions
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.post(**request), 403)

            # Assign the required permission and submit again
            self.add_permissions(
                '{}.delete_{}'.format(self.model._meta.app_label, self.model._meta.model_name)
            )
            response = self.client.post(**request)
            self.assertHttpStatus(response, 302)

            with self.assertRaises(ObjectDoesNotExist):
                self.model.objects.get(pk=instance.pk)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_import_objects(self):
            initial_count = self.model.objects.count()
            request = {
                'path': self._get_url('import'),
                'data': {
                    'csv': '\n'.join(self.csv_data)
                }
            }

            # Attempt to make the request without required permissions
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.post(**request), 403)

            # Assign the required permission and submit again
            self.add_permissions(
                '{}.view_{}'.format(self.model._meta.app_label, self.model._meta.model_name),
                '{}.add_{}'.format(self.model._meta.app_label, self.model._meta.model_name)
            )
            response = self.client.post(**request)
            self.assertHttpStatus(response, 200)

            self.assertEqual(self.model.objects.count(), initial_count + len(self.csv_data) - 1)
