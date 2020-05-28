from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.test import Client, TestCase as _TestCase, override_settings
from django.urls import reverse, NoReverseMatch
from rest_framework.test import APIClient

from users.models import ObjectPermission, Token
from utilities.permissions import resolve_permission
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
            ct, action = resolve_permission(name)
            obj_perm = ObjectPermission(**{f'can_{action}': True})
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.content_types.add(ct)

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

    def assertInstanceEqual(self, instance, data):
        """
        Compare a model instance to a dictionary, checking that its attribute values match those specified
        in the dictionary.
        """
        model_dict = model_to_dict(instance, fields=data.keys())

        for key in list(model_dict.keys()):

            # TODO: Differentiate between tags assigned to the instance and a M2M field for tags (ex: ConfigContext)
            if key == 'tags':
                model_dict[key] = ','.join(sorted([tag.name for tag in model_dict['tags']]))

            # Convert ManyToManyField to list of instance PKs
            elif model_dict[key] and type(model_dict[key]) in (list, tuple) and hasattr(model_dict[key][0], 'pk'):
                model_dict[key] = [obj.pk for obj in model_dict[key]]

        # Omit any dictionary keys which are not instance attributes
        relevant_data = {
            k: v for k, v in data.items() if hasattr(instance, k)
        }

        self.assertDictEqual(model_dict, relevant_data)


class APITestCase(TestCase):
    client_class = APIClient

    def setUp(self):
        """
        Create a superuser and token for API calls.
        """
        self.user = User.objects.create(username='testuser', is_superuser=True)
        self.token = Token.objects.create(user=self.user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(self.token.key)}


