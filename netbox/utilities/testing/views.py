from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import override_settings
from django.urls import reverse

from extras.choices import ObjectChangeActionChoices
from extras.models import ObjectChange
from users.models import ObjectPermission
from .base import ModelTestCase
from .utils import disable_warnings, post_data

__all__ = (
    'ModelViewTestCase',
    'ViewTestCases',
)


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
            instance = self._get_queryset().order_by('pk').last()
            self.assertInstanceEqual(instance, self.form_data)

            # Verify ObjectChange creation
            objectchanges = ObjectChange.objects.filter(
                changed_object_type=ContentType.objects.get_for_model(instance),
                changed_object_id=instance.pk
            )
            self.assertEqual(len(objectchanges), 1)
            self.assertEqual(objectchanges[0].action, ObjectChangeActionChoices.ACTION_CREATE)

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

            # Verify ObjectChange creation
            objectchanges = ObjectChange.objects.filter(
                changed_object_type=ContentType.objects.get_for_model(instance),
                changed_object_id=instance.pk
            )
            self.assertEqual(len(objectchanges), 1)
            self.assertEqual(objectchanges[0].action, ObjectChangeActionChoices.ACTION_UPDATE)

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

            # Verify ObjectChange creation
            objectchanges = ObjectChange.objects.filter(
                changed_object_type=ContentType.objects.get_for_model(instance),
                changed_object_id=instance.pk
            )
            self.assertEqual(len(objectchanges), 1)
            self.assertEqual(objectchanges[0].action, ObjectChangeActionChoices.ACTION_DELETE)

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
            elif hasattr(self.model, 'get_absolute_url'):
                self.assertIn(instance1.get_absolute_url(), content)
                self.assertNotIn(instance2.get_absolute_url(), content)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
        def test_export_objects(self):
            url = self._get_url('list')

            # Test default CSV export
            response = self.client.get(f'{url}?export')
            self.assertHttpStatus(response, 200)
            self.assertEqual(response.get('Content-Type'), 'text/csv; charset=utf-8')

            # Test table-based export
            response = self.client.get(f'{url}?export=table')
            self.assertHttpStatus(response, 200)
            self.assertEqual(response.get('Content-Type'), 'text/csv; charset=utf-8')

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
