from __future__ import unicode_literals

import netaddr
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from ipam.constants import IPADDRESS_ROLE_VIP
from ipam.models import IPAddress, Prefix, VRF


class TestPrefix(TestCase):

    @override_settings(ENFORCE_GLOBAL_UNIQUE=False)
    def test_duplicate_global(self):
        Prefix.objects.create(prefix=netaddr.IPNetwork('192.0.2.0/24'))
        duplicate_prefix = Prefix(prefix=netaddr.IPNetwork('192.0.2.0/24'))
        self.assertIsNone(duplicate_prefix.clean())

    @override_settings(ENFORCE_GLOBAL_UNIQUE=True)
    def test_duplicate_global_unique(self):
        Prefix.objects.create(prefix=netaddr.IPNetwork('192.0.2.0/24'))
        duplicate_prefix = Prefix(prefix=netaddr.IPNetwork('192.0.2.0/24'))
        self.assertRaises(ValidationError, duplicate_prefix.clean)

    def test_duplicate_vrf(self):
        vrf = VRF.objects.create(name='Test', rd='1:1', enforce_unique=False)
        Prefix.objects.create(vrf=vrf, prefix=netaddr.IPNetwork('192.0.2.0/24'))
        duplicate_prefix = Prefix(vrf=vrf, prefix=netaddr.IPNetwork('192.0.2.0/24'))
        self.assertIsNone(duplicate_prefix.clean())

    def test_duplicate_vrf_unique(self):
        vrf = VRF.objects.create(name='Test', rd='1:1', enforce_unique=True)
        Prefix.objects.create(vrf=vrf, prefix=netaddr.IPNetwork('192.0.2.0/24'))
        duplicate_prefix = Prefix(vrf=vrf, prefix=netaddr.IPNetwork('192.0.2.0/24'))
        self.assertRaises(ValidationError, duplicate_prefix.clean)


class TestIPAddress(TestCase):

    @override_settings(ENFORCE_GLOBAL_UNIQUE=False)
    def test_duplicate_global(self):
        IPAddress.objects.create(address=netaddr.IPNetwork('192.0.2.1/24'))
        duplicate_ip = IPAddress(address=netaddr.IPNetwork('192.0.2.1/24'))
        self.assertIsNone(duplicate_ip.clean())

    @override_settings(ENFORCE_GLOBAL_UNIQUE=True)
    def test_duplicate_global_unique(self):
        IPAddress.objects.create(address=netaddr.IPNetwork('192.0.2.1/24'))
        duplicate_ip = IPAddress(address=netaddr.IPNetwork('192.0.2.1/24'))
        self.assertRaises(ValidationError, duplicate_ip.clean)

    def test_duplicate_vrf(self):
        vrf = VRF.objects.create(name='Test', rd='1:1', enforce_unique=False)
        IPAddress.objects.create(vrf=vrf, address=netaddr.IPNetwork('192.0.2.1/24'))
        duplicate_ip = IPAddress(vrf=vrf, address=netaddr.IPNetwork('192.0.2.1/24'))
        self.assertIsNone(duplicate_ip.clean())

    def test_duplicate_vrf_unique(self):
        vrf = VRF.objects.create(name='Test', rd='1:1', enforce_unique=True)
        IPAddress.objects.create(vrf=vrf, address=netaddr.IPNetwork('192.0.2.1/24'))
        duplicate_ip = IPAddress(vrf=vrf, address=netaddr.IPNetwork('192.0.2.1/24'))
        self.assertRaises(ValidationError, duplicate_ip.clean)

    @override_settings(ENFORCE_GLOBAL_UNIQUE=True)
    def test_duplicate_nonunique_role(self):
        IPAddress.objects.create(address=netaddr.IPNetwork('192.0.2.1/24'), role=IPADDRESS_ROLE_VIP)
        IPAddress.objects.create(address=netaddr.IPNetwork('192.0.2.1/24'), role=IPADDRESS_ROLE_VIP)
