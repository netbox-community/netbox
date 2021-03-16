from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from django.db.models import ManyToManyField
from django.forms.models import model_to_dict
from django.test import Client, TestCase as _TestCase, override_settings
from django.urls import reverse, NoReverseMatch
from django.utils.text import slugify
from netaddr import IPNetwork
from taggit.managers import TaggableManager

from extras.models import Tag
from users.models import ObjectPermission
from utilities.permissions import resolve_permission_ct
from .utils import disable_warnings, extract_form_failures, post_data


__all__ = (
    'TestCase',
    'ModelTestCase',
    'ModelViewTestCase',
    'ViewTestCases',
)


class TestCase(_TestCase):
    user_permissions = ()

    def setUp(self):

        # Create the test user and assign permissions
        self.user = User.objects.create_user(username='testuser')
        self.add_permissions(*self.user_permissions)

        # Initialize the test client
        self.client = Client()
        self.client.force_login(self.user)

    def prepare_instance(self, instance):
        """
        Test cases can override this method to perform any necessary manipulation of an instance prior to its evaluation
        against test data. For example, it can be used to decrypt a Secret's plaintext attribute.
        """
        return instance

    def model_to_dict(self, instance, fields, api=False):
        """
        Return a dictionary representation of an instance.
        """
        # Prepare the instance and call Django's model_to_dict() to extract all fields
        model_dict = model_to_dict(self.prepare_instance(instance), fields=fields)

        # Map any additional (non-field) instance attributes that were specified
        for attr in fields:
            if hasattr(instance, attr) and attr not in model_dict:
                model_dict[attr] = getattr(instance, attr)

        for key, value in list(model_dict.items()):
            try:
                field = instance._meta.get_field(key)
            except FieldDoesNotExist:
                # Attribute is not a model field
                continue

            # Handle ManyToManyFields
            if value and type(field) in (ManyToManyField, TaggableManager):

                if field.related_model is ContentType:
                    model_dict[key] = sorted([f'{ct.app_label}.{ct.model}' for ct in value])
                else:
                    model_dict[key] = sorted([obj.pk for obj in value])

            if api:

                # Replace ContentType numeric IDs with <app_label>.<model>
                if type(getattr(instance, key)) is ContentType:
                    ct = ContentType.objects.get(pk=value)
                    model_dict[key] = f'{ct.app_label}.{ct.model}'

                # Convert IPNetwork instances to strings
                elif type(value) is IPNetwork:
                    model_dict[key] = str(value)

            else:

                # Convert ArrayFields to CSV strings
                if type(instance._meta.get_field(key)) is ArrayField:
                    model_dict[key] = ','.join([str(v) for v in value])

        return model_dict

    #
    # Permissions management
    #

    def add_permissions(self, *names):
        """
        Assign a set of permissions to the test user. Accepts permission names in the form <app>.<action>_<model>.
        """
        for name in names:
            ct, action = resolve_permission_ct(name)
            obj_perm = ObjectPermission(name=name, actions=[action])
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ct)

    #
    # Custom assertions
    #

    def assertHttpStatus(self, response, expected_status):
        """
        TestCase method. Provide more detail in the event of an unexpected HTTP response.
        """
        err_message = None
        # Construct an error message only if we know the test is going to fail
        if response.status_code != expected_status:
            if hasattr(response, 'data'):
                # REST API response; pass the response data through directly
                err = response.data
            else:
                # Attempt to extract form validation errors from the response HTML
                form_errors = extract_form_failures(response.content)
                err = form_errors or response.content or 'No data'
            err_message = f"Expected HTTP status {expected_status}; received {response.status_code}: {err}"
        self.assertEqual(response.status_code, expected_status, err_message)

    def assertInstanceEqual(self, instance, data, exclude=None, api=False):
        """
        Compare a model instance to a dictionary, checking that its attribute values match those specified
        in the dictionary.

        :param instance: Python object instance
        :param data: Dictionary of test data used to define the instance
        :param exclude: List of fields to exclude from comparison (e.g. passwords, which get hashed)
        :param api: Set to True is the data is a JSON representation of the instance
        """
        if exclude is None:
            exclude = []

        fields = [k for k in data.keys() if k not in exclude]
        model_dict = self.model_to_dict(instance, fields=fields, api=api)

        # Omit any dictionary keys which are not instance attributes or have been excluded
        relevant_data = {
            k: v for k, v in data.items() if hasattr(instance, k) and k not in exclude
        }

        self.assertDictEqual(model_dict, relevant_data)

    #
    # Convenience methods
    #

    @classmethod
    def create_tags(cls, *names):
        """
        Create and return a Tag instance for each name given.
        """
        tags = [Tag(name=name, slug=slugify(name)) for name in names]
        Tag.objects.bulk_create(tags)
        return tags


