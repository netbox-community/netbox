from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from netaddr import IPAddress

from utilities.request import copy_safe_request, get_client_ip


class CopySafeRequestTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _make_request(self, **kwargs):
        request = self.factory.get('/', **kwargs)
        request.user = AnonymousUser()
        return request

    def test_standard_meta_keys_copied(self):
        request = self._make_request(HTTP_USER_AGENT='TestAgent/1.0')
        fake = copy_safe_request(request)
        self.assertEqual(fake.META.get('HTTP_USER_AGENT'), 'TestAgent/1.0')

    def test_arbitrary_http_headers_copied(self):
        """Arbitrary HTTP_ headers (e.g. X-NetBox-*) should be included."""
        request = self._make_request(HTTP_X_NETBOX_BRANCH='my-branch')
        fake = copy_safe_request(request)
        self.assertEqual(fake.META.get('HTTP_X_NETBOX_BRANCH'), 'my-branch')

    def test_sensitive_headers_excluded(self):
        """Authorization and Cookie headers must not be copied."""
        request = self._make_request(HTTP_AUTHORIZATION='Bearer secret')
        fake = copy_safe_request(request)
        self.assertNotIn('HTTP_AUTHORIZATION', fake.META)

    def test_non_string_meta_values_excluded(self):
        """Non-string META values must not be copied."""
        request = self._make_request()
        request.META['HTTP_X_CUSTOM_INT'] = 42
        fake = copy_safe_request(request)
        self.assertNotIn('HTTP_X_CUSTOM_INT', fake.META)


class GetClientIPTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_ipv4_address(self):
        request = self.factory.get('/', HTTP_X_FORWARDED_FOR='192.168.1.1')
        self.assertEqual(get_client_ip(request), IPAddress('192.168.1.1'))
        request = self.factory.get('/', HTTP_X_FORWARDED_FOR='192.168.1.1:8080')
        self.assertEqual(get_client_ip(request), IPAddress('192.168.1.1'))

    def test_ipv6_address(self):
        request = self.factory.get('/', HTTP_X_FORWARDED_FOR='2001:db8::8a2e:370:7334')
        self.assertEqual(get_client_ip(request), IPAddress('2001:db8::8a2e:370:7334'))
        request = self.factory.get('/', HTTP_X_FORWARDED_FOR='[2001:db8::8a2e:370:7334]')
        self.assertEqual(get_client_ip(request), IPAddress('2001:db8::8a2e:370:7334'))
        request = self.factory.get('/', HTTP_X_FORWARDED_FOR='[2001:db8::8a2e:370:7334]:8080')
        self.assertEqual(get_client_ip(request), IPAddress('2001:db8::8a2e:370:7334'))

    def test_invalid_ip_address(self):
        request = self.factory.get('/', HTTP_X_FORWARDED_FOR='invalid_ip')
        with self.assertRaises(ValueError):
            get_client_ip(request)
