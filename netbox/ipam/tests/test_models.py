from __future__ import unicode_literals

import netaddr
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from ipam.models import IPAddress, Prefix, VRF, Service
from ipam.models import IP_PROTOCOL_TCP
from dcim.models import Manufacturer, DeviceType, Device, Site, DeviceRole


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


class ServiceCase(TestCase):

    def test_rack_funiture_no_assign(self):
        manufacturer = Manufacturer.objects.create(
            name='Acme',
            slug='acme'
        )
        rack_furniture_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='The Best Shelf 9000',
            slug='rf9000',
            is_network_device=False,
            is_rack_furniture=True,
        )
        site = Site.objects.create(
            name="Site 1",
            slug="site-1"
        )
        role = DeviceRole.objects.create(
            name='RF',
            slug='rf'
        )
        rack_furniture = Device.objects.create(
            name="1U Blank",
            device_type=rack_furniture_type,
            site=site,
            device_role=role,
        )

        s = Service(
            name="Service",
            protocol=IP_PROTOCOL_TCP,
            port=80,
            device=rack_furniture
        )

        with self.assertRaises(ValidationError):
            s.clean()
