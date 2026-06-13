from django.test import TestCase
from netaddr import IPAddress

from ipam.fields import IPAddressField, IPNetworkField


class BaseIPFieldTestCase(TestCase):
    """
    Regression coverage for BaseIPField.get_prep_value() — zero addresses such as
    0.0.0.0 and :: are valid hosts and must not be treated as empty values.
    """

    def test_get_prep_value_accepts_ipv4_zero_address(self):
        # Regression: 0.0.0.0 is a valid host, not an empty value.
        self.assertEqual(IPAddressField().get_prep_value(IPAddress('0.0.0.0')), '0.0.0.0')

    def test_get_prep_value_accepts_ipv6_zero_address(self):
        # Regression: :: is a valid host, not an empty value.
        self.assertEqual(IPAddressField().get_prep_value(IPAddress('::')), '::')

    def test_get_prep_value_passes_through_empty(self):
        self.assertIsNone(IPNetworkField().get_prep_value(None))
        self.assertIsNone(IPAddressField().get_prep_value(''))

    def test_get_prep_value_preserves_raw_zero_as_empty(self):
        # Raw int 0 is preserved as the legacy "empty" sentinel; Django's ORM never
        # passes it directly, but the previous `not value` check returned None for it.
        self.assertIsNone(IPAddressField().get_prep_value(0))
        self.assertIsNone(IPNetworkField().get_prep_value(0))
