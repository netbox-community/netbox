import inspect
import json

import strawberry_django
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from strawberry.types.base import StrawberryList, StrawberryOptional
from strawberry.types.lazy_type import LazyType
from strawberry.types.union import StrawberryUnion

from core.choices import ObjectChangeActionChoices
from core.models import ObjectChange, ObjectType
from ipam.graphql.types import IPAddressFamilyType
from users.models import ObjectPermission, Token, User
from utilities.api import get_graphql_type_for_model
from .base import ModelTestCase
from .utils import disable_logging, disable_warnings

__all__ = (
    'APITestCase',
    'APIViewTestCases',
)


#
# REST/GraphQL API Tests
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
        Create a user and token for API calls.
        """
        # Create the test user and assign permissions
        self.user = User.objects.create_user(username='testuser')
        self.add_permissions(*self.user_permissions)
        self.token = Token.objects.create(user=self.user)
        self.header = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

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

        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'], LOGIN_REQUIRED=False)
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

        def test_get_object_without_permission(self):
            """
            GET a single object as an authenticated user without the required permission.
            """
            url = self._get_detail_url(self._get_queryset().first())

            # Try GET without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.get(url, **self.header), status.HTTP_403_FORBIDDEN)

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
            obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

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

        @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'], LOGIN_REQUIRED=False)
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

        def test_list_objects_brief(self):
            """
            GET a list of objects using the "brief" parameter.
            """
            self.add_permissions(f'{self.model._meta.app_label}.view_{self.model._meta.model_name}')
            url = f'{self._get_list_url()}?brief=1'
            response = self.client.get(url, **self.header)

            self.assertEqual(len(response.data['results']), self._get_queryset().count())
            self.assertEqual(sorted(response.data['results'][0]), self.brief_fields)

        def test_list_objects_without_permission(self):
            """
            GET a list of objects as an authenticated user without the required permission.
            """
            url = self._get_list_url()

            # Try GET without permission
            with disable_warnings('django.request'):
                self.assertHttpStatus(self.client.get(url, **self.header), status.HTTP_403_FORBIDDEN)

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
            obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

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
            obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

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
            obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

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
            obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

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
            obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

            id_list = list(self._get_queryset().values_list('id', flat=True)[:3])
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
            obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

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
            obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

            # Target the three most recently created objects to avoid triggering recursive deletions
            # (e.g. with MPTT objects)
            id_list = list(self._get_queryset().order_by('-id').values_list('id', flat=True)[:3])
            self.assertEqual(len(id_list), 3, "Insufficient number of objects to test bulk deletion")
            data = [{"id": id} for id in id_list]

            initial_count = self._get_queryset().count()
            response = self.client.delete(self._get_list_url(), data, format='json', **self.header)
            self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
            self.assertEqual(self._get_queryset().count(), initial_count - 3)

    class GraphQLTestCase(APITestCase):

        def _get_graphql_base_name(self):
            """
            Return graphql_base_name, if set. Otherwise, construct the base name for the query
            field from the model's verbose name.
            """
            base_name = self.model._meta.verbose_name.lower().replace(' ', '_')
            return getattr(self, 'graphql_base_name', base_name)

        def _build_query_with_filter(self, name, filter_string):
            """
            Called by either _build_query or _build_filtered_query - construct the actual
            query given a name and filter string
            """
            type_class = get_graphql_type_for_model(self.model)

            # Compile list of fields to include
            fields_string = ''

            file_fields = (
                strawberry_django.fields.types.DjangoFileType,
                strawberry_django.fields.types.DjangoImageType,
            )
            for field in type_class.__strawberry_definition__.fields:
                if (
                    field.type in file_fields or (
                        type(field.type) is StrawberryOptional and field.type.of_type in file_fields
                    )
                ):
                    # image / file fields nullable or not...
                    fields_string += f'{field.name} {{ name }}\n'
                elif type(field.type) is StrawberryList and type(field.type.of_type) is LazyType:
                    # List of related objects (queryset)
                    fields_string += f'{field.name} {{ id }}\n'
                elif type(field.type) is StrawberryList and type(field.type.of_type) is StrawberryUnion:
                    # this would require a fragment query
                    continue
                elif type(field.type) is StrawberryUnion:
                    # this would require a fragment query
                    continue
                elif type(field.type) is StrawberryOptional and type(field.type.of_type) is StrawberryUnion:
                    # this would require a fragment query
                    continue
                elif type(field.type) is StrawberryOptional and type(field.type.of_type) is LazyType:
                    fields_string += f'{field.name} {{ id }}\n'
                elif hasattr(field, 'is_relation') and field.is_relation:
                    # Ignore private fields
                    if field.name.startswith('_'):
                        continue
                    # Note: StrawberryField types do not have is_relation
                    fields_string += f'{field.name} {{ id }}\n'
                elif inspect.isclass(field.type) and issubclass(field.type, IPAddressFamilyType):
                    fields_string += f'{field.name} {{ value, label }}\n'
                else:
                    fields_string += f'{field.name}\n'

            query = f"""
            {{
                {name}{filter_string} {{
                    {fields_string}
                }}
            }}
            """

            return query

        def _build_filtered_query(self, name, **filters):
            """
            Create a filtered query: i.e. device_list(filters: {name: {i_contains: "akron"}}){.
            """
            # TODO: This should be extended to support AND, OR multi-lookups
            if filters:
                for field_name, params in filters.items():
                    lookup = params['lookup']
                    value = params['value']
                    if lookup:
                        query = f'{{{lookup}: "{value}"}}'
                        filter_string = f'{field_name}: {query}'
                    else:
                        filter_string = f'{field_name}: "{value}"'
                filter_string = f'(filters: {{{filter_string}}})'
            else:
                filter_string = ''

            return self._build_query_with_filter(name, filter_string)

        def _build_query(self, name, **filters):
            """
            Create a normal query - unfiltered or with a string query: i.e. site(name: "aaa"){.
            """
            if filters:
                filter_string = ', '.join(f'{k}:{v}' for k, v in filters.items())
                filter_string = f'({filter_string})'
            else:
                filter_string = ''

            return self._build_query_with_filter(name, filter_string)

        @override_settings(LOGIN_REQUIRED=True)
        def test_graphql_get_object(self):
            url = reverse('graphql')
            field_name = self._get_graphql_base_name()
            object_id = self._get_queryset().first().pk
            query = self._build_query(field_name, id=object_id)

            # Non-authenticated requests should fail
            header = {
                'HTTP_ACCEPT': 'application/json',
            }
            with disable_warnings('django.request'):
                response = self.client.post(url, data={'query': query}, format="json", **header)
            self.assertHttpStatus(response, status.HTTP_403_FORBIDDEN)

            # Add constrained permission
            obj_perm = ObjectPermission(
                name='Test permission',
                actions=['view'],
                constraints={'id': 0}  # Impossible constraint
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

            # Request should succeed but return empty result
            with disable_logging():
                response = self.client.post(url, data={'query': query}, format="json", **self.header)
            self.assertHttpStatus(response, status.HTTP_200_OK)
            data = json.loads(response.content)
            self.assertIn('errors', data)
            self.assertIsNone(data['data'])

            # Remove permission constraint
            obj_perm.constraints = None
            obj_perm.save()

            # Request should return requested object
            response = self.client.post(url, data={'query': query}, format="json", **self.header)
            self.assertHttpStatus(response, status.HTTP_200_OK)
            data = json.loads(response.content)
            self.assertNotIn('errors', data)
            self.assertIsNotNone(data['data'])

        @override_settings(LOGIN_REQUIRED=True)
        def test_graphql_list_objects(self):
            url = reverse('graphql')
            field_name = f'{self._get_graphql_base_name()}_list'
            query = self._build_query(field_name)

            # Non-authenticated requests should fail
            header = {
                'HTTP_ACCEPT': 'application/json',
            }
            with disable_warnings('django.request'):
                response = self.client.post(url, data={'query': query}, format="json", **header)
            self.assertHttpStatus(response, status.HTTP_403_FORBIDDEN)

            # Add constrained permission
            obj_perm = ObjectPermission(
                name='Test permission',
                actions=['view'],
                constraints={'id': 0}  # Impossible constraint
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

            # Request should succeed but return empty results list
            response = self.client.post(url, data={'query': query}, format="json", **self.header)
            self.assertHttpStatus(response, status.HTTP_200_OK)
            data = json.loads(response.content)
            self.assertNotIn('errors', data)
            self.assertEqual(len(data['data'][field_name]), 0)

            # Remove permission constraint
            obj_perm.constraints = None
            obj_perm.save()

            # Request should return all objects
            response = self.client.post(url, data={'query': query}, format="json", **self.header)
            self.assertHttpStatus(response, status.HTTP_200_OK)
            data = json.loads(response.content)
            self.assertNotIn('errors', data)
            self.assertEqual(len(data['data'][field_name]), self.model.objects.count())

        @override_settings(LOGIN_REQUIRED=True)
        def test_graphql_filter_objects(self):
            if not hasattr(self, 'graphql_filter'):
                return

            url = reverse('graphql')
            field_name = f'{self._get_graphql_base_name()}_list'
            query = self._build_filtered_query(field_name, **self.graphql_filter)

            # Add object-level permission
            obj_perm = ObjectPermission(
                name='Test permission',
                actions=['view']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

            response = self.client.post(url, data={'query': query}, format="json", **self.header)
            self.assertHttpStatus(response, status.HTTP_200_OK)
            data = json.loads(response.content)
            self.assertNotIn('errors', data)
            self.assertGreater(len(data['data'][field_name]), 0)

    class APIViewTestCase(
        GetObjectViewTestCase,
        ListObjectsViewTestCase,
        CreateObjectViewTestCase,
        UpdateObjectViewTestCase,
        DeleteObjectViewTestCase,
        GraphQLTestCase
    ):
        pass
