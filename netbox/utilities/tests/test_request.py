from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase, override_settings
from netaddr import IPAddress

from utilities.request import copy_safe_request, get_client_ip, get_safe_request_context

User = get_user_model()


class CopySafeRequestTestCase(TestCase):
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

    def test_request_attributes_copied(self):
        """Core request attributes (path, path_info, method) are copied."""
        request = self.factory.get('/dcim/sites/1/?foo=bar')
        request.user = AnonymousUser()
        fake = copy_safe_request(request)
        self.assertEqual(fake.path, '/dcim/sites/1/')
        self.assertEqual(fake.path_info, '/dcim/sites/1/')
        self.assertEqual(fake.method, 'GET')
        self.assertEqual(fake.GET.get('foo'), 'bar')


class GetSafeRequestContextTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_only_safe_keys_returned(self):
        request = self.factory.get('/dcim/sites/1/?foo=bar')
        request.user = AnonymousUser()
        request.COOKIES['sessionid'] = 'secret'
        request.id = 'abc-123'

        context = get_safe_request_context(request)

        self.assertEqual(set(context.keys()), {'id', 'path', 'path_info', 'method', 'GET', 'user'})
        self.assertEqual(context['id'], 'abc-123')
        self.assertEqual(context['path'], '/dcim/sites/1/')
        self.assertEqual(context['method'], 'GET')
        self.assertEqual(context['GET'].get('foo'), 'bar')

    def test_user_is_username_string(self):
        """The exposed user must be the username string, not the User instance."""
        user = User.objects.create_user(username='testuser')
        request = self.factory.get('/')
        request.user = user

        context = get_safe_request_context(request)

        self.assertEqual(context['user'], 'testuser')
        self.assertNotIsInstance(context['user'], User)

    def test_sensitive_attributes_excluded(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()

        context = get_safe_request_context(request)

        self.assertNotIn('COOKIES', context)
        self.assertNotIn('META', context)
        self.assertNotIn('session', context)

    def test_missing_id_defaults_to_none(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()

        context = get_safe_request_context(request)

        self.assertIsNone(context['id'])

    def test_none_request_returns_none(self):
        self.assertIsNone(get_safe_request_context(None))


class GetClientIPTestCase(TestCase):
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

    def test_no_matching_header(self):
        request = self.factory.get('/')
        request.META.pop('REMOTE_ADDR', None)
        self.assertIsNone(get_client_ip(request))

    def test_additional_headers_argument(self):
        """Headers passed via `additional_headers` are checked after the configured defaults."""
        request = self.factory.get('/', HTTP_CF_CONNECTING_IP='10.0.0.1')
        request.META.pop('REMOTE_ADDR', None)
        self.assertEqual(
            get_client_ip(request, additional_headers=('HTTP_CF_CONNECTING_IP',)),
            IPAddress('10.0.0.1'),
        )

    def test_default_headers_precede_additional_headers(self):
        """Headers from HTTP_CLIENT_IP_HEADERS take precedence over `additional_headers`."""
        request = self.factory.get('/', HTTP_X_FORWARDED_FOR='192.168.1.1', HTTP_CF_CONNECTING_IP='10.0.0.1')
        self.assertEqual(
            get_client_ip(request, additional_headers=('HTTP_CF_CONNECTING_IP',)),
            IPAddress('192.168.1.1'),
        )

    @override_settings(HTTP_CLIENT_IP_HEADERS=('HTTP_CF_CONNECTING_IP', 'HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR'))
    def test_custom_configured_headers(self):
        """get_client_ip() should honor the HTTP_CLIENT_IP_HEADERS setting."""
        request = self.factory.get('/', HTTP_X_FORWARDED_FOR='192.168.1.1', HTTP_CF_CONNECTING_IP='10.0.0.1')
        self.assertEqual(get_client_ip(request), IPAddress('10.0.0.1'))
