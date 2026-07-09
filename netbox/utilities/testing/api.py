import copy
import importlib
import inspect
import json
import types
import typing
from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal

import strawberry
import strawberry_django
from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.test import override_settings
from django.urls import reverse
from graphql import GraphQLList, GraphQLNonNull, GraphQLObjectType
from rest_framework import status
from rest_framework.test import APIClient
from strawberry.schema.schema_converter import GraphQLCoreConverter
from strawberry.types.base import StrawberryList, StrawberryOptional
from strawberry.types.lazy_type import LazyType
from strawberry.types.union import StrawberryUnion
from strawberry_django import (
    BaseFilterLookup,
    ComparisonFilterLookup,
    DateFilterLookup,
    DatetimeFilterLookup,
    FilterLookup,
    RangeLookup,
    StrFilterLookup,
    TimeFilterLookup,
)

from core.choices import ObjectChangeActionChoices
from core.models import ObjectChange, ObjectType
from ipam.graphql.types import IPAddressFamilyType
from netbox.api.exceptions import GraphQLTypeNotFound
from netbox.graphql.filter_lookups import (
    ArrayLookup,
    BigIntegerLookup,
    FloatLookup,
    IntegerLookup,
    IntegerRangeArrayLookup,
    JSONFilter,
    TreeNodeFilter,
)
from netbox.models.features import ChangeLoggingMixin
from users.constants import TOKEN_PREFIX
from users.models import ObjectPermission, Token, User
from utilities.api import get_graphql_type_for_model

from .base import ModelTestCase, TestCase
from .query_counts import assert_expected_query_count
from .utils import disable_logging, disable_warnings, get_random_string

__all__ = (
    'APITestCase',
    'APIViewTestCases',
    'GraphQLFilterTest',
    'GraphQLQueryTest',
)


@dataclass(frozen=True)
class GraphQLFilterTest:
    """
    Declarative GraphQL filter test case for APIViewTestCases.GraphQLTestCase.

    ``filters`` is the raw content to place inside the GraphQL ``filters`` input,
    e.g. ``name: {i_contains: "site"}``.

    ``expected`` may be a callable accepting the model queryset, an ORM filter
    dict, a queryset, an iterable of model instances, or an iterable of object
    IDs. When omitted, the test only asserts that the filter returns at least one
    result; this preserves compatibility with the legacy ``graphql_filter``
    attribute.
    """
    name: str
    filters: str
    expected: object = None
    permissions: tuple[str, ...] = ()


