import uuid

from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework.request import Request

from netbox.api.exceptions import QuerySetNotOrdered
from netbox.api.pagination import OptionalLimitOffsetPagination
from utilities.testing import APITestCase
from users.models import Token


class AppTest(APITestCase):

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


class OptionalLimitOffsetPaginationTest(TestCase):

    def setUp(self):
        self.paginator = OptionalLimitOffsetPagination()
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
