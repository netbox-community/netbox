from django.test import TestCase, RequestFactory

from netaddr import IPAddress
from utilities.request import get_client_ip


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
