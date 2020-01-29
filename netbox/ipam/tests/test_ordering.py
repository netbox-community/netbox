from django.test import TestCase

from ipam.choices import IPAddressRoleChoices, PrefixStatusChoices
from ipam.models import Aggregate, IPAddress, Prefix, RIR, VLAN, VLANGroup, VRF

import netaddr


class PrefixOrderingTestCase(TestCase):

    def _create_prefix(self, prefixes):
        prefixobjects = []
        for pfx in prefixes:
            status, vrf, prefix = pfx
            family = 4
            if not netaddr.valid_ipv4(prefix):
                family = 6
            pfx = Prefix(prefix=prefix, family=family, vrf=vrf, status=status)
            prefixobjects.append(pfx)

        return prefixobjects

    def _compare_prefix(self, queryset, prefixes):

        for i, obj in enumerate(queryset):
            status, vrf, prefix = prefixes[i]
            self.assertEqual((obj.vrf, obj.prefix), (vrf, prefix))

    def _compare_complex(self, queryset, prefixes):
        qsprefixes, regprefixes = [], []
        for i, obj in enumerate(queryset):
            qsprefixes.append(obj.prefix)
        for pfx in prefixes:
            regprefixes.append(pfx[2])
        return (qsprefixes, regprefixes)



    def test_prefix_ordering(self):
        # Setup Prefixes
        prefixes = (
            (PrefixStatusChoices.STATUS_CONTAINER, None, netaddr.IPNetwork('10.0.0.0/8')),
            (PrefixStatusChoices.STATUS_CONTAINER, None, netaddr.IPNetwork('10.0.0.0/16')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('10.0.0.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('10.0.1.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('10.0.2.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('10.0.3.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('10.0.4.0/24')),
            (PrefixStatusChoices.STATUS_CONTAINER, None, netaddr.IPNetwork('10.1.0.0/16')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('10.1.1.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('10.1.2.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('10.1.3.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('10.1.4.0/24')),
            (PrefixStatusChoices.STATUS_CONTAINER, None, netaddr.IPNetwork('10.2.0.0/16')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('10.2.1.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('10.2.2.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('10.2.3.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('10.2.4.0/24')),

            (PrefixStatusChoices.STATUS_CONTAINER, None, netaddr.IPNetwork('172.16.0.0/12')),
            (PrefixStatusChoices.STATUS_CONTAINER, None, netaddr.IPNetwork('172.16.0.0/16')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('172.16.0.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('172.16.1.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('172.16.2.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('172.16.3.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('172.16.4.0/24')),
            (PrefixStatusChoices.STATUS_CONTAINER, None, netaddr.IPNetwork('172.17.0.0/16')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('172.17.0.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('172.17.1.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('172.17.2.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('172.17.3.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('172.17.4.0/24')),

            (PrefixStatusChoices.STATUS_CONTAINER, None, netaddr.IPNetwork('192.168.0.0/16')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('192.168.0.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('192.168.1.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('192.168.2.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('192.168.3.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('192.168.4.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('192.168.5.0/24'))
        )
        Prefix.objects.bulk_create(self._create_prefix(prefixes))

        # Test
        self._compare_prefix(Prefix.objects.all(), prefixes)

    def test_prefix_vrf_ordering(self):
        # Setup VRFs
        vrfa = VRF(name='VRF A')
        vrfb = VRF(name='VRF B')
        vrfs = [vrfa, vrfb]
        VRF.objects.bulk_create(vrfs)

        # Setup Prefixes
        prefixes = (
            (PrefixStatusChoices.STATUS_CONTAINER, None, netaddr.IPNetwork('192.168.0.0/16')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('192.168.0.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('192.168.1.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('192.168.2.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('192.168.3.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('192.168.4.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('192.168.5.0/24')),

            (PrefixStatusChoices.STATUS_CONTAINER, vrfa, netaddr.IPNetwork('10.0.0.0/8')),
            (PrefixStatusChoices.STATUS_CONTAINER, vrfa, netaddr.IPNetwork('10.0.0.0/16')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfa, netaddr.IPNetwork('10.0.0.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfa, netaddr.IPNetwork('10.0.1.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfa, netaddr.IPNetwork('10.0.2.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfa, netaddr.IPNetwork('10.0.3.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfa, netaddr.IPNetwork('10.0.4.0/24')),
            (PrefixStatusChoices.STATUS_CONTAINER, vrfa, netaddr.IPNetwork('10.1.0.0/16')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfa, netaddr.IPNetwork('10.1.1.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfa, netaddr.IPNetwork('10.1.2.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfa, netaddr.IPNetwork('10.1.3.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfa, netaddr.IPNetwork('10.1.4.0/24')),
            (PrefixStatusChoices.STATUS_CONTAINER, vrfa, netaddr.IPNetwork('10.2.0.0/16')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfa, netaddr.IPNetwork('10.2.1.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfa, netaddr.IPNetwork('10.2.2.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfa, netaddr.IPNetwork('10.2.3.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfa, netaddr.IPNetwork('10.2.4.0/24')),

            (PrefixStatusChoices.STATUS_CONTAINER, vrfb, netaddr.IPNetwork('172.16.0.0/12')),
            (PrefixStatusChoices.STATUS_CONTAINER, vrfb, netaddr.IPNetwork('172.16.0.0/16')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfb, netaddr.IPNetwork('172.16.0.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfb, netaddr.IPNetwork('172.16.1.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfb, netaddr.IPNetwork('172.16.2.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfb, netaddr.IPNetwork('172.16.3.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfb, netaddr.IPNetwork('172.16.4.0/24')),
            (PrefixStatusChoices.STATUS_CONTAINER, vrfb, netaddr.IPNetwork('172.17.0.0/16')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfb, netaddr.IPNetwork('172.17.0.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfb, netaddr.IPNetwork('172.17.1.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfb, netaddr.IPNetwork('172.17.2.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfb, netaddr.IPNetwork('172.17.3.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrfb, netaddr.IPNetwork('172.17.4.0/24')),
        )
        Prefix.objects.bulk_create(self._create_prefix(prefixes))

        # Test
        self._compare_prefix(Prefix.objects.all(), prefixes)

    def test_prefix_complex_ordering(self):
        # Setup VRF's
        vrf = VRF(name='VRF A')
        vrfs = [vrf]
        VRF.objects.bulk_create(vrfs)

        # Setup Prefixes
        prefixes = [
            (PrefixStatusChoices.STATUS_CONTAINER, None, netaddr.IPNetwork('10.0.0.0/8')),
            (PrefixStatusChoices.STATUS_CONTAINER, None, netaddr.IPNetwork('10.0.0.0/16')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('10.1.0.0/16')),
            (PrefixStatusChoices.STATUS_ACTIVE, None, netaddr.IPNetwork('192.168.0.0/16')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrf, netaddr.IPNetwork('10.0.0.0/24')),
            (PrefixStatusChoices.STATUS_CONTAINER, vrf, netaddr.IPNetwork('10.0.1.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrf, netaddr.IPNetwork('10.0.1.0/25')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrf, netaddr.IPNetwork('10.1.0.0/24')),
            (PrefixStatusChoices.STATUS_ACTIVE, vrf, netaddr.IPNetwork('10.1.1.0/24'))
        ]
        Prefix.objects.bulk_create(self._create_prefix(prefixes))

        # Test
        qsprefixes, compprefixes = self._compare_complex(Prefix.objects.all(), prefixes)
        self.assertEquals(qsprefixes, compprefixes)