class ModelTestCase(TestCase):
    """
    Parent class for TestCases which deal with models.
    """
    model = None

    def _get_queryset(self):
        """
        Return a base queryset suitable for use in test methods.
        """
        return self.model.objects.all()


#
# UI Tests
#

class ModelViewTestCase(ModelTestCase):
    """
    Base TestCase for model views. Subclass to test individual views.
    """

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
        Return the URL name for a specific action and optionally a specific instance
        """
        url_format = self._get_base_url()

        # If no instance was provided, assume we don't need a unique identifier
        if instance is None:
            return reverse(url_format.format(action))

        # Attempt to resolve using slug as the unique identifier if one exists
        if hasattr(self.model, 'slug'):
            try:
                return reverse(url_format.format(action), kwargs={'slug': instance.slug})
            except NoReverseMatch:
                pass

        # Default to using the numeric PK to retrieve the URL for an object
        return reverse(url_format.format(action), kwargs={'pk': instance.pk})


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
            response = self.client.get(self._get_queryset().first().get_absolute_url())
            self.assertHttpStatus(response, 200)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_get_object_without_permission(self):
            instance = self._get_queryset().first()

            # Try GET without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.get(instance.get_absolute_url()), 403)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_get_object_with_permission(self):
            instance = self._get_queryset().first()

            # Add model-level permission
            obj_perm = ObjectPermission(
                name='Test permission',
                actions=['view']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            # Try GET with model-level permission
            self.assertHttpStatus(self.client.get(instance.get_absolute_url()), 200)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_get_object_with_constrained_permission(self):
            instance1, instance2 = self._get_queryset().all()[:2]

            # Add object-level permission
            obj_perm = ObjectPermission(
                name='Test permission',
                constraints={'pk': instance1.pk},
                actions=['view']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            # Try GET to permitted object
            self.assertHttpStatus(self.client.get(instance1.get_absolute_url()), 200)

            # Try GET to non-permitted object
            self.assertHttpStatus(self.client.get(instance2.get_absolute_url()), 404)

    class GetObjectChangelogViewTestCase(ModelViewTestCase):
        """
        View the changelog for an instance.
        """
        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
        def test_get_object_changelog(self):
            url = self._get_url('changelog', self._get_queryset().first())
            response = self.client.get(url)
            self.assertHttpStatus(response, 200)

    class CreateObjectViewTestCase(ModelViewTestCase):
        """
        Create a single new instance.

        :form_data: Data to be used when creating a new object.
        """
        form_data = {}

        def test_create_object_without_permission(self):

            # Try GET without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.get(self._get_url('add')), 403)

            # Try POST without permission
            request = {
                'path': self._get_url('add'),
                'data': post_data(self.form_data),
            }
            response = self.client.post(**request)
            with disable_warnings('django.request'):
                self.assertHttpStatus(response, 403)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
        def test_create_object_with_permission(self):
            initial_count = self._get_queryset().count()

            # Assign unconstrained permission
            obj_perm = ObjectPermission(
                name='Test permission',
                actions=['add']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            # Try GET with model-level permission
            self.assertHttpStatus(self.client.get(self._get_url('add')), 200)

            # Try POST with model-level permission
            request = {
                'path': self._get_url('add'),
                'data': post_data(self.form_data),
            }
            self.assertHttpStatus(self.client.post(**request), 302)
            self.assertEqual(initial_count + 1, self._get_queryset().count())
            self.assertInstanceEqual(self._get_queryset().order_by('pk').last(), self.form_data)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
        def test_create_object_with_constrained_permission(self):
            initial_count = self._get_queryset().count()

            # Assign constrained permission
            obj_perm = ObjectPermission(
                name='Test permission',
                constraints={'pk': 0},  # Dummy permission to deny all
                actions=['add']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            # Try GET with object-level permission
            self.assertHttpStatus(self.client.get(self._get_url('add')), 200)

            # Try to create an object (not permitted)
            request = {
                'path': self._get_url('add'),
                'data': post_data(self.form_data),
            }
            self.assertHttpStatus(self.client.post(**request), 200)
            self.assertEqual(initial_count, self._get_queryset().count())  # Check that no object was created

            # Update the ObjectPermission to allow creation
            obj_perm.constraints = {'pk__gt': 0}
            obj_perm.save()

            # Try to create an object (permitted)
            request = {
                'path': self._get_url('add'),
                'data': post_data(self.form_data),
            }
            self.assertHttpStatus(self.client.post(**request), 302)
            self.assertEqual(initial_count + 1, self._get_queryset().count())
            self.assertInstanceEqual(self._get_queryset().order_by('pk').last(), self.form_data)

    class EditObjectViewTestCase(ModelViewTestCase):
        """
        Edit a single existing instance.

        :form_data: Data to be used when updating the first existing object.
        """
        form_data = {}

        def test_edit_object_without_permission(self):
            instance = self._get_queryset().first()

            # Try GET without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.get(self._get_url('edit', instance)), 403)

            # Try POST without permission
            request = {
                'path': self._get_url('edit', instance),
                'data': post_data(self.form_data),
            }
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.post(**request), 403)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
        def test_edit_object_with_permission(self):
            instance = self._get_queryset().first()

            # Assign model-level permission
            obj_perm = ObjectPermission(
                name='Test permission',
                actions=['change']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            # Try GET with model-level permission
            self.assertHttpStatus(self.client.get(self._get_url('edit', instance)), 200)

            # Try POST with model-level permission
            request = {
                'path': self._get_url('edit', instance),
                'data': post_data(self.form_data),
            }
            self.assertHttpStatus(self.client.post(**request), 302)
            self.assertInstanceEqual(self._get_queryset().get(pk=instance.pk), self.form_data)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
        def test_edit_object_with_constrained_permission(self):
            instance1, instance2 = self._get_queryset().all()[:2]

            # Assign constrained permission
            obj_perm = ObjectPermission(
                name='Test permission',
                constraints={'pk': instance1.pk},
                actions=['change']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

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
            self.assertInstanceEqual(self._get_queryset().get(pk=instance1.pk), self.form_data)

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
        def test_delete_object_without_permission(self):
            instance = self._get_queryset().first()

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

        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
        def test_delete_object_with_permission(self):
            instance = self._get_queryset().first()

            # Assign model-level permission
            obj_perm = ObjectPermission(
                name='Test permission',
                actions=['delete']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            # Try GET with model-level permission
            self.assertHttpStatus(self.client.get(self._get_url('delete', instance)), 200)

            # Try POST with model-level permission
            request = {
                'path': self._get_url('delete', instance),
                'data': post_data({'confirm': True}),
            }
            self.assertHttpStatus(self.client.post(**request), 302)
            with self.assertRaises(ObjectDoesNotExist):
                self._get_queryset().get(pk=instance.pk)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
        def test_delete_object_with_constrained_permission(self):
            instance1, instance2 = self._get_queryset().all()[:2]

            # Assign object-level permission
            obj_perm = ObjectPermission(
                name='Test permission',
                constraints={'pk': instance1.pk},
                actions=['delete']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

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
                self._get_queryset().get(pk=instance1.pk)

            # Try to delete a non-permitted object
            request = {
                'path': self._get_url('delete', instance2),
                'data': post_data({'confirm': True}),
            }
            self.assertHttpStatus(self.client.post(**request), 404)
            self.assertTrue(self._get_queryset().filter(pk=instance2.pk).exists())

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
        def test_list_objects_with_permission(self):

            # Add model-level permission
            obj_perm = ObjectPermission(
                name='Test permission',
                actions=['view']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            # Try GET with model-level permission
            self.assertHttpStatus(self.client.get(self._get_url('list')), 200)

            # Built-in CSV export
            if hasattr(self.model, 'csv_headers'):
                response = self.client.get('{}?export'.format(self._get_url('list')))
                self.assertHttpStatus(response, 200)
                self.assertEqual(response.get('Content-Type'), 'text/csv')

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_list_objects_with_constrained_permission(self):
            instance1, instance2 = self._get_queryset().all()[:2]

            # Add object-level permission
            obj_perm = ObjectPermission(
                name='Test permission',
                constraints={'pk': instance1.pk},
                actions=['view']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            # Try GET with object-level permission
            response = self.client.get(self._get_url('list'))
            self.assertHttpStatus(response, 200)
            content = str(response.content)
            if hasattr(self.model, 'name'):
                self.assertIn(instance1.name, content)
                self.assertNotIn(instance2.name, content)
            else:
                self.assertIn(instance1.get_absolute_url(), content)
                self.assertNotIn(instance2.get_absolute_url(), content)

    class CreateMultipleObjectsViewTestCase(ModelViewTestCase):
        """
        Create multiple instances using a single form. Expects the creation of three new instances by default.

        :bulk_create_count: The number of objects expected to be created (default: 3).
        :bulk_create_data: A dictionary of data to be used for bulk object creation.
        """
        bulk_create_count = 3
        bulk_create_data = {}

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_create_multiple_objects_without_permission(self):
            request = {
                'path': self._get_url('add'),
                'data': post_data(self.bulk_create_data),
            }

            # Try POST without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.post(**request), 403)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_create_multiple_objects_with_permission(self):
            initial_count = self._get_queryset().count()
            request = {
                'path': self._get_url('add'),
                'data': post_data(self.bulk_create_data),
            }

            # Assign non-constrained permission
            obj_perm = ObjectPermission(
                name='Test permission',
                actions=['add'],
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            # Bulk create objects
            response = self.client.post(**request)
            self.assertHttpStatus(response, 302)
            self.assertEqual(initial_count + self.bulk_create_count, self._get_queryset().count())
            for instance in self._get_queryset().order_by('-pk')[:self.bulk_create_count]:
                self.assertInstanceEqual(instance, self.bulk_create_data)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_create_multiple_objects_with_constrained_permission(self):
            initial_count = self._get_queryset().count()
            request = {
                'path': self._get_url('add'),
                'data': post_data(self.bulk_create_data),
            }

            # Assign constrained permission
            obj_perm = ObjectPermission(
                name='Test permission',
                actions=['add'],
                constraints={'pk': 0}  # Dummy constraint to deny all
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            # Attempt to make the request with unmet constraints
            self.assertHttpStatus(self.client.post(**request), 200)
            self.assertEqual(self._get_queryset().count(), initial_count)

            # Update the ObjectPermission to allow creation
            obj_perm.constraints = {'pk__gt': 0}  # Dummy constraint to allow all
            obj_perm.save()

            response = self.client.post(**request)
            self.assertHttpStatus(response, 302)
            self.assertEqual(initial_count + self.bulk_create_count, self._get_queryset().count())
            for instance in self._get_queryset().order_by('-pk')[:self.bulk_create_count]:
                self.assertInstanceEqual(instance, self.bulk_create_data)

    class BulkImportObjectsViewTestCase(ModelViewTestCase):
        """
        Create multiple instances from imported data.

        :csv_data: A list of CSV-formatted lines (starting with the headers) to be used for bulk object import.
        """
        csv_data = ()

        def _get_csv_data(self):
            return '\n'.join(self.csv_data)

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

        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
        def test_bulk_import_objects_with_permission(self):
            initial_count = self._get_queryset().count()
            data = {
                'csv': self._get_csv_data(),
            }

            # Assign model-level permission
            obj_perm = ObjectPermission(
                name='Test permission',
                actions=['add']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            # Try GET with model-level permission
            self.assertHttpStatus(self.client.get(self._get_url('import')), 200)

            # Test POST with permission
            self.assertHttpStatus(self.client.post(self._get_url('import'), data), 200)
            self.assertEqual(self._get_queryset().count(), initial_count + len(self.csv_data) - 1)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
        def test_bulk_import_objects_with_constrained_permission(self):
            initial_count = self._get_queryset().count()
            data = {
                'csv': self._get_csv_data(),
            }

            # Assign constrained permission
            obj_perm = ObjectPermission(
                name='Test permission',
                constraints={'pk': 0},  # Dummy permission to deny all
                actions=['add']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            # Attempt to import non-permitted objects
            self.assertHttpStatus(self.client.post(self._get_url('import'), data), 200)
            self.assertEqual(self._get_queryset().count(), initial_count)

            # Update permission constraints
            obj_perm.constraints = {'pk__gt': 0}  # Dummy permission to allow all
            obj_perm.save()

            # Import permitted objects
            self.assertHttpStatus(self.client.post(self._get_url('import'), data), 200)
            self.assertEqual(self._get_queryset().count(), initial_count + len(self.csv_data) - 1)

    class BulkEditObjectsViewTestCase(ModelViewTestCase):
        """
        Edit multiple instances.

        :bulk_edit_data: A dictionary of data to be used when bulk editing a set of objects. This data should differ
                         from that used for initial object creation within setUpTestData().
        """
        bulk_edit_data = {}

        def test_bulk_edit_objects_without_permission(self):
            pk_list = self._get_queryset().values_list('pk', flat=True)[:3]
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

        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
        def test_bulk_edit_objects_with_permission(self):
            pk_list = self._get_queryset().values_list('pk', flat=True)[:3]
            data = {
                'pk': pk_list,
                '_apply': True,  # Form button
            }

            # Append the form data to the request
            data.update(post_data(self.bulk_edit_data))

            # Assign model-level permission
            obj_perm = ObjectPermission(
                name='Test permission',
                actions=['change']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            # Try POST with model-level permission
            self.assertHttpStatus(self.client.post(self._get_url('bulk_edit'), data), 302)
            for i, instance in enumerate(self._get_queryset().filter(pk__in=pk_list)):
                self.assertInstanceEqual(instance, self.bulk_edit_data)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
        def test_bulk_edit_objects_with_constrained_permission(self):
            pk_list = list(self._get_queryset().values_list('pk', flat=True)[:3])
            data = {
                'pk': pk_list,
                '_apply': True,  # Form button
            }

            # Append the form data to the request
            data.update(post_data(self.bulk_edit_data))

            # Dynamically determine a constraint that will *not* be matched by the updated objects.
            attr_name = list(self.bulk_edit_data.keys())[0]
            field = self.model._meta.get_field(attr_name)
            value = field.value_from_object(self._get_queryset().first())

            # Assign constrained permission
            obj_perm = ObjectPermission(
                name='Test permission',
                constraints={attr_name: value},
                actions=['change']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            # Attempt to bulk edit permitted objects into a non-permitted state
            response = self.client.post(self._get_url('bulk_edit'), data)
            self.assertHttpStatus(response, 200)

            # Update permission constraints
            obj_perm.constraints = {'pk__gt': 0}
            obj_perm.save()

            # Bulk edit permitted objects
            self.assertHttpStatus(self.client.post(self._get_url('bulk_edit'), data), 302)
            for i, instance in enumerate(self._get_queryset().filter(pk__in=pk_list)):
                self.assertInstanceEqual(instance, self.bulk_edit_data)

    class BulkDeleteObjectsViewTestCase(ModelViewTestCase):
        """
        Delete multiple instances.
        """
        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_bulk_delete_objects_without_permission(self):
            pk_list = self._get_queryset().values_list('pk', flat=True)[:3]
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
        def test_bulk_delete_objects_with_permission(self):
            pk_list = self._get_queryset().values_list('pk', flat=True)
            data = {
                'pk': pk_list,
                'confirm': True,
                '_confirm': True,  # Form button
            }

            # Assign unconstrained permission
            obj_perm = ObjectPermission(
                name='Test permission',
                actions=['delete']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            # Try POST with model-level permission
            self.assertHttpStatus(self.client.post(self._get_url('bulk_delete'), data), 302)
            self.assertEqual(self._get_queryset().count(), 0)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_bulk_delete_objects_with_constrained_permission(self):
            initial_count = self._get_queryset().count()
            pk_list = self._get_queryset().values_list('pk', flat=True)
            data = {
                'pk': pk_list,
                'confirm': True,
                '_confirm': True,  # Form button
            }

            # Assign constrained permission
            obj_perm = ObjectPermission(
                name='Test permission',
                constraints={'pk': 0},  # Dummy permission to deny all
                actions=['delete']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            # Attempt to bulk delete non-permitted objects
            self.assertHttpStatus(self.client.post(self._get_url('bulk_delete'), data), 302)
            self.assertEqual(self._get_queryset().count(), initial_count)

            # Update permission constraints
            obj_perm.constraints = {'pk__gt': 0}  # Dummy permission to allow all
            obj_perm.save()

            # Bulk delete permitted objects
            self.assertHttpStatus(self.client.post(self._get_url('bulk_delete'), data), 302)
            self.assertEqual(self._get_queryset().count(), 0)

    class BulkRenameObjectsViewTestCase(ModelViewTestCase):
        """
        Rename multiple instances.
        """
        rename_data = {
            'find': '^(.*)$',
            'replace': '\\1X',  # Append an X to the original value
            'use_regex': True,
        }

        def test_bulk_rename_objects_without_permission(self):
            pk_list = self._get_queryset().values_list('pk', flat=True)[:3]
            data = {
                'pk': pk_list,
                '_apply': True,  # Form button
            }
            data.update(self.rename_data)

            # Test GET without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.get(self._get_url('bulk_rename')), 403)

            # Try POST without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.post(self._get_url('bulk_rename'), data), 403)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
        def test_bulk_rename_objects_with_permission(self):
            objects = self._get_queryset().all()[:3]
            pk_list = [obj.pk for obj in objects]
            data = {
                'pk': pk_list,
                '_apply': True,  # Form button
            }
            data.update(self.rename_data)

            # Assign model-level permission
            obj_perm = ObjectPermission(
                name='Test permission',
                actions=['change']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            # Try POST with model-level permission
            self.assertHttpStatus(self.client.post(self._get_url('bulk_rename'), data), 302)
            for i, instance in enumerate(self._get_queryset().filter(pk__in=pk_list)):
                self.assertEqual(instance.name, f'{objects[i].name}X')

        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
        def test_bulk_rename_objects_with_constrained_permission(self):
            objects = self._get_queryset().all()[:3]
            pk_list = [obj.pk for obj in objects]
            data = {
                'pk': pk_list,
                '_apply': True,  # Form button
            }
            data.update(self.rename_data)

            # Assign constrained permission
            obj_perm = ObjectPermission(
                name='Test permission',
                constraints={'name__regex': '[^X]$'},
                actions=['change']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            # Attempt to bulk edit permitted objects into a non-permitted state
            response = self.client.post(self._get_url('bulk_rename'), data)
            self.assertHttpStatus(response, 200)

            # Update permission constraints
            obj_perm.constraints = {'pk__gt': 0}
            obj_perm.save()

            # Bulk rename permitted objects
            self.assertHttpStatus(self.client.post(self._get_url('bulk_rename'), data), 302)
            for i, instance in enumerate(self._get_queryset().filter(pk__in=pk_list)):
                self.assertEqual(instance.name, f'{objects[i].name}X')

    class PrimaryObjectViewTestCase(
        GetObjectViewTestCase,
        GetObjectChangelogViewTestCase,
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
        GetObjectChangelogViewTestCase,
        CreateObjectViewTestCase,
        EditObjectViewTestCase,
        DeleteObjectViewTestCase,
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
        CreateMultipleObjectsViewTestCase,
        BulkEditObjectsViewTestCase,
        BulkRenameObjectsViewTestCase,
        BulkDeleteObjectsViewTestCase,
    ):
        """
        TestCase suitable for testing device component template models (ConsolePortTemplates, InterfaceTemplates, etc.)
        """
        maxDiff = None

    class DeviceComponentViewTestCase(
        GetObjectViewTestCase,
        GetObjectChangelogViewTestCase,
        EditObjectViewTestCase,
        DeleteObjectViewTestCase,
        ListObjectsViewTestCase,
        CreateMultipleObjectsViewTestCase,
        BulkImportObjectsViewTestCase,
        BulkEditObjectsViewTestCase,
        BulkRenameObjectsViewTestCase,
        BulkDeleteObjectsViewTestCase,
    ):
        """
        TestCase suitable for testing device component models (ConsolePorts, Interfaces, etc.)
        """
        maxDiff = None
