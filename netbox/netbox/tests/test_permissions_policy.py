from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from netbox.middleware import PermissionsPolicyMiddleware
from utilities.testing import TestCase as NetBoxTestCase

HEADER = 'Permissions-Policy'

DEFAULT_HEADER = 'camera=(), microphone=(), geolocation=(), payment=(), usb=(), hid=(), serial=(), bluetooth=()'


class PermissionsPolicyHeaderTestCase(TestCase):
    """
    Check the header on real responses, through the whole middleware stack.
    """

    def test_default_denies_the_default_deny_list(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response[HEADER], DEFAULT_HEADER)

    @override_settings(PERMISSIONS_POLICY={'camera': ['self'], 'geolocation': []})
    def test_custom_policy_replaces_default(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response[HEADER], 'camera=(self), geolocation=()')

    @override_settings(PERMISSIONS_POLICY={'camera': ['self', 'https://scan.example.com']})
    def test_origins_are_quoted_and_self_is_a_token(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response[HEADER], 'camera=(self "https://scan.example.com")')

    @override_settings(PERMISSIONS_POLICY={})
    def test_empty_policy_sends_no_header(self):
        response = self.client.get(reverse('login'))
        self.assertNotIn(HEADER, response)


class PermissionsPolicyContentTypeTestCase(NetBoxTestCase):
    """
    The header is only useful to a browser rendering a document, so raw API data responses carry none.
    """

    def setUp(self):
        super().setUp()

        self.user.is_superuser = True
        self.user.save()

    def test_rest_api_json_has_no_header(self):
        response = self.client.get(reverse('api-root'), HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('application/json'))
        self.assertNotIn(HEADER, response)

    def test_graphql_json_has_no_header(self):
        response = self.client.post(
            reverse('graphql'),
            data='{"query": "{ __typename }"}',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('application/json'))
        self.assertNotIn(HEADER, response)

    def test_browsable_api_html_has_header(self):
        response = self.client.get(reverse('api-root'), HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('text/html'))
        self.assertEqual(response[HEADER], DEFAULT_HEADER)

    def test_ui_page_has_header(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response[HEADER], DEFAULT_HEADER)


class PermissionsPolicyMiddlewareTestCase(SimpleTestCase):
    """
    Check the middleware in isolation, with a view that sets the header itself.
    """

    def test_header_set_by_view_is_untouched(self):
        def view(request):
            response = HttpResponse()
            response[HEADER] = 'fullscreen=(self)'
            return response

        response = PermissionsPolicyMiddleware(view)(RequestFactory().get('/'))
        self.assertEqual(response[HEADER], 'fullscreen=(self)')

    def test_redirects_and_not_modified_have_no_header(self):
        for status in (301, 302, 304):
            with self.subTest(status=status):
                response = HttpResponse(status=status, content_type='text/html')
                middleware = PermissionsPolicyMiddleware(lambda request, response=response: response)
                self.assertNotIn(HEADER, middleware(RequestFactory().get('/')))

    def test_html_200_has_header(self):
        middleware = PermissionsPolicyMiddleware(lambda request: HttpResponse(content_type='text/html'))
        self.assertEqual(middleware(RequestFactory().get('/'))[HEADER], DEFAULT_HEADER)

    @override_settings(PERMISSIONS_POLICY={'camera': ['*']})
    def test_lone_wildcard_is_a_bare_token(self):
        response = PermissionsPolicyMiddleware(lambda request: HttpResponse(content_type='text/html'))(
            RequestFactory().get('/')
        )
        self.assertEqual(response[HEADER], 'camera=*')

    @override_settings(PERMISSIONS_POLICY={'camera': ['*', 'self']})
    def test_wildcard_with_other_origins_stays_an_inner_list(self):
        response = PermissionsPolicyMiddleware(lambda request: HttpResponse(content_type='text/html'))(
            RequestFactory().get('/')
        )
        self.assertEqual(response[HEADER], 'camera=(* self)')

    def test_header_is_built_once_per_instance(self):
        with patch.object(
            PermissionsPolicyMiddleware, 'build_header', wraps=PermissionsPolicyMiddleware.build_header
        ) as build_header:
            middleware = PermissionsPolicyMiddleware(lambda request: HttpResponse())
            first = middleware(RequestFactory().get('/'))
            second = middleware(RequestFactory().get('/'))
        build_header.assert_called_once()
        self.assertEqual(first[HEADER], DEFAULT_HEADER)
        self.assertEqual(second[HEADER], DEFAULT_HEADER)
