from django.test import TestCase

from ipam.choices import IPAddressStatusChoices, PrefixStatusChoices
from ipam.models import IPAddress, Prefix, VRF

import netaddr

class OrderingTestBase(TestCase):
    vrfs = None

    """
    Setup the VRFs for the class as a whole
    """
    def setUp(self):
        self.vrfs = (VRF(name="VRF A"), VRF(name="VRF B"), VRF(name="VRF C"))
        VRF.objects.bulk_create(self.vrfs)

    """
    Perform the comparison of the queryset object and the object used to instantiate the queryset.
    """
    def _compare(self, queryset, objectset):
        for i, obj in enumerate(queryset):
            if isinstance(obj, Prefix):
                self.assertEqual((obj.vrf, obj.prefix), (objectset[i]['vrf'], objectset[i]['prefix']))
            elif isinstance(obj, IPAddress):
                self.assertEqual((obj.vrf, obj.address), (objectset[i]['vrf'], objectset[i]['address']))


class PrefixOrderingTestCase(OrderingTestBase):

    """
    This is for comparing the complex ordering test case
    """
    def _compare_complex(self, queryset, prefixes):
        qsprefixes, regprefixes = [], []
        for i, obj in enumerate(queryset):
            qsprefixes.append(obj.prefix)
        for pfx in prefixes:
            regprefixes.append(pfx['prefix'])
        self.assertEquals(qsprefixes, regprefixes)

    """
    This is a very basic test, which tests both prefixes without VRFs and prefixes with VRFs
    """
    def test_prefix_vrf_ordering(self):
        # Setup VRFs
        vrfa, vrfb, vrfc = self.vrfs

        # Setup Prefixes
        prefixes = (
            {"status": PrefixStatusChoices.STATUS_CONTAINER, "vrf": None, "family": 4, "prefix": netaddr.IPNetwork('192.168.0.0/16')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": None, "family": 4, "prefix": netaddr.IPNetwork('192.168.0.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": None, "family": 4, "prefix": netaddr.IPNetwork('192.168.1.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": None, "family": 4, "prefix": netaddr.IPNetwork('192.168.2.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": None, "family": 4, "prefix": netaddr.IPNetwork('192.168.3.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": None, "family": 4, "prefix": netaddr.IPNetwork('192.168.4.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": None, "family": 4, "prefix": netaddr.IPNetwork('192.168.5.0/24')},

            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "prefix": netaddr.IPNetwork('10.0.0.0/8')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "prefix": netaddr.IPNetwork('10.0.0.0/16')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "prefix": netaddr.IPNetwork('10.0.0.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "prefix": netaddr.IPNetwork('10.0.1.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "prefix": netaddr.IPNetwork('10.0.2.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "prefix": netaddr.IPNetwork('10.0.3.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "prefix": netaddr.IPNetwork('10.0.4.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "prefix": netaddr.IPNetwork('10.1.0.0/16')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "prefix": netaddr.IPNetwork('10.1.1.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "prefix": netaddr.IPNetwork('10.1.2.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "prefix": netaddr.IPNetwork('10.1.3.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "prefix": netaddr.IPNetwork('10.1.4.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "prefix": netaddr.IPNetwork('10.2.0.0/16')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "prefix": netaddr.IPNetwork('10.2.1.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "prefix": netaddr.IPNetwork('10.2.2.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "prefix": netaddr.IPNetwork('10.2.3.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "prefix": netaddr.IPNetwork('10.2.4.0/24')},

            {"status": PrefixStatusChoices.STATUS_CONTAINER, "vrf": vrfb, "family": 4, "prefix": netaddr.IPNetwork('172.16.0.0/12')},
            {"status": PrefixStatusChoices.STATUS_CONTAINER, "vrf": vrfb, "family": 4, "prefix": netaddr.IPNetwork('172.16.0.0/16')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfb, "family": 4, "prefix": netaddr.IPNetwork('172.16.0.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfb, "family": 4, "prefix": netaddr.IPNetwork('172.16.1.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfb, "family": 4, "prefix": netaddr.IPNetwork('172.16.2.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfb, "family": 4, "prefix": netaddr.IPNetwork('172.16.3.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfb, "family": 4, "prefix": netaddr.IPNetwork('172.16.4.0/24')},
            {"status": PrefixStatusChoices.STATUS_CONTAINER, "vrf": vrfb, "family": 4, "prefix": netaddr.IPNetwork('172.17.0.0/16')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfb, "family": 4, "prefix": netaddr.IPNetwork('172.17.0.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfb, "family": 4, "prefix": netaddr.IPNetwork('172.17.1.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfb, "family": 4, "prefix": netaddr.IPNetwork('172.17.2.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfb, "family": 4, "prefix": netaddr.IPNetwork('172.17.3.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfb, "family": 4, "prefix": netaddr.IPNetwork('172.17.4.0/24')},
        )

        Prefix.objects.bulk_create([Prefix(status=args['status'], vrf=args['vrf'], family=args['family'], prefix=args['prefix']) for args in prefixes])

        # Test
        self._compare(Prefix.objects.all(), prefixes)

    """
    This function tests a compex ordering of interwoven prefixes and vrfs.  This is the current expected ordering of VRFs
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
    def test_prefix_complex_ordering(self):
        # Setup VRFs
        vrfa, vrfb, vrfc = self.vrfs

        # Setup Prefixes
        prefixes = [
            {"status": PrefixStatusChoices.STATUS_CONTAINER, "vrf": None, "family": 4, "prefix": netaddr.IPNetwork('10.0.0.0/8')},
            {"status": PrefixStatusChoices.STATUS_CONTAINER, "vrf": None, "family": 4, "prefix": netaddr.IPNetwork('10.0.0.0/16')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": None, "family": 4, "prefix": netaddr.IPNetwork('10.1.0.0/16')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": None, "family": 4, "prefix": netaddr.IPNetwork('192.168.0.0/16')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "prefix": netaddr.IPNetwork('10.0.0.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "prefix": netaddr.IPNetwork('10.0.1.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "prefix": netaddr.IPNetwork('10.0.1.0/25')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "prefix": netaddr.IPNetwork('10.1.0.0/24')},
            {"status": PrefixStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "prefix": netaddr.IPNetwork('10.1.1.0/24')},
        ]
        Prefix.objects.bulk_create([Prefix(status=args['status'], vrf=args['vrf'], family=args['family'], prefix=args['prefix']) for args in prefixes])

        # Test
        self._compare_complex(Prefix.objects.all(), prefixes)


class IPAddressOrderingTestCase(OrderingTestBase):
    """
    This function tests ordering with the inclusion of vrfs
    """
    def test_address_vrf_ordering(self):
        # Setup VRFs
        vrfa, vrfb, vrfc = self.vrfs

        # Setup Addresses
        addresses = (
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "address": netaddr.IPNetwork('10.0.0.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "address": netaddr.IPNetwork('10.0.1.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "address": netaddr.IPNetwork('10.0.2.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "address": netaddr.IPNetwork('10.0.3.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "address": netaddr.IPNetwork('10.0.4.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "address": netaddr.IPNetwork('10.1.0.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "address": netaddr.IPNetwork('10.1.1.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "address": netaddr.IPNetwork('10.1.2.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "address": netaddr.IPNetwork('10.1.3.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "address": netaddr.IPNetwork('10.1.4.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "address": netaddr.IPNetwork('10.2.0.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "address": netaddr.IPNetwork('10.2.1.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "address": netaddr.IPNetwork('10.2.2.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "address": netaddr.IPNetwork('10.2.3.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfa, "family": 4, "address": netaddr.IPNetwork('10.2.4.1/24')},

            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfb, "family": 4, "address": netaddr.IPNetwork('172.16.0.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfb, "family": 4, "address": netaddr.IPNetwork('172.16.1.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfb, "family": 4, "address": netaddr.IPNetwork('172.16.2.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfb, "family": 4, "address": netaddr.IPNetwork('172.16.3.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfb, "family": 4, "address": netaddr.IPNetwork('172.16.4.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfb, "family": 4, "address": netaddr.IPNetwork('172.17.0.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfb, "family": 4, "address": netaddr.IPNetwork('172.17.1.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfb, "family": 4, "address": netaddr.IPNetwork('172.17.2.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfb, "family": 4, "address": netaddr.IPNetwork('172.17.3.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": vrfb, "family": 4, "address": netaddr.IPNetwork('172.17.4.1/24')},

            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": None, "family": 4, "address": netaddr.IPNetwork('192.168.0.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": None, "family": 4, "address": netaddr.IPNetwork('192.168.1.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": None, "family": 4, "address": netaddr.IPNetwork('192.168.2.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": None, "family": 4, "address": netaddr.IPNetwork('192.168.3.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": None, "family": 4, "address": netaddr.IPNetwork('192.168.4.1/24')},
            {"status": IPAddressStatusChoices.STATUS_ACTIVE, "vrf": None, "family": 4, "address": netaddr.IPNetwork('192.168.5.1/24')},
        )
        IPAddress.objects.bulk_create([IPAddress(status=args['status'], vrf=args['vrf'], family=args['family'], address=args['address']) for args in addresses])

        # Test
        self._compare(IPAddress.objects.all(), addresses)
