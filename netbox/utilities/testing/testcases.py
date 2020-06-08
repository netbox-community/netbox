from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.test import Client, TestCase as _TestCase, override_settings
from django.urls import reverse, NoReverseMatch
from netaddr import IPNetwork
from rest_framework import status
from rest_framework.test import APIClient

from users.models import Token
from .utils import disable_warnings, post_data


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

    def assertInstanceEqual(self, instance, data, api=False):
        """
        Compare a model instance to a dictionary, checking that its attribute values match those specified
        in the dictionary.

        :instance: Python object instance
        :data: Dictionary of test data used to define the instance
        :api: Set to True is the data is a JSON representation of the instance
        """
        model_dict = model_to_dict(instance, fields=data.keys())

        for key, value in list(model_dict.items()):

            # TODO: Differentiate between tags assigned to the instance and a M2M field for tags (ex: ConfigContext)
            if key == 'tags':
                model_dict[key] = ','.join(sorted([tag.name for tag in value]))

            # Convert ManyToManyField to list of instance PKs
            elif model_dict[key] and type(value) in (list, tuple) and hasattr(value[0], 'pk'):
                model_dict[key] = [obj.pk for obj in value]

            if api:

                # Replace ContentType numeric IDs with <app_label>.<model>
                if type(getattr(instance, key)) is ContentType:
                    ct = ContentType.objects.get(pk=value)
                    model_dict[key] = f'{ct.app_label}.{ct.model}'

                # Convert IPNetwork instances to strings
                if type(value) is IPNetwork:
                    model_dict[key] = str(value)

        # Omit any dictionary keys which are not instance attributes
        relevant_data = {
            k: v for k, v in data.items() if hasattr(instance, k)
        }

        self.assertDictEqual(model_dict, relevant_data)


#
# UI Tests
#

class ModelViewTestCase(TestCase):
    """
    Base TestCase for model views. Subclass to test individual views.
    """
    model = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.model is None:
            raise Exception("Test case requires model to be defined")

    def _get_base_url(self):
        """
        Return the base format for a URL for the test's model. Override this to test for a model which belongs
        to a different app (e.g. testing Interfaces within the virtualization app).
        """
        return '{}:{}_{{}}'.format(
            self.model._meta.app_label,
            self.model._meta.model_name
        )

    def _get_url(self, action, instance=None):
        """
        Return the URL name for a specific action. An instance must be specified for
        get/edit/delete views.
        """
        url_format = self._get_base_url()

        if action in ('list', 'add', 'import', 'bulk_edit', 'bulk_delete'):
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


