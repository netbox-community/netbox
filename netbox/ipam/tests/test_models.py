import netaddr

from django.test import TestCase, override_settings

from ipam.models import IPAddress, Prefix, VRF
from django.core.exceptions import ValidationError


class TestPrefix(TestCase):

    fixtures = [
        'dcim',
        'ipam'
    ]

    def test_create(self):
        prefix = Prefix.objects.create(
            prefix=netaddr.IPNetwork('10.1.1.0/24'),
            status=1
        )
        self.assertIsNone(prefix.clean())

    @override_settings(ENFORCE_GLOBAL_UNIQUE=True)
    def test_duplicate_global(self):
        prefix = Prefix.objects.create(
            prefix=netaddr.IPNetwork('10.1.1.0/24'),
            status=1
        )
        self.assertRaises(ValidationError, prefix.clean)

    @override_settings(ENFORCE_GLOBAL_UNIQUE=True)
    def test_duplicate_vrf(self):
        pfx_kwargs = {
            "prefix": netaddr.IPNetwork('10.1.1.0/24'),
            "status": 1,
            "vrf": VRF.objects.create(name='Test', rd='1:1'),
        }
        Prefix.objects.create(**pfx_kwargs)
        dup_prefix = Prefix.objects.create(**pfx_kwargs)
        self.assertRaises(ValidationError, dup_prefix.clean)


class TestIPAddress(TestCase):

    fixtures = [
        'dcim',
        'ipam'
    ]

    def test_create(self):
        address = IPAddress.objects.create(
            address=netaddr.IPNetwork('10.0.254.1/24'),
        )
        self.assertIsNone(address.clean())

    @override_settings(ENFORCE_GLOBAL_UNIQUE=True)
    def test_duplicate_global(self):
        address = IPAddress.objects.create(
            address=netaddr.IPNetwork('10.0.254.1/24'),
        )
        self.assertRaises(ValidationError, address.clean)

    @override_settings(ENFORCE_GLOBAL_UNIQUE=True)
    def test_duplicate_vrf(self):
        pfx_kwargs = {
            "address": netaddr.IPNetwork('10.0.254.1/24'),
            "status": 1,
            "vrf": VRF.objects.create(name='Test', rd='1:1'),
        }
        IPAddress.objects.create(**pfx_kwargs)
        dup_address = IPAddress.objects.create(**pfx_kwargs)
        self.assertRaises(ValidationError, dup_address.clean)
