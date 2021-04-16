from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient

from extras.choices import ObjectChangeActionChoices
from extras.models import ObjectChange
from users.models import ObjectPermission, Token
from .base import ModelTestCase
from .utils import disable_warnings


__all__ = (
    'APITestCase',
    'APIViewTestCases',
)


#
# REST API Tests
#

class APITestCase(ModelTestCase):
    """
    Base test case for API requests.

    client_class: Test client class
    view_namespace: Namespace for API views. If None, the model's app_label will be used.
    """
    client_class = APIClient
    view_namespace = None

    def setUp(self):
        """
        Create a superuser and token for API calls.
        """
        # Create the test user and assign permissions
        self.user = User.objects.create_user(username='testuser')
        self.add_permissions(*self.user_permissions)
        self.token = Token.objects.create(user=self.user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(self.token.key)}

    def _get_view_namespace(self):
        return f'{self.view_namespace or self.model._meta.app_label}-api'

    def _get_detail_url(self, instance):
        viewname = f'{self._get_view_namespace()}:{instance._meta.model_name}-detail'
        return reverse(viewname, kwargs={'pk': instance.pk})

    def _get_list_url(self):
        viewname = f'{self._get_view_namespace()}:{self.model._meta.model_name}-list'
        return reverse(viewname)