@dataclass(frozen=True)
class GraphQLQueryTest:
    """
    Declarative GraphQL query test case for model-specific complex queries.

    ``assert_result`` is called as ``assert_result(testcase, data)`` where
    ``testcase`` is the running ``GraphQLTestCase`` instance (use it for
    ``testcase.assertEqual`` etc.) and ``data`` is the decoded GraphQL
    ``data`` object (the inner ``response.json()['data']``, not the full HTTP
    response).
    """
    name: str
    query: str
    assert_result: Callable
    permissions: tuple[str, ...] = ()


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
        self.header = {'HTTP_AUTHORIZATION': f'Bearer {TOKEN_PREFIX}{self.token.key}.{self.token.token}'}

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
            response = self.client.get(url, **self.header)
            self.assertHttpStatus(response, status.HTTP_200_OK)

            # Verify ETag header is present for objects with timestamps
            if issubclass(self.model, ChangeLoggingMixin):
                self.assertIn('ETag', response, "ETag header missing from detail response")

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

            self.assertHttpStatus(response, status.HTTP_200_OK)
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
            with assert_expected_query_count(self, 'api_list_objects'):
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

            self.add_related_view_permissions(self.create_data[0])

            data = copy.deepcopy(self.create_data[0])

            # If supported, add a changelog message
            if issubclass(self.model, ChangeLoggingMixin):
                data['changelog_message'] = get_random_string(10)

            initial_count = self._get_queryset().count()
            response = self.client.post(self._get_list_url(), data, format='json', **self.header)
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
            if issubclass(self.model, ChangeLoggingMixin):
                objectchange = ObjectChange.objects.get(
                    changed_object_type=ContentType.objects.get_for_model(instance),
                    changed_object_id=instance.pk,
                    action=ObjectChangeActionChoices.ACTION_CREATE,
                )
                self.assertObjectChange(objectchange, action=ObjectChangeActionChoices.ACTION_CREATE,
                    message=data['changelog_message'])

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

            self.add_related_view_permissions(*self.create_data)

            # If supported, add a changelog message
            changelog_message = get_random_string(10)
            if issubclass(self.model, ChangeLoggingMixin):
                for obj_data in self.create_data:
                    obj_data['changelog_message'] = changelog_message

            initial_count = self._get_queryset().count()
            response = self.client.post(self._get_list_url(), self.create_data, format='json', **self.header)
            self.assertHttpStatus(response, status.HTTP_201_CREATED)
            self.assertEqual(len(response.data), len(self.create_data))
            self.assertEqual(self._get_queryset().count(), initial_count + len(self.create_data))
            for i, obj in enumerate(response.data):
                for field in self.create_data[i]:
                    if field in ('changelog_message', 'add_tags', 'remove_tags'):
                        # Write-only field
                        continue
                    if field not in self.validation_excluded_fields:
                        self.assertIn(field, obj, f"Bulk create field '{field}' missing from object {i} in response")
            for i, obj in enumerate(response.data):
                self.assertInstanceEqual(
                    self._get_queryset().get(pk=obj['id']),
                    self.create_data[i],
                    exclude=self.validation_excluded_fields,
                    api=True
                )

            # Verify ObjectChange creation
            if issubclass(self.model, ChangeLoggingMixin):
                id_list = [
                    obj['id'] for obj in response.data
                ]
                objectchanges = ObjectChange.objects.filter(
                    changed_object_type=ContentType.objects.get_for_model(self.model),
                    changed_object_id__in=id_list,
                    action=ObjectChangeActionChoices.ACTION_CREATE,
                )
                self.assertEqual(len(objectchanges), len(self.create_data))
                for oc in objectchanges:
                    self.assertObjectChange(oc, action=ObjectChangeActionChoices.ACTION_CREATE,
                        message=changelog_message)

    class UpdateObjectViewTestCase(APITestCase):
        update_data = {}
        bulk_update_data = None
        bulk_update_invalid_data = None
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

            self.add_related_view_permissions(update_data)

            data = copy.deepcopy(update_data)

            # If supported, add a changelog message
            if issubclass(self.model, ChangeLoggingMixin):
                data['changelog_message'] = get_random_string(10)

            response = self.client.patch(url, data, format='json', **self.header)
            self.assertHttpStatus(response, status.HTTP_200_OK)
            instance.refresh_from_db()
            self.assertInstanceEqual(
                instance,
                data,
                exclude=self.validation_excluded_fields,
                api=True
            )

            # Verify ObjectChange creation
            if hasattr(self.model, 'to_objectchange'):
                objectchange = ObjectChange.objects.get(
                    changed_object_type=ContentType.objects.get_for_model(instance),
                    changed_object_id=instance.pk
                )
                self.assertObjectChange(objectchange, action=ObjectChangeActionChoices.ACTION_UPDATE,
                    message=data['changelog_message'])

        def test_update_object_with_etag(self):
            """
            PATCH an object using a valid If-Match ETag → expect 200.
            PATCH again with the now-stale ETag → expect 412.
            """
            if not issubclass(self.model, ChangeLoggingMixin):
                self.skipTest("Model does not support ETags")

            self.add_permissions(
                f'{self.model._meta.app_label}.view_{self.model._meta.model_name}',
                f'{self.model._meta.app_label}.change_{self.model._meta.model_name}',
            )
            instance = self._get_queryset().first()
            url = self._get_detail_url(instance)
            update_data = self.update_data or getattr(self, 'create_data')[0]
            self.add_related_view_permissions(update_data)

            # Fetch current ETag
            get_response = self.client.get(url, **self.header)
            self.assertHttpStatus(get_response, status.HTTP_200_OK)
            etag = get_response.get('ETag')
            self.assertIsNotNone(etag, "No ETag returned by GET")

            # PATCH with correct ETag → 200
            response = self.client.patch(
                url, update_data, format='json',
                **{**self.header, 'HTTP_IF_MATCH': etag}
            )
            self.assertHttpStatus(response, status.HTTP_200_OK)
            new_etag = response.get('ETag')
            self.assertIsNotNone(new_etag)
            self.assertNotEqual(etag, new_etag)  # ETag must change after update

            # PATCH with the old (stale) ETag → 412
            with disable_warnings('django.request'):
                response = self.client.patch(
                    url, update_data, format='json',
                    **{**self.header, 'HTTP_IF_MATCH': etag}
                )
            self.assertHttpStatus(response, status.HTTP_412_PRECONDITION_FAILED)

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

            self.add_related_view_permissions(self.bulk_update_data)

            id_list = list(self._get_queryset().values_list('id', flat=True)[:3])
            self.assertEqual(len(id_list), 3, "Insufficient number of objects to test bulk update")
            data = [
                {'id': id, **self.bulk_update_data} for id in id_list
            ]

            # If supported, add a changelog message
            changelog_message = get_random_string(10)
            if issubclass(self.model, ChangeLoggingMixin):
                for obj_data in data:
                    obj_data['changelog_message'] = changelog_message

            response = self.client.patch(self._get_list_url(), data, format='json', **self.header)
            self.assertHttpStatus(response, status.HTTP_200_OK)
            for i, obj in enumerate(response.data):
                for field in self.bulk_update_data:
                    if field in ('changelog_message', 'add_tags', 'remove_tags'):
                        # Write-only field
                        continue
                    self.assertIn(field, obj, f"Bulk update field '{field}' missing from object {i} in response")
            for instance in self._get_queryset().filter(pk__in=id_list):
                self.assertInstanceEqual(instance, self.bulk_update_data, api=True)

            # Verify ObjectChange creation
            if issubclass(self.model, ChangeLoggingMixin):
                objectchanges = ObjectChange.objects.filter(
                    changed_object_type=ContentType.objects.get_for_model(self.model),
                    changed_object_id__in=id_list
                )
                self.assertEqual(len(objectchanges), len(data))
                for oc in objectchanges:
                    self.assertObjectChange(oc, action=ObjectChangeActionChoices.ACTION_UPDATE,
                        message=changelog_message)

        def test_bulk_update_objects_validation_error(self):
            """
            PATCH a set of objects where one fails validation. Verify the structured per-object error
            response and that no objects are modified (atomic rollback).
            """
            if self.bulk_update_data is None or self.bulk_update_invalid_data is None:
                self.skipTest('Bulk update data not set')

            obj_perm = ObjectPermission(name='Test permission', actions=['change'])
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

            id_list = list(self._get_queryset().values_list('id', flat=True)[:2])
            self.assertEqual(len(id_list), 2, 'Insufficient number of objects to test bulk update validation error')

            # First object: valid data; second: invalid data that must fail validation
            data = [
                {'id': id_list[0], **self.bulk_update_data},
                {'id': id_list[1], **self.bulk_update_invalid_data},
            ]

            # Snapshot field values before the request so we can verify atomicity afterward
            instance0_before = self._get_queryset().get(pk=id_list[0])

            response = self.client.patch(self._get_list_url(), data, format='json', **self.header)

            self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
            self.assertIn('detail', response.data)
            self.assertIn('results', response.data)
            self.assertEqual(len(response.data['results']), 2)
            self.assertEqual(response.data['results'][0]['id'], id_list[0])
            self.assertNotIn('errors', response.data['results'][0])
            self.assertEqual(response.data['results'][1]['id'], id_list[1])
            self.assertIn('errors', response.data['results'][1])

            # Verify atomicity: object 0 passed validation but must not have been modified
            instance0_after = self._get_queryset().get(pk=id_list[0])
            for field in self.bulk_update_data:
                if field in ('changelog_message', 'add_tags', 'remove_tags'):
                    continue
                self.assertEqual(
                    getattr(instance0_after, field, None),
                    getattr(instance0_before, field, None),
                    f'Field {field!r} of object {id_list[0]} was modified — atomic rollback may be broken',
                )

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

            data = {}

            # If supported, add a changelog message
            if issubclass(self.model, ChangeLoggingMixin):
                data['changelog_message'] = get_random_string(10)

            response = self.client.delete(url, data, **self.header)
            self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
            self.assertFalse(self._get_queryset().filter(pk=instance.pk).exists())

            # Verify ObjectChange creation
            if hasattr(self.model, 'to_objectchange'):
                objectchange = ObjectChange.objects.get(
                    changed_object_type=ContentType.objects.get_for_model(instance),
                    changed_object_id=instance.pk
                )
                self.assertObjectChange(objectchange, action=ObjectChangeActionChoices.ACTION_DELETE,
                    message=data['changelog_message'])

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

            # If supported, add a changelog message
            changelog_message = get_random_string(10)
            if issubclass(self.model, ChangeLoggingMixin):
                for obj_data in data:
                    obj_data['changelog_message'] = changelog_message

            initial_count = self._get_queryset().count()
            response = self.client.delete(self._get_list_url(), data, format='json', **self.header)
            self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
            self.assertEqual(self._get_queryset().count(), initial_count - 3)

            # Verify ObjectChange creation
            if issubclass(self.model, ChangeLoggingMixin):
                objectchanges = ObjectChange.objects.filter(
                    changed_object_type=ContentType.objects.get_for_model(self.model),
                    changed_object_id__in=id_list
                )
                self.assertEqual(len(objectchanges), len(data))
                for oc in objectchanges:
                    self.assertObjectChange(oc, action=ObjectChangeActionChoices.ACTION_DELETE,
                        message=changelog_message)

    class GraphQLTestCase(APITestCase):
        graphql_auto_filter_tests = True
        graphql_auto_filter_exclude = ()

        # Cap fields per lookup kind to keep test counts balanced across kinds
        # (string fields shouldn't crowd out numeric/date/array fields).
        graphql_auto_filter_fields_per_kind = 2

        # Fail when auto mode is on and no tests were generated.
        graphql_auto_filter_required = True

        # Gate the negative constrained-permission check in the get/list tests; the positive
        # query still runs. Set False for types not enforcing object permissions (e.g. no BaseObjectType).
        graphql_object_permission_assertions = True

        # Additional explicit-list filter cases as GraphQLFilterTest instances.
        graphql_filter_tests = ()

        # Additional full-query cases (e.g. nested filters) as GraphQLQueryTest instances.
        graphql_query_tests = ()

        # GraphQL type under test. Defaults to the type derived from `model` via the naming
        # convention; set explicitly when the convention does not apply (e.g. plugin types).
        type_class = None

        # Exclude this test case from GraphQL schema coverage.
        graphql_test_exempt = False

        @classmethod
        def get_graphql_type_class(cls):
            if getattr(cls, 'type_class', None) is not None:
                return cls.type_class
            model = getattr(cls, 'model', None)
            if model is None:
                return None
            return get_graphql_type_for_model(model)

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
            type_class = self.get_graphql_type_class()

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

        @staticmethod
        def _graphql_literal(value):
            """
            Render a Python value as a GraphQL literal.
            """
            if value is None:
                return 'null'
            if isinstance(value, bool):
                return 'true' if value else 'false'
            if isinstance(value, (int, float)):
                return str(value)
            if isinstance(value, Decimal):
                return str(float(value))
            if isinstance(value, (list, tuple)):
                items = ', '.join(
                    APIViewTestCases.GraphQLTestCase._graphql_literal(v) for v in value
                )
                return f'[{items}]'
            if isinstance(value, str):
                return json.dumps(value)

            return json.dumps(str(value))

        def _render_graphql_filter_value(self, params):
            """
            Render the legacy graphql_filter dict value to a GraphQL filter value.
            """
            if isinstance(params, str):
                return params

            if not isinstance(params, dict):
                return self._graphql_literal(params)

            lookup = params.get('lookup')
            value = params['value']

            if lookup:
                return f'{{{lookup}: {self._graphql_literal(value)}}}'

            return self._graphql_literal(value)

        def _build_graphql_filter_string(self, **filters):
            if not filters:
                return ''

            filter_expressions = [
                f'{field_name}: {self._render_graphql_filter_value(params)}'
                for field_name, params in filters.items()
            ]

            return f'(filters: {{{", ".join(filter_expressions)}}})'

        def _build_filtered_query(self, name, **filters):
            """
            Create a filtered query: i.e. device_list(filters: {name: {i_contains: "akron"}}){.
            """
            filter_string = self._build_graphql_filter_string(**filters)

            return self._build_query_with_filter(name, filter_string)

        def _build_graphql_id_list_query(self, name, filters):
            filter_string = f'(filters: {{{filters}}})' if filters else ''
            selection = 'id' if self._graphql_type_exposes_id() else '__typename'

            return f"""
            {{
              {name}{filter_string} {{
                {selection}
              }}
            }}
            """

        def _graphql_type_exposes_id(self):
            """
            Return True when the model's GraphQL type exposes ``id`` as a
            queryable selection. Some NetBox types (e.g. Notification,
            Subscription) omit ``id`` from the output type; for those, the
            assertion path falls back to length-only comparison.
            """
            type_class = self.get_graphql_type_class()
            strawberry_definition = getattr(type_class, '__strawberry_definition__', None)
            if strawberry_definition is None:
                return False
            return any(field.name == 'id' for field in strawberry_definition.fields)

        def _get_model_graphql_filter_class(self, model=None):
            """
            Return the model's GraphQL filter class, if one follows NetBox's
            conventional <app>.graphql.filters.<Model>Filter path. ``None`` if
            the filter module (or any of its parent packages) is absent or the
            class is not present in the module. Import errors originating
            inside an existing filter module are re-raised.
            """
            model = model or self.model
            module_path = f'{model._meta.app_label}.graphql.filters'
            class_name = f'{model.__name__}Filter'

            try:
                module = importlib.import_module(module_path)
            except ModuleNotFoundError as exc:
                # Treat both "<app>.graphql.filters" absent and any missing
                # parent (e.g. "<app>.graphql" or "<app>") as "no conventional
                # filter class". Real ImportErrors from inside an existing
                # filter module still propagate.
                if exc.name == module_path or module_path.startswith(f'{exc.name}.'):
                    return None
                raise

            return getattr(module, class_name, None)

        def _get_graphql_filter_field_names(self):
            """
            Return the names exposed by the model's GraphQL filter input, sourced
            only from the conventional <app>.graphql.filters.<Model>Filter path.
            """
            filter_class = self._get_model_graphql_filter_class()
            if filter_class is None:
                return set()

            return self._collect_filter_class_annotation_names(filter_class)

        @staticmethod
        def _collect_filter_class_annotation_names(filter_class):
            field_names = set()
            for cls in reversed(getattr(filter_class, '__mro__', ())):
                field_names.update(
                    field_name for field_name in getattr(cls, '__annotations__', {})
                    if not field_name.startswith('_')
                )
            return field_names

        def _assert_graphql_filter_class_present(self, filter_fields, handwritten_tests=()):
            """
            Raise when the model has no discoverable filter class or the class
            declares no fields. Skipped when auto-filter generation is disabled,
            the per-model opt-out attribute is set, or hand-written (legacy or
            explicit) filter tests are declared for the model.
            """
            if handwritten_tests:
                return
            if not getattr(self, 'graphql_auto_filter_required', True):
                return
            if not getattr(self, 'graphql_auto_filter_tests', True):
                return

            label = self.model._meta.label
            path = f'{self.model._meta.app_label}.graphql.filters.{self.model.__name__}Filter'

            filter_class = self._get_model_graphql_filter_class()
            self.assertIsNotNone(
                filter_class,
                f'No GraphQL filter class found for {label} at {path}. '
                f'Set graphql_auto_filter_required = False on this test case if intentional.'
            )
            self.assertTrue(
                filter_fields,
                f'GraphQL filter class for {label} declares no fields. '
                f'Set graphql_auto_filter_required = False on this test case if intentional.'
            )

        def _get_nonempty_field_value(self, field):
            queryset = self._get_queryset()

            if getattr(field, 'null', False):
                queryset = queryset.exclude(**{f'{field.name}__isnull': True})

            if isinstance(field, (models.CharField, models.TextField)):
                queryset = queryset.exclude(**{field.name: ''})

            return queryset.values_list(field.name, flat=True).first()

        def _get_model_field_for_filter_field(self, field_name):
            """
            Find the Django model field matching a filter field name. Filter
            fields are declared with either the model field name (e.g. `name`)
            or the FK attname (e.g. `tenant_id`).
            """
            for field in self.model._meta.fields:
                if field.name == field_name or getattr(field, 'attname', None) == field_name:
                    return field
            return None

        def _iter_filter_class_annotations(self, filter_class):
            """
            Yield (field_name, annotation) pairs for the filter class, walking
            its MRO so inherited fields surface. Subclass annotations override
            inherited ones (private `_`-prefixed names are skipped).
            """
            annotations = {}
            for cls in reversed(filter_class.__mro__):
                annotations.update({
                    name: ann for name, ann in getattr(cls, '__annotations__', {}).items()
                    if not name.startswith('_')
                })
            yield from annotations.items()

        @staticmethod
        def _unwrap_filter_annotation(annotation):
            """
            Strip ``X | None`` / ``Optional[X]`` and ``Annotated[X, ...]``
            layers. Resolve `strawberry.lazy('...')` metadata so lazily-annotated
            lookup types (e.g. ``Annotated['FloatLookup', strawberry.lazy('mod')] | None``)
            are returned as the actual class. When an ``Annotated`` layer carries
            multiple metadata entries, the first ``module``-bearing entry wins.
            Returns None when the inner type cannot be resolved.
            """
            if annotation is None:
                return None

            lazy_module = None
            lazy_package = None
            # Cap iterations at 8: typical NetBox annotations nest at most 3 layers
            # (Union > Annotated > ForwardRef). 8 is a generous safety net to
            # prevent infinite loops on pathological / future annotation shapes.
            for _ in range(8):
                origin = typing.get_origin(annotation)
                args = typing.get_args(annotation)

                if origin in (typing.Union, types.UnionType):
                    non_none = [a for a in args if a is not type(None)]
                    if len(non_none) != 1:
                        return None
                    annotation = non_none[0]
                    continue

                if hasattr(annotation, '__metadata__'):
                    for meta in annotation.__metadata__:
                        module_name = getattr(meta, 'module', None)
                        if module_name:
                            lazy_module = module_name
                            # strawberry.lazy('.relative') records the anchor package
                            # needed to resolve the leading-dot module path.
                            lazy_package = getattr(meta, 'package', None)
                            break
                    inner = args[0] if args else None
                    if inner is None:
                        return None
                    annotation = inner
                    continue

                break

            if isinstance(annotation, (str, typing.ForwardRef)):
                if lazy_module is None:
                    return None
                name = annotation.__forward_arg__ if isinstance(annotation, typing.ForwardRef) else annotation
                # Resolve via import_module(module, package) rather than import_string()
                # so relative lazy modules (e.g. strawberry.lazy('.filters')) resolve
                # against their anchor package, as strawberry itself does.
                try:
                    module = importlib.import_module(lazy_module, lazy_package)
                    return getattr(module, name)
                except (ImportError, AttributeError):
                    return None

            return annotation

        @classmethod
        def _classify_filter_annotation(cls, annotation):
            """
            Resolve a filter field annotation to a (kind, kind_arg) tuple keyed
            on the declared GraphQL lookup type. Returns (None, None) for
            annotations the dispatcher does not handle (those fields are
            silently skipped).
            """
            annotation = cls._unwrap_filter_annotation(annotation)
            if annotation is None or isinstance(annotation, str):
                return None, None

            if annotation is strawberry.ID:
                return 'id', None

            origin = typing.get_origin(annotation)
            target = origin if isinstance(origin, type) else annotation
            type_args = typing.get_args(annotation)

            if not isinstance(target, type):
                return None, None

            if target in (IntegerLookup, BigIntegerLookup, FloatLookup):
                return 'numeric', target

            # TreeNodeFilter schema requires {id, match_type}; skip auto-emit.
            if target is TreeNodeFilter:
                return None, None

            if issubclass(target, (DateFilterLookup, DatetimeFilterLookup, TimeFilterLookup)):
                return 'date_lookup', None

            if target is RangeLookup or issubclass(target, RangeLookup):
                return 'range_lookup', type_args[0] if type_args else None

            if issubclass(target, ArrayLookup):
                return 'array_lookup', None
            if target is IntegerRangeArrayLookup or issubclass(target, IntegerRangeArrayLookup):
                return 'range_array_lookup', None
            if target is JSONFilter:
                # JSONFilter requires explicit (path, typed lookup); no general auto shape.
                return None, None

            if issubclass(target, StrFilterLookup):
                return 'str_lookup', None
            if issubclass(target, ComparisonFilterLookup):
                return 'comparison_lookup', type_args[0] if type_args else None
            if issubclass(target, FilterLookup):
                return 'filter_lookup', type_args[0] if type_args else None
            # Enum-typed BaseFilterLookup needs an enum literal; skip auto-emit.
            if issubclass(target, BaseFilterLookup):
                return None, None

            return None, None

        def _emit_id_filter_tests(self, field_name, _kind_arg):
            if field_name == 'id':
                instance = self._get_queryset().first()
                if instance is None:
                    return
                yield GraphQLFilterTest(
                    name='id__exact',
                    filters=f'id: {self._graphql_literal(str(instance.pk))}',
                    expected=lambda qs, pk=instance.pk: qs.filter(pk=pk),
                )
                return

            model_field = self._get_model_field_for_filter_field(field_name)
            if model_field is None or not isinstance(model_field, models.ForeignKey):
                return
            queryset = self._get_queryset().exclude(**{f'{model_field.name}__isnull': True})
            value = queryset.values_list(model_field.attname, flat=True).first()
            if value is None:
                return
            yield GraphQLFilterTest(
                name=f'{field_name}__exact',
                filters=f'{field_name}: {self._graphql_literal(str(value))}',
                expected=lambda qs, attname=model_field.attname, v=value: qs.filter(**{attname: v}),
            )

        def _emit_str_lookup_filter_tests(self, field_name, _kind_arg):
            model_field = self._get_model_field_for_filter_field(field_name)
            if model_field is None:
                return
            value = self._get_nonempty_field_value(model_field)
            if value in (None, ''):
                return
            value = str(value)
            token = max(1, min(3, len(value)))
            lookups = (
                ('exact', 'exact', value),
                ('i_contains', 'icontains', value[:token]),
                ('i_starts_with', 'istartswith', value[:token]),
                ('i_ends_with', 'iendswith', value[-token:]),
            )
            for lookup, orm_lookup, filter_value in lookups:
                yield GraphQLFilterTest(
                    name=f'{field_name}__{lookup}',
                    filters=f'{field_name}: {{{lookup}: {self._graphql_literal(filter_value)}}}',
                    expected=(
                        lambda qs, fn=model_field.name, ol=orm_lookup, v=filter_value:
                        qs.filter(**{f'{fn}__{ol}': v})
                    ),
                )

        def _emit_filter_lookup_filter_tests(self, field_name, type_arg):
            model_field = self._get_model_field_for_filter_field(field_name)
            if model_field is None:
                return
            value = self._get_nonempty_field_value(model_field)
            if value is None:
                return
            if type_arg is bool or isinstance(value, bool):
                yield GraphQLFilterTest(
                    name=f'{field_name}__exact',
                    filters=f'{field_name}: {{exact: {self._graphql_literal(value)}}}',
                    expected=lambda qs, fn=model_field.name, v=value: qs.filter(**{fn: v}),
                )
                return
            yield GraphQLFilterTest(
                name=f'{field_name}__exact',
                filters=f'{field_name}: {{exact: {self._graphql_literal(value)}}}',
                expected=lambda qs, fn=model_field.name, v=value: qs.filter(**{f'{fn}__exact': v}),
            )

        def _emit_comparison_lookup_filter_tests(self, field_name, _type_arg):
            model_field = self._get_model_field_for_filter_field(field_name)
            if model_field is None:
                return
            value = self._get_nonempty_field_value(model_field)
            if value is None:
                return
            yield GraphQLFilterTest(
                name=f'{field_name}__exact',
                filters=f'{field_name}: {{exact: {self._graphql_literal(value)}}}',
                expected=lambda qs, fn=model_field.name, v=value: qs.filter(**{f'{fn}__exact': v}),
            )

        def _emit_numeric_filter_tests(self, field_name, _type_arg):
            # NetBox numeric wrapper: {filter_lookup: {exact: N}}.
            model_field = self._get_model_field_for_filter_field(field_name)
            if model_field is None:
                return
            if isinstance(model_field, ArrayField):
                return
            value = self._get_nonempty_field_value(model_field)
            if value is None:
                return
            if isinstance(value, Decimal):
                value = float(value)
            yield GraphQLFilterTest(
                name=f'{field_name}__filter_lookup__exact',
                filters=(
                    f'{field_name}: {{filter_lookup: '
                    f'{{exact: {self._graphql_literal(value)}}}}}'
                ),
                expected=lambda qs, fn=model_field.name, v=value: qs.filter(**{f'{fn}__exact': v}),
            )

        def _emit_date_lookup_filter_tests(self, field_name, _kind_arg):
            model_field = self._get_model_field_for_filter_field(field_name)
            if model_field is None:
                return
            value = self._get_nonempty_field_value(model_field)
            if value is None:
                return
            iso_value = value.isoformat() if hasattr(value, 'isoformat') else str(value)
            yield GraphQLFilterTest(
                name=f'{field_name}__exact',
                filters=f'{field_name}: {{exact: "{iso_value}"}}',
                expected=lambda qs, fn=model_field.name, v=value: qs.filter(**{fn: v}),
            )

        def _emit_range_lookup_filter_tests(self, field_name, _kind_arg):
            model_field = self._get_model_field_for_filter_field(field_name)
            if model_field is None:
                return
            aggregates = self._get_queryset().aggregate(
                _min=models.Min(model_field.name), _max=models.Max(model_field.name),
            )
            start, end = aggregates['_min'], aggregates['_max']
            if start is None or end is None or start == end:
                return
            yield GraphQLFilterTest(
                name=f'{field_name}__range_lookup',
                filters=(
                    f'{field_name}: {{range_lookup: '
                    f'{{start: {self._graphql_literal(start)}, end: {self._graphql_literal(end)}}}}}'
                ),
                expected=(
                    lambda qs, fn=model_field.name, lo=start, hi=end:
                    qs.filter(**{f'{fn}__gte': lo, f'{fn}__lte': hi})
                ),
            )

        def _emit_array_lookup_filter_tests(self, field_name, _kind_arg):
            model_field = self._get_model_field_for_filter_field(field_name)
            if model_field is None:
                return
            if not isinstance(model_field, ArrayField):
                return
            queryset = self._get_queryset().exclude(**{field_name: []})
            sample = queryset.values_list(field_name, flat=True).first()
            if not sample:
                return
            element = sample[0]
            yield GraphQLFilterTest(
                name=f'{field_name}__contains',
                filters=(
                    f'{field_name}: {{contains: [{self._graphql_literal(element)}]}}'
                ),
                expected=(
                    lambda qs, fn=model_field.name, v=element: qs.filter(**{f'{fn}__contains': [v]})
                ),
            )

        def _emit_range_array_lookup_filter_tests(self, field_name, _kind_arg):
            model_field = self._get_model_field_for_filter_field(field_name)
            if model_field is None:
                return
            queryset = self._get_queryset().exclude(**{f'{field_name}__isnull': True})
            sample = queryset.values_list(field_name, flat=True).first()
            if not sample:
                return
            first_range = sample[0]
            lower = getattr(first_range, 'lower', None)
            if lower is None:
                return
            yield GraphQLFilterTest(
                name=f'{field_name}__contains',
                filters=f'{field_name}: {{contains: {self._graphql_literal(lower)}}}',
                expected=(
                    lambda qs, fn=model_field.name, v=lower: qs.filter(**{f'{fn}__range_contains': v})
                ),
            )

        def _iter_auto_graphql_filter_tests(self):
            if not getattr(self, 'graphql_auto_filter_tests', True):
                return

            filter_class = self._get_model_graphql_filter_class()
            if filter_class is None:
                return

            exclude = set(getattr(self, 'graphql_auto_filter_exclude', ()))
            per_kind = self.graphql_auto_filter_fields_per_kind

            # Bucket eligible fields by lookup kind so per-kind budgeting balances coverage.
            by_kind: dict[str, list[tuple[str, object]]] = {}
            for field_name, annotation in self._iter_filter_class_annotations(filter_class):
                if field_name in exclude:
                    continue
                kind, kind_arg = self._classify_filter_annotation(annotation)
                if kind is None:
                    continue
                by_kind.setdefault(kind, []).append((field_name, kind_arg))

            # Emit per-kind; the cap counts SUCCESSFUL emissions, not candidate fields, so
            # early null/empty fields don't shadow later fields with usable fixture data.
            for kind, fields in by_kind.items():
                emitter = getattr(self, f'_emit_{kind}_filter_tests', None)
                if emitter is None:
                    continue

                emitted_fields = 0
                for field_name, kind_arg in fields:
                    tests = list(emitter(field_name, kind_arg))
                    if not tests:
                        continue
                    yield from tests
                    emitted_fields += 1
                    if emitted_fields >= per_kind:
                        break

        def _iter_legacy_graphql_filter_tests(self):
            if not hasattr(self, 'graphql_filter'):
                return

            filter_expressions = [
                f'{field_name}: {self._render_graphql_filter_value(params)}'
                for field_name, params in self.graphql_filter.items()
            ]

            yield GraphQLFilterTest(
                name='graphql_filter',
                filters=', '.join(filter_expressions),
            )

        def _coerce_graphql_filter_test(self, filter_test):
            if isinstance(filter_test, GraphQLFilterTest):
                return filter_test

            filter_test = dict(filter_test)
            if 'filter' in filter_test and 'filters' not in filter_test:
                filter_test['filters'] = filter_test.pop('filter')

            return GraphQLFilterTest(**filter_test)

        def _iter_explicit_graphql_filter_tests(self):
            for filter_test in getattr(self, 'graphql_filter_tests', ()):
                yield self._coerce_graphql_filter_test(filter_test)

        def _get_expected_id_set(self, filter_test):
            expected = filter_test.expected

            if callable(expected):
                expected = expected(self._get_queryset())

            if isinstance(expected, dict):
                expected = self._get_queryset().filter(**expected)

            if hasattr(expected, 'values_list'):
                values = expected.distinct().values_list('pk', flat=True)
            else:
                values = [getattr(value, 'pk', value) for value in expected]

            return {str(value) for value in values}

        def _assert_graphql_filter_test(self, url, field_name, filter_test):
            query = self._build_graphql_id_list_query(field_name, filter_test.filters)

            for permission in filter_test.permissions:
                self.add_permissions(permission)

            response = self.client.post(url, data={'query': query}, format="json", **self.header)
            self.assertHttpStatus(response, status.HTTP_200_OK)

            data = json.loads(response.content)
            self.assertNotIn('errors', data)

            results = data['data'][field_name]

            if filter_test.expected is None:
                self.assertGreater(len(results), 0)
                return

            expected_ids = self._get_expected_id_set(filter_test)

            self.assertGreater(
                len(expected_ids), 0,
                msg=(
                    f'{self.model._meta.label}: filter "{filter_test.name}" produced an empty '
                    f'expected set; the test would tautologically pass. Adjust fixtures or the '
                    f'filter so the expected ORM queryset is non-empty.'
                ),
            )

            if self._graphql_type_exposes_id():
                result_ids = [str(result['id']) for result in results]
                self.assertEqual(
                    set(result_ids), expected_ids,
                    msg=f'{self.model._meta.label}: filter "{filter_test.name}" ID set mismatch',
                )

            self.assertEqual(
                len(results), len(expected_ids),
                msg=(
                    f'{self.model._meta.label}: filter "{filter_test.name}" result count mismatch '
                    f'(GraphQL type does not expose id; comparing by length).'
                ),
            )

        def _coerce_graphql_query_test(self, query_test):
            if isinstance(query_test, GraphQLQueryTest):
                return query_test

            query_test = dict(query_test)
            if 'assertion' in query_test and 'assert_result' not in query_test:
                query_test['assert_result'] = query_test.pop('assertion')

            return GraphQLQueryTest(**query_test)

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

            if self.graphql_object_permission_assertions:
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

            if self.graphql_object_permission_assertions:
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

        def _assert_graphql_filter_tests_exist(self, auto_tests, legacy_tests, explicit_tests):
            """
            Fail loudly when auto mode is required and no GraphQL filter tests
            (auto, legacy, or explicit) exist for the current model.
            """
            if (
                getattr(self, 'graphql_auto_filter_tests', True)
                and getattr(self, 'graphql_auto_filter_required', True)
                and not auto_tests
                and not legacy_tests
                and not explicit_tests
            ):
                self.fail(
                    f'No GraphQL filter tests were generated for {self.model._meta.label}. '
                    f'Set graphql_auto_filter_required = False or add explicit graphql_filter_tests '
                    f'if intentional.'
                )

        @override_settings(LOGIN_REQUIRED=True)
        def test_graphql_filter_objects(self):
            legacy_tests = list(self._iter_legacy_graphql_filter_tests())
            explicit_tests = list(self._iter_explicit_graphql_filter_tests())

            filter_fields = self._get_graphql_filter_field_names()
            self._assert_graphql_filter_class_present(
                filter_fields, handwritten_tests=[*legacy_tests, *explicit_tests]
            )

            auto_tests = list(self._iter_auto_graphql_filter_tests())

            self._assert_graphql_filter_tests_exist(auto_tests, legacy_tests, explicit_tests)

            filter_tests = [*auto_tests, *legacy_tests, *explicit_tests]
            if not filter_tests:
                return

            url = reverse('graphql')
            field_name = f'{self._get_graphql_base_name()}_list'

            # Add object-level permission
            obj_perm = ObjectPermission(
                name='Test permission',
                actions=['view']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

            for filter_test in filter_tests:
                with self.subTest(filter=filter_test.name):
                    self._assert_graphql_filter_test(url, field_name, filter_test)

        @override_settings(LOGIN_REQUIRED=True)
        def test_graphql_extra_queries(self):
            query_tests = [
                self._coerce_graphql_query_test(query_test)
                for query_test in getattr(self, 'graphql_query_tests', ())
            ]

            if not query_tests:
                return

            url = reverse('graphql')

            # Add object-level permission for this model. Additional permissions
            # required by the query can be declared on the GraphQLQueryTest.
            obj_perm = ObjectPermission(
                name='Test permission',
                actions=['view']
            )
            obj_perm.save()
            obj_perm.users.add(self.user)
            obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

            for query_test in query_tests:
                with self.subTest(query=query_test.name):
                    for permission in query_test.permissions:
                        self.add_permissions(permission)

                    response = self.client.post(url, data={'query': query_test.query}, format="json", **self.header)
                    self.assertHttpStatus(response, status.HTTP_200_OK)

                    data = json.loads(response.content)
                    self.assertNotIn('errors', data)
                    query_test.assert_result(self, data['data'])

    class APIViewTestCase(
        GetObjectViewTestCase,
        ListObjectsViewTestCase,
        CreateObjectViewTestCase,
        UpdateObjectViewTestCase,
        DeleteObjectViewTestCase,
        GraphQLTestCase
    ):
        pass

    class GraphQLSchemaCoverageTestCase(TestCase):
        """
        Assert every model-backed GraphQL type exposed as a root query field is covered by a
        concrete GraphQLTestCase subclass. Subclass this in a test module to run the audit.

        Scope is intentionally limited to types reachable as root query fields (e.g. ``site``,
        ``site_list``); these are exactly the types the detail/list GraphQLTestCase methods can
        exercise. Types reachable only as nested object fields are out of scope.
        """
        # Per-app test submodules to import so their GraphQLTestCase subclasses are defined.
        graphql_test_modules = ('test_api', 'test_graphql')

        # GraphQL type classes intentionally excluded from coverage.
        graphql_exempt_type_classes = ()

        def get_graphql_schema(self):
            # Imported lazily so importing this testing utility does not eagerly build the schema.
            from netbox.graphql.schema import schema
            return schema._schema

        def iter_test_module_names(self):
            # Import test modules only for apps exposing model-backed root query types;
            # coverage classes are expected to live with the app whose type they cover.
            app_labels = {model._meta.app_label for model in self.get_schema_type_classes().values()}
            for app_label in sorted(app_labels):
                app_config = apps.get_app_config(app_label)
                for module_name in self.graphql_test_modules:
                    yield f'{app_config.name}.tests.{module_name}'

        def import_graphql_test_modules(self):
            for module_name in self.iter_test_module_names():
                self.import_graphql_test_module(module_name)

        def import_graphql_test_module(self, module_name):
            try:
                importlib.import_module(module_name)
            except ModuleNotFoundError as exc:
                # A missing test module, or a missing parent package (e.g. `<app>.tests`),
                # is fine. An import error raised from inside an existing test module
                # should still fail loudly.
                if exc.name == module_name or module_name.startswith(f'{exc.name}.'):
                    return
                raise

        def unwrap_graphql_type(self, graphql_type):
            while isinstance(graphql_type, (GraphQLNonNull, GraphQLList)):
                graphql_type = graphql_type.of_type
            return graphql_type

        def get_schema_field_type_class(self, field):
            graphql_type = self.unwrap_graphql_type(field.type)
            if not isinstance(graphql_type, GraphQLObjectType):
                return None
            extensions = getattr(graphql_type, 'extensions', None) or {}
            definition = extensions.get(GraphQLCoreConverter.DEFINITION_BACKREF)
            return getattr(definition, 'origin', None)

        def get_graphql_type_model(self, type_class):
            django_definition = getattr(type_class, '__strawberry_django_definition__', None)
            return getattr(django_definition, 'model', None)

        def get_schema_type_classes(self):
            """Return {type_class: model} for every model-backed root query type (cached per instance)."""
            cached = getattr(self, '_schema_type_classes', None)
            if cached is not None:
                return cached
            type_classes = {}
            for field in self.get_graphql_schema().query_type.fields.values():
                type_class = self.get_schema_field_type_class(field)
                if type_class is None:
                    continue
                model = self.get_graphql_type_model(type_class)
                if model is None:
                    continue
                type_classes[type_class] = model
            self._schema_type_classes = type_classes
            return type_classes

        def iter_graphql_testcase_classes(self, base_class=None):
            base_class = base_class or APIViewTestCases.GraphQLTestCase
            for subclass in base_class.__subclasses__():
                yield subclass
                yield from self.iter_graphql_testcase_classes(subclass)

        def get_testcase_type_class(self, testcase):
            if getattr(testcase, 'graphql_test_exempt', False):
                return None
            try:
                return testcase.get_graphql_type_class()
            except GraphQLTypeNotFound as exc:
                model = getattr(testcase, 'model', None)
                model_label = model._meta.label if model is not None else 'unknown model'
                self.fail(
                    f'{testcase.__module__}.{testcase.__name__} sets model = {model_label} '
                    f'but no GraphQL type could be resolved. Set type_class if the type lives '
                    f'outside the conventional <app>.graphql.types.<Model>Type path, or set '
                    f'graphql_test_exempt = True if this test case should not count toward '
                    f'schema coverage. Original error: {exc}'
                )

        def get_testcase_type_classes(self):
            self.import_graphql_test_modules()
            type_classes = set()
            for testcase in self.iter_graphql_testcase_classes():
                type_class = self.get_testcase_type_class(testcase)
                if type_class is not None:
                    type_classes.add(type_class)
            return type_classes

        def format_type_class(self, type_class):
            model = self.get_graphql_type_model(type_class)
            label = f' ({model._meta.label})' if model is not None else ''
            return f'{type_class.__module__}.{type_class.__name__}{label}'

        def test_schema_types_have_graphql_test_coverage(self):
            """Every model-backed root query type is covered by a GraphQLTestCase."""
            expected = set(self.get_schema_type_classes())
            self.assertGreater(
                len(expected), 0,
                'No model-backed root query GraphQL types were discovered; schema '
                'introspection may have broken.'
            )
            actual = self.get_testcase_type_classes()
            exempt = set(self.graphql_exempt_type_classes)
            missing = sorted(self.format_type_class(tc) for tc in expected - actual - exempt)
            self.assertEqual(missing, [])