class ViewTestCases:
    """
    We keep any TestCases with test_* methods inside a class to prevent unittest from trying to run them.
    """
    class GetObjectViewTestCase(ModelViewTestCase):
        """
        Retrieve a single instance.
        """
        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
        def test_get_object_anonymous(self):
            # Make the request as an unauthenticated user
            self.client.logout()
            response = self.client.get(self.model.objects.first().get_absolute_url())
            self.assertHttpStatus(response, 200)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_get_object_without_permission(self):
            instance = self.model.objects.first()

            # Try GET without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.get(instance.get_absolute_url()), 403)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_get_object_with_model_permission(self):
            instance = self.model.objects.first()

            # Add model-level permission
            obj_perm = ObjectPermission(
                can_view=True
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.content_types.add(ContentType.objects.get_for_model(self.model))

            # Try GET with model-level permission
            self.assertHttpStatus(self.client.get(instance.get_absolute_url()), 200)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_get_object_with_object_permission(self):
            instance1, instance2 = self.model.objects.all()[:2]

            # Add object-level permission
            obj_perm = ObjectPermission(
                attrs={'pk': instance1.pk},
                can_view=True
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.content_types.add(ContentType.objects.get_for_model(self.model))

            # Try GET to permitted object
            self.assertHttpStatus(self.client.get(instance1.get_absolute_url()), 200)

            # Try GET to non-permitted object
            self.assertHttpStatus(self.client.get(instance2.get_absolute_url()), 404)

    class CreateObjectViewTestCase(ModelViewTestCase):
        """
        Create a single new instance.
        """
        form_data = {}

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_create_object_without_permission(self):

            # Try GET without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.post(self._get_url('add')), 403)

            # Try POST without permission
            request = {
                'path': self._get_url('add'),
                'data': post_data(self.form_data),
            }
            response = self.client.post(**request)
            with disable_warnings('django.request'):
                self.assertHttpStatus(response, 403)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_create_object_with_model_permission(self):
            initial_count = self.model.objects.count()

            # Assign model-level permission
            obj_perm = ObjectPermission(
                can_add=True
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.content_types.add(ContentType.objects.get_for_model(self.model))

            # Try GET with model-level permission
            self.assertHttpStatus(self.client.get(self._get_url('add')), 200)

            # Try POST with model-level permission
            request = {
                'path': self._get_url('add'),
                'data': post_data(self.form_data),
            }
            self.assertHttpStatus(self.client.post(**request), 302)
            self.assertEqual(initial_count + 1, self.model.objects.count())
            self.assertInstanceEqual(self.model.objects.order_by('pk').last(), self.form_data)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_create_object_with_object_permission(self):
            initial_count = self.model.objects.count()

            # Assign object-level permission
            obj_perm = ObjectPermission(
                attrs={'pk__gt': 0},  # Dummy permission to allow all
                can_add=True
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.content_types.add(ContentType.objects.get_for_model(self.model))

            # Try GET with object-level permission
            self.assertHttpStatus(self.client.get(self._get_url('add')), 200)

            # Try to create permitted object
            request = {
                'path': self._get_url('add'),
                'data': post_data(self.form_data),
            }
            self.assertHttpStatus(self.client.post(**request), 302)
            self.assertEqual(initial_count + 1, self.model.objects.count())
            self.assertInstanceEqual(self.model.objects.order_by('pk').last(), self.form_data)

            # Nullify ObjectPermission to disallow new object creation
            obj_perm.attrs = {'pk': 0}
            obj_perm.save()

            # Try to create a non-permitted object
            initial_count = self.model.objects.count()
            request = {
                'path': self._get_url('add'),
                'data': post_data(self.form_data),
            }
            self.assertHttpStatus(self.client.post(**request), 200)
            self.assertEqual(initial_count, self.model.objects.count())  # Check that no object was created

    class EditObjectViewTestCase(ModelViewTestCase):
        """
        Edit a single existing instance.
        """
        form_data = {}

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_edit_object_without_permission(self):
            instance = self.model.objects.first()

            # Try GET without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.post(self._get_url('edit', instance)), 403)

            # Try POST without permission
            request = {
                'path': self._get_url('edit', instance),
                'data': post_data(self.form_data),
            }
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.post(**request), 403)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_edit_object_with_model_permission(self):
            instance = self.model.objects.first()

            # Assign model-level permission
            obj_perm = ObjectPermission(
                can_change=True
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.content_types.add(ContentType.objects.get_for_model(self.model))

            # Try GET with model-level permission
            self.assertHttpStatus(self.client.get(self._get_url('edit', instance)), 200)

            # Try POST with model-level permission
            request = {
                'path': self._get_url('edit', instance),
                'data': post_data(self.form_data),
            }
            self.assertHttpStatus(self.client.post(**request), 302)
            self.assertInstanceEqual(self.model.objects.get(pk=instance.pk), self.form_data)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_edit_object_with_object_permission(self):
            instance1, instance2 = self.model.objects.all()[:2]

            # Assign object-level permission
            obj_perm = ObjectPermission(
                attrs={'pk': instance1.pk},
                can_change=True
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.content_types.add(ContentType.objects.get_for_model(self.model))

            # Try GET with a permitted object
            self.assertHttpStatus(self.client.get(self._get_url('edit', instance1)), 200)

            # Try GET with a non-permitted object
            self.assertHttpStatus(self.client.get(self._get_url('edit', instance2)), 404)

            # Try to edit a permitted object
            request = {
                'path': self._get_url('edit', instance1),
                'data': post_data(self.form_data),
            }
            self.assertHttpStatus(self.client.post(**request), 302)
            self.assertInstanceEqual(self.model.objects.get(pk=instance1.pk), self.form_data)

            # Try to edit a non-permitted object
            request = {
                'path': self._get_url('edit', instance2),
                'data': post_data(self.form_data),
            }
            self.assertHttpStatus(self.client.post(**request), 404)

    class DeleteObjectViewTestCase(ModelViewTestCase):
        """
        Delete a single instance.
        """
        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_delete_object_without_permission(self):
            instance = self.model.objects.first()

            # Try GET without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.get(self._get_url('delete', instance)), 403)

            # Try POST without permission
            request = {
                'path': self._get_url('delete', instance),
                'data': post_data({'confirm': True}),
            }
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.post(**request), 403)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_delete_object_with_model_permission(self):
            instance = self.model.objects.first()

            # Assign model-level permission
            obj_perm = ObjectPermission(
                can_delete=True
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.content_types.add(ContentType.objects.get_for_model(self.model))

            # Try GET with model-level permission
            self.assertHttpStatus(self.client.get(self._get_url('delete', instance)), 200)

            # Try POST with model-level permission
            request = {
                'path': self._get_url('delete', instance),
                'data': post_data({'confirm': True}),
            }
            self.assertHttpStatus(self.client.post(**request), 302)
            with self.assertRaises(ObjectDoesNotExist):
                self.model.objects.get(pk=instance.pk)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_delete_object_with_object_permission(self):
            instance1, instance2 = self.model.objects.all()[:2]

            # Assign object-level permission
            obj_perm = ObjectPermission(
                attrs={'pk': instance1.pk},
                can_delete=True
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.content_types.add(ContentType.objects.get_for_model(self.model))

            # Try GET with a permitted object
            self.assertHttpStatus(self.client.get(self._get_url('delete', instance1)), 200)

            # Try GET with a non-permitted object
            self.assertHttpStatus(self.client.get(self._get_url('delete', instance2)), 404)

            # Try to delete a permitted object
            request = {
                'path': self._get_url('delete', instance1),
                'data': post_data({'confirm': True}),
            }
            self.assertHttpStatus(self.client.post(**request), 302)
            with self.assertRaises(ObjectDoesNotExist):
                self.model.objects.get(pk=instance1.pk)

            # Try to delete a non-permitted object
            request = {
                'path': self._get_url('delete', instance2),
                'data': post_data({'confirm': True}),
            }
            self.assertHttpStatus(self.client.post(**request), 404)
            self.assertTrue(self.model.objects.filter(pk=instance2.pk).exists())

    class ListObjectsViewTestCase(ModelViewTestCase):
        """
        Retrieve multiple instances.
        """
        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
        def test_list_objects_anonymous(self):
            # Make the request as an unauthenticated user
            self.client.logout()
            response = self.client.get(self._get_url('list'))
            self.assertHttpStatus(response, 200)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_list_objects_without_permission(self):

            # Try GET without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.get(self._get_url('list')), 403)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_list_objects_with_model_permission(self):

            # Add model-level permission
            obj_perm = ObjectPermission(
                can_view=True
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.content_types.add(ContentType.objects.get_for_model(self.model))

            # Try GET with model-level permission
            self.assertHttpStatus(self.client.get(self._get_url('list')), 200)

            # Built-in CSV export
            if hasattr(self.model, 'csv_headers'):
                response = self.client.get('{}?export'.format(self._get_url('list')))
                self.assertHttpStatus(response, 200)
                self.assertEqual(response.get('Content-Type'), 'text/csv')

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_list_objects_with_object_permission(self):
            instance1, instance2 = self.model.objects.all()[:2]

            # Add object-level permission
            obj_perm = ObjectPermission(
                attrs={'pk': instance1.pk},
                can_view=True
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.content_types.add(ContentType.objects.get_for_model(self.model))

            # Try GET with object-level permission
            self.assertHttpStatus(self.client.get(self._get_url('list')), 200)

            # TODO: Verify that only the permitted object is returned

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
            }

            # Attempt to make the request without required permissions
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.post(**request), 403)

            # Assign object-level permission
            obj_perm = ObjectPermission(can_add=True)
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.content_types.add(ContentType.objects.get_for_model(self.model))

            response = self.client.post(**request)
            self.assertHttpStatus(response, 302)

            self.assertEqual(initial_count + self.bulk_create_count, self.model.objects.count())
            for instance in self.model.objects.order_by('-pk')[:self.bulk_create_count]:
                self.assertInstanceEqual(instance, self.bulk_create_data)

    class BulkImportObjectsViewTestCase(ModelViewTestCase):
        """
        Create multiple instances from imported data.
        """
        csv_data = ()

        def _get_csv_data(self):
            return '\n'.join(self.csv_data)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_bulk_import_objects_without_permission(self):
            data = {
                'csv': self._get_csv_data(),
            }

            # Test GET without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.get(self._get_url('import')), 403)

            # Try POST without permission
            response = self.client.post(self._get_url('import'), data)
            with disable_warnings('django.request'):
                self.assertHttpStatus(response, 403)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_bulk_import_objects_with_model_permission(self):
            initial_count = self.model.objects.count()
            data = {
                'csv': self._get_csv_data(),
            }

            # Assign model-level permission
            obj_perm = ObjectPermission(
                can_add=True
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.content_types.add(ContentType.objects.get_for_model(self.model))

            # Try GET with model-level permission
            self.assertHttpStatus(self.client.get(self._get_url('import')), 200)

            # Test POST with permission
            self.assertHttpStatus(self.client.post(self._get_url('import'), data), 200)
            self.assertEqual(self.model.objects.count(), initial_count + len(self.csv_data) - 1)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_bulk_import_objects_with_object_permission(self):
            initial_count = self.model.objects.count()
            data = {
                'csv': self._get_csv_data(),
            }

            # Assign object-level permission
            obj_perm = ObjectPermission(
                attrs={'pk__gt': 0},  # Dummy permission to allow all
                can_add=True
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.content_types.add(ContentType.objects.get_for_model(self.model))

            # Test import with object-level permission
            self.assertHttpStatus(self.client.post(self._get_url('import'), data), 200)
            self.assertEqual(self.model.objects.count(), initial_count + len(self.csv_data) - 1)

            # TODO: Test importing non-permitted objects

    class BulkEditObjectsViewTestCase(ModelViewTestCase):
        """
        Edit multiple instances.
        """
        bulk_edit_data = {}

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_bulk_edit_objects_without_permission(self):
            pk_list = self.model.objects.values_list('pk', flat=True)[:3]
            data = {
                'pk': pk_list,
                '_apply': True,  # Form button
            }

            # Test GET without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.get(self._get_url('bulk_edit')), 403)

            # Try POST without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.post(self._get_url('bulk_edit'), data), 403)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_bulk_edit_objects_with_model_permission(self):
            pk_list = self.model.objects.values_list('pk', flat=True)[:3]
            data = {
                'pk': pk_list,
                '_apply': True,  # Form button
            }

            # Append the form data to the request
            data.update(post_data(self.bulk_edit_data))

            # Assign model-level permission
            obj_perm = ObjectPermission(
                can_change=True
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.content_types.add(ContentType.objects.get_for_model(self.model))

            # Try POST with model-level permission
            self.assertHttpStatus(self.client.post(self._get_url('bulk_edit'), data), 302)
            for i, instance in enumerate(self.model.objects.filter(pk__in=pk_list)):
                self.assertInstanceEqual(instance, self.bulk_edit_data)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_bulk_edit_objects_with_object_permission(self):
            pk_list = self.model.objects.values_list('pk', flat=True)[:3]
            data = {
                'pk': pk_list,
                '_apply': True,  # Form button
            }

            # Append the form data to the request
            data.update(post_data(self.bulk_edit_data))

            # Assign object-level permission
            obj_perm = ObjectPermission(
                attrs={'pk__in': list(pk_list)},
                can_change=True
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.content_types.add(ContentType.objects.get_for_model(self.model))

            # Try POST with model-level permission
            self.assertHttpStatus(self.client.post(self._get_url('bulk_edit'), data), 302)
            for i, instance in enumerate(self.model.objects.filter(pk__in=pk_list)):
                self.assertInstanceEqual(instance, self.bulk_edit_data)

            # TODO: Test editing non-permitted objects

    class BulkDeleteObjectsViewTestCase(ModelViewTestCase):
        """
        Delete multiple instances.
        """
        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_bulk_delete_objects_without_permission(self):
            pk_list = self.model.objects.values_list('pk', flat=True)[:3]
            data = {
                'pk': pk_list,
                'confirm': True,
                '_confirm': True,  # Form button
            }

            # Test GET without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.get(self._get_url('bulk_delete')), 403)

            # Try POST without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.post(self._get_url('bulk_delete'), data), 403)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_bulk_delete_objects_with_model_permission(self):
            pk_list = self.model.objects.values_list('pk', flat=True)
            data = {
                'pk': pk_list,
                'confirm': True,
                '_confirm': True,  # Form button
            }

            # Assign model-level permission
            obj_perm = ObjectPermission(
                can_delete=True
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.content_types.add(ContentType.objects.get_for_model(self.model))

            # Try POST with model-level permission
            self.assertHttpStatus(self.client.post(self._get_url('bulk_delete'), data), 302)
            self.assertEqual(self.model.objects.count(), 0)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_bulk_delete_objects_with_object_permission(self):
            pk_list = self.model.objects.values_list('pk', flat=True)
            data = {
                'pk': pk_list,
                'confirm': True,
                '_confirm': True,  # Form button
            }

            # Assign object-level permission
            obj_perm = ObjectPermission(
                attrs={'pk__in': list(pk_list)},
                can_delete=True
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.content_types.add(ContentType.objects.get_for_model(self.model))

            # Try POST with object-level permission
            self.assertHttpStatus(self.client.post(self._get_url('bulk_delete'), data), 302)
            self.assertEqual(self.model.objects.count(), 0)

            # TODO: Test deleting non-permitted objects

    class PrimaryObjectViewTestCase(
        GetObjectViewTestCase,
        CreateObjectViewTestCase,
        EditObjectViewTestCase,
        DeleteObjectViewTestCase,
        ListObjectsViewTestCase,
        BulkImportObjectsViewTestCase,
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
        BulkImportObjectsViewTestCase,
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
        BulkImportObjectsViewTestCase,
        BulkEditObjectsViewTestCase,
        BulkDeleteObjectsViewTestCase,
    ):
        """
        TestCase suitable for testing device component models (ConsolePorts, Interfaces, etc.)
        """
        maxDiff = None
