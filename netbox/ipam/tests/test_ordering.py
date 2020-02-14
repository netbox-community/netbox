from django.test import TestCase

from ipam.choices import IPAddressStatusChoices, PrefixStatusChoices
from ipam.models import IPAddress, Prefix, VRF

import netaddr


class OrderingTestBase(TestCase):
    vrfs = None

    def setUp(self):
        """
        Setup the VRFs for the class as a whole
        """
        self.vrfs = (VRF(name="VRF A"), VRF(name="VRF B"), VRF(name="VRF C"))
        VRF.objects.bulk_create(self.vrfs)

    def _compare(self, queryset, objectset):
        """
        Perform the comparison of the queryset object and the object used to instantiate the queryset.
        """
        for i, obj in enumerate(queryset):
            self.assertEqual(obj, objectset[i])

    def _compare_ne(self, queryset, objectset):
        """
        Perform the comparison of the queryset object and the object used to instantiate the queryset.
        """
        for i, obj in enumerate(queryset):
            self.assertNotEqual(obj, objectset[i])


class PrefixOrderingTestCase(OrderingTestBase):

    def test_prefix_vrf_ordering(self):
        """
        This is a very basic test, which tests both prefixes without VRFs and prefixes with VRFs
        """
        # Setup VRFs
        vrfa, vrfb, vrfc = self.vrfs

        # Setup Prefixes
        prefixes = (
            Prefix(status=PrefixStatusChoices.STATUS_CONTAINER, vrf=None, prefix=netaddr.IPNetwork('192.168.0.0/16')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=None, prefix=netaddr.IPNetwork('192.168.0.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=None, prefix=netaddr.IPNetwork('192.168.1.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=None, prefix=netaddr.IPNetwork('192.168.2.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=None, prefix=netaddr.IPNetwork('192.168.3.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=None, prefix=netaddr.IPNetwork('192.168.4.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=None, prefix=netaddr.IPNetwork('192.168.5.0/24')),

            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfa, prefix=netaddr.IPNetwork('10.0.0.0/8')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfa, prefix=netaddr.IPNetwork('10.0.0.0/16')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfa, prefix=netaddr.IPNetwork('10.0.0.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfa, prefix=netaddr.IPNetwork('10.0.1.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfa, prefix=netaddr.IPNetwork('10.0.2.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfa, prefix=netaddr.IPNetwork('10.0.3.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfa, prefix=netaddr.IPNetwork('10.0.4.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfa, prefix=netaddr.IPNetwork('10.1.0.0/16')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfa, prefix=netaddr.IPNetwork('10.1.1.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfa, prefix=netaddr.IPNetwork('10.1.2.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfa, prefix=netaddr.IPNetwork('10.1.3.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfa, prefix=netaddr.IPNetwork('10.1.4.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfa, prefix=netaddr.IPNetwork('10.2.0.0/16')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfa, prefix=netaddr.IPNetwork('10.2.1.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfa, prefix=netaddr.IPNetwork('10.2.2.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfa, prefix=netaddr.IPNetwork('10.2.3.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfa, prefix=netaddr.IPNetwork('10.2.4.0/24')),

            Prefix(status=PrefixStatusChoices.STATUS_CONTAINER, vrf=vrfb, prefix=netaddr.IPNetwork('172.16.0.0/12')),
            Prefix(status=PrefixStatusChoices.STATUS_CONTAINER, vrf=vrfb, prefix=netaddr.IPNetwork('172.16.0.0/16')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfb, prefix=netaddr.IPNetwork('172.16.0.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfb, prefix=netaddr.IPNetwork('172.16.1.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfb, prefix=netaddr.IPNetwork('172.16.2.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfb, prefix=netaddr.IPNetwork('172.16.3.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfb, prefix=netaddr.IPNetwork('172.16.4.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_CONTAINER, vrf=vrfb, prefix=netaddr.IPNetwork('172.17.0.0/16')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfb, prefix=netaddr.IPNetwork('172.17.0.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfb, prefix=netaddr.IPNetwork('172.17.1.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfb, prefix=netaddr.IPNetwork('172.17.2.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfb, prefix=netaddr.IPNetwork('172.17.3.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfb, prefix=netaddr.IPNetwork('172.17.4.0/24')),
        )

        Prefix.objects.bulk_create(prefixes)

        # Test
        self._compare(Prefix.objects.all(), prefixes)

    def test_prefix_complex_ordering(self):
        """
        This function tests a complex ordering of interwoven prefixes and vrfs.  This is the current expected ordering of VRFs
        This includes the testing of the Container status.

        The proper ordering, to get proper containerization should be:
            None:10.0.0.0/8
            None:10.0.0.0/16
            VRF A:10.0.0.0/24
            VRF A:10.0.1.0/24
            VRF A:10.0.1.0/25
            None:10.1.0.0/16
            VRF A:10.1.0.0/24
            VRF A:10.1.1.0/24
            None: 192.168.0.0/16
        """
        # Setup VRFs
        vrfa, vrfb, vrfc = self.vrfs

        # Setup Prefixes
        prefixes = [
            Prefix(status=PrefixStatusChoices.STATUS_CONTAINER, vrf=None, prefix=netaddr.IPNetwork('10.0.0.0/8')),
            Prefix(status=PrefixStatusChoices.STATUS_CONTAINER, vrf=None, prefix=netaddr.IPNetwork('10.0.0.0/16')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=None, prefix=netaddr.IPNetwork('10.1.0.0/16')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=None, prefix=netaddr.IPNetwork('192.168.0.0/16')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfa, prefix=netaddr.IPNetwork('10.0.0.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfa, prefix=netaddr.IPNetwork('10.0.1.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfa, prefix=netaddr.IPNetwork('10.0.1.0/25')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfa, prefix=netaddr.IPNetwork('10.1.0.0/24')),
            Prefix(status=PrefixStatusChoices.STATUS_ACTIVE, vrf=vrfa, prefix=netaddr.IPNetwork('10.1.1.0/24')),
        ]
        Prefix.objects.bulk_create(prefixes)

        # Test
        self._compare(Prefix.objects.all(), prefixes)


class IPAddressOrderingTestCase(OrderingTestBase):

    def test_address_vrf_ordering(self):
        """
        This function tests ordering with the inclusion of vrfs
        """
        # Setup VRFs
        vrfa, vrfb, vrfc = self.vrfs

        # Setup Addresses
        addresses = (
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfa, address=netaddr.IPNetwork('10.0.0.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfa, address=netaddr.IPNetwork('10.0.1.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfa, address=netaddr.IPNetwork('10.0.2.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfa, address=netaddr.IPNetwork('10.0.3.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfa, address=netaddr.IPNetwork('10.0.4.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfa, address=netaddr.IPNetwork('10.1.0.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfa, address=netaddr.IPNetwork('10.1.1.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfa, address=netaddr.IPNetwork('10.1.2.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfa, address=netaddr.IPNetwork('10.1.3.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfa, address=netaddr.IPNetwork('10.1.4.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfa, address=netaddr.IPNetwork('10.2.0.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfa, address=netaddr.IPNetwork('10.2.1.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfa, address=netaddr.IPNetwork('10.2.2.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfa, address=netaddr.IPNetwork('10.2.3.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfa, address=netaddr.IPNetwork('10.2.4.1/24')),

            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfb, address=netaddr.IPNetwork('172.16.0.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfb, address=netaddr.IPNetwork('172.16.1.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfb, address=netaddr.IPNetwork('172.16.2.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfb, address=netaddr.IPNetwork('172.16.3.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfb, address=netaddr.IPNetwork('172.16.4.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfb, address=netaddr.IPNetwork('172.17.0.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfb, address=netaddr.IPNetwork('172.17.1.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfb, address=netaddr.IPNetwork('172.17.2.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfb, address=netaddr.IPNetwork('172.17.3.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=vrfb, address=netaddr.IPNetwork('172.17.4.1/24')),

            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=None, address=netaddr.IPNetwork('192.168.0.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=None, address=netaddr.IPNetwork('192.168.1.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=None, address=netaddr.IPNetwork('192.168.2.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=None, address=netaddr.IPNetwork('192.168.3.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=None, address=netaddr.IPNetwork('192.168.4.1/24')),
            IPAddress(status=IPAddressStatusChoices.STATUS_ACTIVE, vrf=None, address=netaddr.IPNetwork('192.168.5.1/24')),
        )
        IPAddress.objects.bulk_create(addresses)

        # Test
        self._compare(IPAddress.objects.all(), addresses)