class ViewTestCases:
    """
    We keep any TestCases with test_* methods inside a class to prevent unittest from trying to run them.
    """
    class GetObjectViewTestCase(ModelViewTestCase):
        """
        Retrieve a single instance.
        """
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

        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
        def test_get_object_anonymous(self):
            # Make the request as an unauthenticated user
            self.client.logout()
            response = self.client.get(self.model.objects.first().get_absolute_url())
            self.assertHttpStatus(response, 200)

    class CreateObjectViewTestCase(ModelViewTestCase):
        """
        Create a single new instance.
        """
        form_data = {}

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_create_object(self):

            # Try GET without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.post(self._get_url('add')), 403)

            # Try GET with permission
            self.add_permissions(
                '{}.add_{}'.format(self.model._meta.app_label, self.model._meta.model_name)
            )
            response = self.client.get(path=self._get_url('add'))
            self.assertHttpStatus(response, 200)

            # Try POST with permission
            initial_count = self.model.objects.count()
            request = {
                'path': self._get_url('add'),
                'data': post_data(self.form_data),
                'follow': False,  # Do not follow 302 redirects
            }
            response = self.client.post(**request)
            self.assertHttpStatus(response, 302)

            # Validate object creation
            self.assertEqual(initial_count + 1, self.model.objects.count())
            instance = self.model.objects.order_by('-pk').first()
            self.assertInstanceEqual(instance, self.form_data)

    class EditObjectViewTestCase(ModelViewTestCase):
        """
        Edit a single existing instance.
        """
        form_data = {}

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_edit_object(self):
            instance = self.model.objects.first()

            # Try GET without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.post(self._get_url('edit', instance)), 403)

            # Try GET with permission
            self.add_permissions(
                '{}.change_{}'.format(self.model._meta.app_label, self.model._meta.model_name)
            )
            response = self.client.get(path=self._get_url('edit', instance))
            self.assertHttpStatus(response, 200)

            # Try POST with permission
            request = {
                'path': self._get_url('edit', instance),
                'data': post_data(self.form_data),
                'follow': False,  # Do not follow 302 redirects
            }
            response = self.client.post(**request)
            self.assertHttpStatus(response, 302)

            # Validate object modifications
            instance = self.model.objects.get(pk=instance.pk)
            self.assertInstanceEqual(instance, self.form_data)

    class DeleteObjectViewTestCase(ModelViewTestCase):
        """
        Delete a single instance.
        """
        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_delete_object(self):
            instance = self.model.objects.first()

            # Try GET without permissions
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.post(self._get_url('delete', instance)), 403)

            # Try GET with permission
            self.add_permissions(
                '{}.delete_{}'.format(self.model._meta.app_label, self.model._meta.model_name)
            )
            response = self.client.get(path=self._get_url('delete', instance))
            self.assertHttpStatus(response, 200)

            request = {
                'path': self._get_url('delete', instance),
                'data': {'confirm': True},
                'follow': False,  # Do not follow 302 redirects
            }
            response = self.client.post(**request)
            self.assertHttpStatus(response, 302)

            # Validate object deletion
            with self.assertRaises(ObjectDoesNotExist):
                self.model.objects.get(pk=instance.pk)

    class ListObjectsViewTestCase(ModelViewTestCase):
        """
        Retrieve multiple instances.
        """
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

        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
        def test_list_objects_anonymous(self):
            # Make the request as an unauthenticated user
            self.client.logout()
            response = self.client.get(self._get_url('list'))
            self.assertHttpStatus(response, 200)

    class BulkCreateObjectsViewTestCase(ModelViewTestCase):
        """
        Create multiple instances using a single form. Expects the creation of three new instances by default.
        """
        bulk_create_count = 3
        bulk_create_data = {}

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_bulk_create_objects(self):
            initial_count = self.model.objects.count()
            request = {
                'path': self._get_url('add'),
                'data': post_data(self.bulk_create_data),
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

            self.assertEqual(initial_count + self.bulk_create_count, self.model.objects.count())
            for instance in self.model.objects.order_by('-pk')[:self.bulk_create_count]:
                self.assertInstanceEqual(instance, self.bulk_create_data)

    class ImportObjectsViewTestCase(ModelViewTestCase):
        """
        Create multiple instances from imported data.
        """
        csv_data = ()

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_import_objects(self):

            # Test GET without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.get(self._get_url('import')), 403)

            # Test GET with permission
            self.add_permissions(
                '{}.view_{}'.format(self.model._meta.app_label, self.model._meta.model_name),
                '{}.add_{}'.format(self.model._meta.app_label, self.model._meta.model_name)
            )
            response = self.client.get(self._get_url('import'))
            self.assertHttpStatus(response, 200)

            # Test POST with permission
            initial_count = self.model.objects.count()
            request = {
                'path': self._get_url('import'),
                'data': {
                    'csv': '\n'.join(self.csv_data)
                }
            }
            response = self.client.post(**request)
            self.assertHttpStatus(response, 200)

            # Validate import of new objects
            self.assertEqual(self.model.objects.count(), initial_count + len(self.csv_data) - 1)

    class BulkEditObjectsViewTestCase(ModelViewTestCase):
        """
        Edit multiple instances.
        """
        bulk_edit_data = {}

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_bulk_edit_objects(self):
            # Bulk edit the first three objects only
            pk_list = self.model.objects.values_list('pk', flat=True)[:3]

            request = {
                'path': self._get_url('bulk_edit'),
                'data': {
                    'pk': pk_list,
                    '_apply': True,  # Form button
                },
                'follow': False,  # Do not follow 302 redirects
            }

            # Append the form data to the request
            request['data'].update(post_data(self.bulk_edit_data))

            # Attempt to make the request without required permissions
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.post(**request), 403)

            # Assign the required permission and submit again
            self.add_permissions(
                '{}.change_{}'.format(self.model._meta.app_label, self.model._meta.model_name)
            )
            response = self.client.post(**request)
            self.assertHttpStatus(response, 302)

            for i, instance in enumerate(self.model.objects.filter(pk__in=pk_list)):
                self.assertInstanceEqual(instance, self.bulk_edit_data)

    class BulkDeleteObjectsViewTestCase(ModelViewTestCase):
        """
        Delete multiple instances.
        """
        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_bulk_delete_objects(self):
            pk_list = self.model.objects.values_list('pk', flat=True)

            request = {
                'path': self._get_url('bulk_delete'),
                'data': {
                    'pk': pk_list,
                    'confirm': True,
                    '_confirm': True,  # Form button
                },
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

            # Check that all objects were deleted
            self.assertEqual(self.model.objects.count(), 0)

    class PrimaryObjectViewTestCase(
        GetObjectViewTestCase,
        CreateObjectViewTestCase,
        EditObjectViewTestCase,
        DeleteObjectViewTestCase,
        ListObjectsViewTestCase,
        ImportObjectsViewTestCase,
        BulkEditObjectsViewTestCase,
        BulkDeleteObjectsViewTestCase,
    ):
        """
        TestCase suitable for testing all standard View functions for primary objects
        """
        maxDiff = None

    class OrganizationalObjectViewTestCase(
        CreateObjectViewTestCase,
        EditObjectViewTestCase,
        ListObjectsViewTestCase,
        ImportObjectsViewTestCase,
        BulkDeleteObjectsViewTestCase,
    ):
        """
        TestCase suitable for all organizational objects
        """
        maxDiff = None

    class DeviceComponentTemplateViewTestCase(
        EditObjectViewTestCase,
        DeleteObjectViewTestCase,
        BulkCreateObjectsViewTestCase,
        BulkEditObjectsViewTestCase,
        BulkDeleteObjectsViewTestCase,
    ):
        """
        TestCase suitable for testing device component template models (ConsolePortTemplates, InterfaceTemplates, etc.)
        """
        maxDiff = None

    class DeviceComponentViewTestCase(
        EditObjectViewTestCase,
        DeleteObjectViewTestCase,
        ListObjectsViewTestCase,
        BulkCreateObjectsViewTestCase,
        ImportObjectsViewTestCase,
        BulkEditObjectsViewTestCase,
        BulkDeleteObjectsViewTestCase,
    ):
        """
        TestCase suitable for testing device component models (ConsolePorts, Interfaces, etc.)
        """
        maxDiff = None


#
# REST API Tests
#

class APITestCase(TestCase):
    client_class = APIClient
    model = None

    def setUp(self):
        """
        Create a superuser and token for API calls.
        """
        self.user = User.objects.create(username='testuser', is_superuser=True)
        self.token = Token.objects.create(user=self.user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(self.token.key)}

    def _get_detail_url(self, instance):
        viewname = f'{instance._meta.app_label}-api:{instance._meta.model_name}-detail'
        return reverse(viewname, kwargs={'pk': instance.pk})

    def _get_list_url(self):
        viewname = f'{self.model._meta.app_label}-api:{self.model._meta.model_name}-list'
        return reverse(viewname)


class APIViewTestCases:

    class GetObjectViewTestCase(APITestCase):

        def test_get_object(self):
            """
            GET a single object identified by its numeric ID.
            """
            instance = self.model.objects.first()
            url = self._get_detail_url(instance)
            response = self.client.get(url, **self.header)

            self.assertEqual(response.data['id'], instance.pk)

    class ListObjectsViewTestCase(APITestCase):
        brief_fields = []

        def test_list_objects(self):
            """
            GET a list of objects.
            """
            url = self._get_list_url()
            response = self.client.get(url, **self.header)

            self.assertEqual(len(response.data['results']), self.model.objects.count())

        def test_list_objects_brief(self):
            """
            GET a list of objects using the "brief" parameter.
            """
            url = f'{self._get_list_url()}?brief=1'
            response = self.client.get(url, **self.header)

            self.assertEqual(len(response.data['results']), self.model.objects.count())
            self.assertEqual(sorted(response.data['results'][0]), self.brief_fields)

    class CreateObjectViewTestCase(APITestCase):
        create_data = []

        def test_create_object(self):
            """
            POST a single object.
            """
            initial_count = self.model.objects.count()
            url = self._get_list_url()
            response = self.client.post(url, self.create_data[0], format='json', **self.header)

            self.assertHttpStatus(response, status.HTTP_201_CREATED)
            self.assertEqual(self.model.objects.count(), initial_count + 1)
            self.assertInstanceEqual(self.model.objects.get(pk=response.data['id']), self.create_data[0], api=True)

        def test_bulk_create_object(self):
            """
            POST a set of objects in a single request.
            """
            initial_count = self.model.objects.count()
            url = self._get_list_url()
            response = self.client.post(url, self.create_data, format='json', **self.header)

            self.assertHttpStatus(response, status.HTTP_201_CREATED)
            self.assertEqual(self.model.objects.count(), initial_count + len(self.create_data))

    class UpdateObjectViewTestCase(APITestCase):
        update_data = {}

        def test_update_object(self):
            """
            PATCH a single object identified by its numeric ID.
            """
            instance = self.model.objects.first()
            url = self._get_detail_url(instance)
            update_data = self.update_data or getattr(self, 'create_data')[0]
            response = self.client.patch(url, update_data, format='json', **self.header)

            self.assertHttpStatus(response, status.HTTP_200_OK)
            instance.refresh_from_db()
            self.assertInstanceEqual(instance, self.update_data, api=True)

    class DeleteObjectViewTestCase(APITestCase):

        def test_delete_object(self):
            """
            DELETE a single object identified by its numeric ID.
            """
            instance = self.model.objects.first()
            url = self._get_detail_url(instance)
            response = self.client.delete(url, **self.header)

            self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
            self.assertFalse(self.model.objects.filter(pk=instance.pk).exists())

    class APIViewTestCase(
        GetObjectViewTestCase,
        ListObjectsViewTestCase,
        CreateObjectViewTestCase,
        UpdateObjectViewTestCase,
        DeleteObjectViewTestCase
    ):
        pass