class APIViewTestCases:

    class GetObjectViewTestCase(APITestCase):

        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
        def test_get_object_anonymous(self):
            """
            GET a single object as an unauthenticated user.
            """
            url = self._get_detail_url(self._get_queryset().first())
            if (self.model._meta.app_label, self.model._meta.model_name) in settings.EXEMPT_EXCLUDE_MODELS:
                # Models listed in EXEMPT_EXCLUDE_MODELS should not be accessible to anonymous users
                with disable_warnings('django.request'):
                    self.assertHttpStatus(self.client.get(url, **self.header), status.HTTP_403_FORBIDDEN)
            else:
                response = self.client.get(url, **self.header)
                self.assertHttpStatus(response, status.HTTP_200_OK)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_get_object_without_permission(self):
            """
            GET a single object as an authenticated user without the required permission.
            """
            url = self._get_detail_url(self._get_queryset().first())

            # Try GET without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.get(url, **self.header), status.HTTP_403_FORBIDDEN)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_get_object(self):
            """
            GET a single object as an authenticated user with permission to view the object.
            """
            self.assertGreaterEqual(self._get_queryset().count(), 2,
                                    f"Test requires the creation of at least two {self.model} instances")
            instance1, instance2 = self._get_queryset()[:2]

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
            url = self._get_detail_url(instance1)
            self.assertHttpStatus(self.client.get(url, **self.header), status.HTTP_200_OK)

            # Try GET to non-permitted object
            url = self._get_detail_url(instance2)
            self.assertHttpStatus(self.client.get(url, **self.header), status.HTTP_404_NOT_FOUND)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
        def test_options_object(self):
            """
            Make an OPTIONS request for a single object.
            """
            url = self._get_detail_url(self._get_queryset().first())
            response = self.client.options(url, **self.header)
            self.assertHttpStatus(response, status.HTTP_200_OK)

    class ListObjectsViewTestCase(APITestCase):
        brief_fields = []

        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
        def test_list_objects_anonymous(self):
            """
            GET a list of objects as an unauthenticated user.
            """
            url = self._get_list_url()
            if (self.model._meta.app_label, self.model._meta.model_name) in settings.EXEMPT_EXCLUDE_MODELS:
                # Models listed in EXEMPT_EXCLUDE_MODELS should not be accessible to anonymous users
                with disable_warnings('django.request'):
                    self.assertHttpStatus(self.client.get(url, **self.header), status.HTTP_403_FORBIDDEN)
            else:
                response = self.client.get(url, **self.header)
                self.assertHttpStatus(response, status.HTTP_200_OK)
                self.assertEqual(len(response.data['results']), self._get_queryset().count())

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_list_objects_brief(self):
            """
            GET a list of objects using the "brief" parameter.
            """
            self.add_permissions(f'{self.model._meta.app_label}.view_{self.model._meta.model_name}')
            url = f'{self._get_list_url()}?brief=1'
            response = self.client.get(url, **self.header)

            self.assertEqual(len(response.data['results']), self._get_queryset().count())
            self.assertEqual(sorted(response.data['results'][0]), self.brief_fields)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_list_objects_without_permission(self):
            """
            GET a list of objects as an authenticated user without the required permission.
            """
            url = self._get_list_url()

            # Try GET without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.get(url, **self.header), status.HTTP_403_FORBIDDEN)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
        def test_list_objects(self):
            """
            GET a list of objects as an authenticated user with permission to view the objects.
            """
            self.assertGreaterEqual(self._get_queryset().count(), 3,
                                    f"Test requires the creation of at least three {self.model} instances")
            instance1, instance2 = self._get_queryset()[:2]

            # Add object-level permission
            obj_perm = ObjectPermission(
                name='Test permission',
                constraints={'pk__in': [instance1.pk, instance2.pk]},
                actions=['view']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            # Try GET to permitted objects
            response = self.client.get(self._get_list_url(), **self.header)
            self.assertHttpStatus(response, status.HTTP_200_OK)
            self.assertEqual(len(response.data['results']), 2)

        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
        def test_options_objects(self):
            """
            Make an OPTIONS request for a list endpoint.
            """
            response = self.client.options(self._get_list_url(), **self.header)
            self.assertHttpStatus(response, status.HTTP_200_OK)

    class CreateObjectViewTestCase(APITestCase):
        create_data = []
        validation_excluded_fields = []

        def test_create_object_without_permission(self):
            """
            POST a single object without permission.
            """
            url = self._get_list_url()

            # Try POST without permission
            with disable_warnings('django.request'):
                response = self.client.post(url, self.create_data[0], format='json', **self.header)
                self.assertHttpStatus(response, status.HTTP_403_FORBIDDEN)

        def test_create_object(self):
            """
            POST a single object with permission.
            """
            # Add object-level permission
            obj_perm = ObjectPermission(
                name='Test permission',
                actions=['add']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            initial_count = self._get_queryset().count()
            response = self.client.post(self._get_list_url(), self.create_data[0], format='json', **self.header)
            self.assertHttpStatus(response, status.HTTP_201_CREATED)
            self.assertEqual(self._get_queryset().count(), initial_count + 1)
            instance = self._get_queryset().get(pk=response.data['id'])
            self.assertInstanceEqual(
                instance,
                self.create_data[0],
                exclude=self.validation_excluded_fields,
                api=True
            )

            # Verify ObjectChange creation
            if hasattr(self.model, 'to_objectchange'):
                objectchanges = ObjectChange.objects.filter(
                    changed_object_type=ContentType.objects.get_for_model(instance),
                    changed_object_id=instance.pk
                )
                self.assertEqual(len(objectchanges), 1)
                self.assertEqual(objectchanges[0].action, ObjectChangeActionChoices.ACTION_CREATE)

        def test_bulk_create_objects(self):
            """
            POST a set of objects in a single request.
            """
            # Add object-level permission
            obj_perm = ObjectPermission(
                name='Test permission',
                actions=['add']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            initial_count = self._get_queryset().count()
            response = self.client.post(self._get_list_url(), self.create_data, format='json', **self.header)
            self.assertHttpStatus(response, status.HTTP_201_CREATED)
            self.assertEqual(len(response.data), len(self.create_data))
            self.assertEqual(self._get_queryset().count(), initial_count + len(self.create_data))
            for i, obj in enumerate(response.data):
                for field in self.create_data[i]:
                    if field not in self.validation_excluded_fields:
                        self.assertIn(field, obj, f"Bulk create field '{field}' missing from object {i} in response")
            for i, obj in enumerate(response.data):
                self.assertInstanceEqual(
                    self._get_queryset().get(pk=obj['id']),
                    self.create_data[i],
                    exclude=self.validation_excluded_fields,
                    api=True
                )

    class UpdateObjectViewTestCase(APITestCase):
        update_data = {}
        bulk_update_data = None
        validation_excluded_fields = []

        def test_update_object_without_permission(self):
            """
            PATCH a single object without permission.
            """
            url = self._get_detail_url(self._get_queryset().first())
            update_data = self.update_data or getattr(self, 'create_data')[0]

            # Try PATCH without permission
            with disable_warnings('django.request'):
                response = self.client.patch(url, update_data, format='json', **self.header)
                self.assertHttpStatus(response, status.HTTP_403_FORBIDDEN)

        def test_update_object(self):
            """
            PATCH a single object identified by its numeric ID.
            """
            instance = self._get_queryset().first()
            url = self._get_detail_url(instance)
            update_data = self.update_data or getattr(self, 'create_data')[0]

            # Add object-level permission
            obj_perm = ObjectPermission(
                name='Test permission',
                actions=['change']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            response = self.client.patch(url, update_data, format='json', **self.header)
            self.assertHttpStatus(response, status.HTTP_200_OK)
            instance.refresh_from_db()
            self.assertInstanceEqual(
                instance,
                update_data,
                exclude=self.validation_excluded_fields,
                api=True
            )

            # Verify ObjectChange creation
            if hasattr(self.model, 'to_objectchange'):
                objectchanges = ObjectChange.objects.filter(
                    changed_object_type=ContentType.objects.get_for_model(instance),
                    changed_object_id=instance.pk
                )
                self.assertEqual(len(objectchanges), 1)
                self.assertEqual(objectchanges[0].action, ObjectChangeActionChoices.ACTION_UPDATE)

        def test_bulk_update_objects(self):
            """
            PATCH a set of objects in a single request.
            """
            if self.bulk_update_data is None:
                self.skipTest("Bulk update data not set")

            # Add object-level permission
            obj_perm = ObjectPermission(
                name='Test permission',
                actions=['change']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            id_list = self._get_queryset().values_list('id', flat=True)[:3]
            self.assertEqual(len(id_list), 3, "Insufficient number of objects to test bulk update")
            data = [
                {'id': id, **self.bulk_update_data} for id in id_list
            ]

            response = self.client.patch(self._get_list_url(), data, format='json', **self.header)
            self.assertHttpStatus(response, status.HTTP_200_OK)
            for i, obj in enumerate(response.data):
                for field in self.bulk_update_data:
                    self.assertIn(field, obj, f"Bulk update field '{field}' missing from object {i} in response")
            for instance in self._get_queryset().filter(pk__in=id_list):
                self.assertInstanceEqual(instance, self.bulk_update_data, api=True)

    class DeleteObjectViewTestCase(APITestCase):

        def test_delete_object_without_permission(self):
            """
            DELETE a single object without permission.
            """
            url = self._get_detail_url(self._get_queryset().first())

            # Try DELETE without permission
            with disable_warnings('django.request'):
                response = self.client.delete(url, **self.header)
                self.assertHttpStatus(response, status.HTTP_403_FORBIDDEN)

        def test_delete_object(self):
            """
            DELETE a single object identified by its numeric ID.
            """
            instance = self._get_queryset().first()
            url = self._get_detail_url(instance)

            # Add object-level permission
            obj_perm = ObjectPermission(
                name='Test permission',
                actions=['delete']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            response = self.client.delete(url, **self.header)
            self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
            self.assertFalse(self._get_queryset().filter(pk=instance.pk).exists())

            # Verify ObjectChange creation
            if hasattr(self.model, 'to_objectchange'):
                objectchanges = ObjectChange.objects.filter(
                    changed_object_type=ContentType.objects.get_for_model(instance),
                    changed_object_id=instance.pk
                )
                self.assertEqual(len(objectchanges), 1)
                self.assertEqual(objectchanges[0].action, ObjectChangeActionChoices.ACTION_DELETE)

        def test_bulk_delete_objects(self):
            """
            DELETE a set of objects in a single request.
            """
            # Add object-level permission
            obj_perm = ObjectPermission(
                name='Test permission',
                actions=['delete']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

            # Target the three most recently created objects to avoid triggering recursive deletions
            # (e.g. with MPTT objects)
            id_list = self._get_queryset().order_by('-id').values_list('id', flat=True)[:3]
            self.assertEqual(len(id_list), 3, "Insufficient number of objects to test bulk deletion")
            data = [{"id": id} for id in id_list]

            initial_count = self._get_queryset().count()
            response = self.client.delete(self._get_list_url(), data, format='json', **self.header)
            self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
            self.assertEqual(self._get_queryset().count(), initial_count - 3)

    class APIViewTestCase(
        GetObjectViewTestCase,
        ListObjectsViewTestCase,
        CreateObjectViewTestCase,
        UpdateObjectViewTestCase,
        DeleteObjectViewTestCase
    ):
        pass
