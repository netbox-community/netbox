import uuid

from django.db.backends.postgresql.psycopg_any import NumericRange
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from dcim.api.serializers import RackSerializer
from netbox.api.exceptions import QuerySetNotOrdered
from netbox.api.fields import IntegerRangeSerializer, RelatedObjectCountField
from netbox.api.pagination import NetBoxPagination
from users.models import Token
from utilities.testing import APITestCase


class AppTestCase(APITestCase):

    def test_http_headers(self):
        response = self.client.get(reverse('api-root'), **self.header)

        # Check that all custom response headers are present and valid
        self.assertEqual(response.status_code, 200)
        request_id = response.headers['X-Request-ID']
        uuid.UUID(request_id)

    def test_root(self):
        url = reverse('api-root')
        response = self.client.get(f'{url}?format=api', **self.header)

        self.assertEqual(response.status_code, 200)

    def test_status(self):
        url = reverse('api-status')
        response = self.client.get(f'{url}?format=api', **self.header)

        self.assertEqual(response.status_code, 200)

    def test_authentication_check(self):
        url = reverse('api-authentication-check')

        # Test an unauthenticated request
        response = self.client.get(f'{url}')
        self.assertEqual(response.status_code, 403)

        # Test an authenticated request
        response = self.client.get(f'{url}', **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.user.pk)


class RelatedObjectCountFieldTestCase(TestCase):
    """
    RelatedObjectCountFields are populated by annotations applied to a viewset's queryset, which are only
    added when serializing an object via its own endpoint (including ?brief=1). They are never annotated when
    the object is rendered as a nested related object, so they must be omitted from nested representations to
    keep the generated OpenAPI schema honest. See #22154.
    """
    def test_count_field_omitted_when_nested(self):
        """A nested serializer must drop RelatedObjectCountFields (e.g. RackSerializer.device_count)."""
        serializer = RackSerializer(nested=True)
        count_fields = [
            name for name, field in serializer.fields.items() if isinstance(field, RelatedObjectCountField)
        ]
        self.assertEqual(count_fields, [])
        self.assertNotIn('device_count', serializer.fields)

    def test_count_field_retained_in_brief_mode(self):
        """?brief=1 (fields=brief_fields, not nested) must retain RelatedObjectCountFields."""
        serializer = RackSerializer(fields=RackSerializer.Meta.brief_fields)
        self.assertIn('device_count', serializer.fields)
        self.assertIsInstance(serializer.fields['device_count'], RelatedObjectCountField)


class NetBoxPaginationTestCase(TestCase):

    def setUp(self):
        self.paginator = NetBoxPagination()
        self.factory = RequestFactory()

    def _make_drf_request(self, path='/', query_params=None):
        """Helper to create a proper DRF Request object"""
        return Request(self.factory.get(path, query_params or {}))

    def test_raises_exception_for_unordered_queryset(self):
        """Should raise QuerySetNotOrdered for unordered QuerySet"""
        queryset = Token.objects.all().order_by()
        request = self._make_drf_request()

        with self.assertRaises(QuerySetNotOrdered) as cm:
            self.paginator.paginate_queryset(queryset, request)

        error_msg = str(cm.exception)
        self.assertIn("Paginating over an unordered queryset is unreliable", error_msg)
        self.assertIn("Ensure that a minimal ordering has been applied", error_msg)

    def test_allows_ordered_queryset(self):
        """Should not raise exception for ordered QuerySet"""
        queryset = Token.objects.all().order_by('created')
        request = self._make_drf_request()

        self.paginator.paginate_queryset(queryset, request)  # Should not raise exception

    def test_allows_non_queryset_iterables(self):
        """Should not raise exception for non-QuerySet iterables"""
        iterable = [1, 2, 3, 4, 5]
        request = self._make_drf_request()

        self.paginator.paginate_queryset(iterable, request)  # Should not raise exception

    def test_get_start_returns_none_when_absent(self):
        """get_start() returns None when start param is not in the request"""
        request = self._make_drf_request()
        self.assertIsNone(self.paginator.get_start(request))

    def test_get_start_returns_integer(self):
        """get_start() returns an integer when start param is present"""
        request = self._make_drf_request(query_params={'start': '42'})
        self.assertEqual(self.paginator.get_start(request), 42)

    def test_get_start_raises_for_negative(self):
        """get_start() raises ValidationError for negative values"""
        request = self._make_drf_request(query_params={'start': '-1'})
        with self.assertRaises(ValidationError):
            self.paginator.get_start(request)

    def test_cursor_and_offset_conflict_raises_validation_error(self):
        """paginate_queryset() raises ValidationError when both start and offset are specified"""
        queryset = Token.objects.all().order_by('created')
        request = self._make_drf_request(query_params={'start': '1', 'offset': '10'})
        with self.assertRaises(ValidationError):
            self.paginator.paginate_queryset(queryset, request)

    def test_cursor_and_ordering_conflict_raises_validation_error(self):
        """paginate_queryset() raises ValidationError when both start and ordering are specified"""
        queryset = Token.objects.all().order_by('created')
        request = self._make_drf_request(query_params={'start': '1', 'ordering': 'created'})
        with self.assertRaises(ValidationError):
            self.paginator.paginate_queryset(queryset, request)


class IntegerRangeSerializerTestCase(TestCase):

    def test_to_representation_emits_inclusive_bounds_for_non_canonical_range(self):
        """A NumericRange with bounds='[]' must serialize to its inclusive (lower, upper) pair."""
        serializer = IntegerRangeSerializer()
        self.assertEqual(
            serializer.to_representation(NumericRange(100, 199, bounds='[]')),
            (100, 199)
        )
        self.assertEqual(
            serializer.to_representation(NumericRange(100, 200, bounds='[)')),
            (100, 199)
        )

    def test_to_internal_value_produces_canonical_half_open_range(self):
        """An inclusive [lo, hi] pair is normalized to NumericRange(lo, hi+1, '[)')."""
        serializer = IntegerRangeSerializer()
        self.assertEqual(
            serializer.to_internal_value([100, 199]),
            NumericRange(100, 200, bounds='[)')
        )

    def test_to_internal_value_rejects_malformed_input(self):
        """Input must be a two-element list or tuple of ints."""
        serializer = IntegerRangeSerializer()
        with self.assertRaises(ValidationError):
            serializer.to_internal_value('100-200')
        with self.assertRaises(ValidationError):
            serializer.to_internal_value([100])
        with self.assertRaises(ValidationError):
            serializer.to_internal_value([100, 200, 300])

    def test_to_internal_value_rejects_non_integer_bounds(self):
        """Range boundaries must be integers, not strings or floats."""
        serializer = IntegerRangeSerializer()
        with self.assertRaises(ValidationError):
            serializer.to_internal_value(['100', '200'])
        with self.assertRaises(ValidationError):
            serializer.to_internal_value([100.5, 200.5])
