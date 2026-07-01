import netaddr
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.backends.postgresql.psycopg_any import NumericRange
from django.test import TestCase, override_settings
from netaddr import IPNetwork, IPSet

from dcim.models import Site, SiteGroup
from ipam.choices import *
from ipam.constants import SERVICE_PORT_MAX, SERVICE_PORT_MIN
from ipam.models import *
from ipam.utils import rebuild_prefixes
from utilities.data import string_to_ranges
from virtualization.models import VirtualMachine


class AggregateTestCase(TestCase):

    def test_family_string(self):
        # Test property when prefix is a string
        agg = Aggregate(prefix='10.0.0.0/8')
        self.assertEqual(agg.family, 4)
        agg_v6 = Aggregate(prefix='2001:db8::/32')
        self.assertEqual(agg_v6.family, 6)

    def test_get_utilization(self):
        rir = RIR.objects.create(name='RIR 1', slug='rir-1')
        aggregate = Aggregate(prefix=IPNetwork('10.0.0.0/8'), rir=rir)
        aggregate.save()

        # 25% utilization
        Prefix.objects.bulk_create((
            Prefix(prefix=IPNetwork('10.0.0.0/12')),
            Prefix(prefix=IPNetwork('10.16.0.0/12')),
            Prefix(prefix=IPNetwork('10.32.0.0/12')),
            Prefix(prefix=IPNetwork('10.48.0.0/12')),
        ))
        self.assertEqual(aggregate.get_utilization(), 25)

        # 50% utilization
        Prefix.objects.bulk_create((
            Prefix(prefix=IPNetwork('10.64.0.0/10')),
        ))
        self.assertEqual(aggregate.get_utilization(), 50)

        # 100% utilization
        Prefix.objects.bulk_create((
            Prefix(prefix=IPNetwork('10.128.0.0/9')),
        ))
        self.assertEqual(aggregate.get_utilization(), 100)


class IPRangeTestCase(TestCase):

    def test_family_string(self):
        # Test property when start_address is a string
        ip_range = IPRange(start_address='10.0.0.1/24', end_address='10.0.0.254/24')
        self.assertEqual(ip_range.family, 4)
        ip_range_v6 = IPRange(start_address='2001:db8::1/64', end_address='2001:db8::ffff/64')
        self.assertEqual(ip_range_v6.family, 6)

    def test_overlapping_range(self):
        iprange_192_168 = IPRange.objects.create(
            start_address=IPNetwork('192.168.0.1/22'), end_address=IPNetwork('192.168.0.49/22')
        )
        iprange_192_168.clean()
        iprange_3_1_99 = IPRange.objects.create(
            start_address=IPNetwork('1.2.3.1/24'), end_address=IPNetwork('1.2.3.99/24')
        )
        iprange_3_1_99.clean()
        iprange_3_100_199 = IPRange.objects.create(
            start_address=IPNetwork('1.2.3.100/24'), end_address=IPNetwork('1.2.3.199/24')
        )
        iprange_3_100_199.clean()
        iprange_3_200_255 = IPRange.objects.create(
            start_address=IPNetwork('1.2.3.200/24'), end_address=IPNetwork('1.2.3.255/24')
        )
        iprange_3_200_255.clean()
        iprange_4_1_99 = IPRange.objects.create(
            start_address=IPNetwork('1.2.4.1/24'), end_address=IPNetwork('1.2.4.99/24')
        )
        iprange_4_1_99.clean()
        iprange_4_200 = IPRange.objects.create(
            start_address=IPNetwork('1.2.4.200/24'), end_address=IPNetwork('1.2.4.255/24')
        )
        iprange_4_200.clean()

        # Overlapping range entirely within existing
        with self.assertRaises(ValidationError):
            iprange_3_123_124 = IPRange.objects.create(
                start_address=IPNetwork('1.2.3.123/26'), end_address=IPNetwork('1.2.3.124/26')
            )
            iprange_3_123_124.clean()

        # Overlapping range starting within existing
        with self.assertRaises(ValidationError):
            iprange_4_98_101 = IPRange.objects.create(
                start_address=IPNetwork('1.2.4.98/24'), end_address=IPNetwork('1.2.4.101/24')
            )
            iprange_4_98_101.clean()

        # Overlapping range ending within existing
        with self.assertRaises(ValidationError):
            iprange_4_198_201 = IPRange.objects.create(
                start_address=IPNetwork('1.2.4.198/24'), end_address=IPNetwork('1.2.4.201/24')
            )
            iprange_4_198_201.clean()

    def test_single_address_range(self):
        iprange = IPRange(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.10/24'),
        )

        iprange.clean()
        iprange.save()

        self.assertEqual(iprange.size, 1)
        self.assertEqual(str(iprange), '192.0.2.10-192.0.2.10/24')
        self.assertEqual(iprange.get_first_available_ip(), '192.0.2.10/24')

    def test_first_available_ip_consumed_single_address_range(self):
        iprange = IPRange.objects.create(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.10/24'),
        )
        IPAddress.objects.create(address=IPNetwork('192.0.2.10/24'))

        # The sole address in the range is now assigned, so no IPs remain available.
        self.assertIsNone(iprange.get_first_available_ip())

    def test_single_address_range_ipv6(self):
        # IPRange.name has IPv4/IPv6-specific formatting; exercise the IPv6 branch
        # for a single-address range too.
        iprange = IPRange(
            start_address=IPNetwork('2001:db8::10/64'),
            end_address=IPNetwork('2001:db8::10/64'),
        )

        iprange.clean()
        iprange.save()

        self.assertEqual(iprange.size, 1)
        self.assertEqual(str(iprange), '2001:db8::10-2001:db8::10/64')
        self.assertEqual(iprange.get_first_available_ip(), '2001:db8::10/64')

    def test_reversed_range(self):
        iprange = IPRange(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.9/24'),
        )

        with self.assertRaises(ValidationError):
            iprange.clean()

    def test_overlapping_single_address_range(self):
        IPRange.objects.create(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.10/24'),
        )

        iprange = IPRange(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.10/24'),
        )

        # Assert the overlap-specific error message so this test cannot pass on a
        # regression where start_address == end_address is rejected earlier.
        with self.assertRaisesMessage(ValidationError, 'Defined addresses overlap'):
            iprange.clean()

    def test_get_child_ips_host_portion(self):
        iprange = IPRange.objects.create(
            start_address=IPNetwork('10.0.0.2/24'),
            end_address=IPNetwork('10.0.0.254/24'),
        )

        ip1 = IPAddress.objects.create(address=IPNetwork('10.0.0.2/32'))
        ip2 = IPAddress.objects.create(address=IPNetwork('10.0.0.3/24'))

        self.assertEqual(set(iprange.get_child_ips()), {ip1, ip2})

    def test_get_available_ips(self):
        """
        Tests that occupied hosts are deduplicated and excluded from the available set.
        """
        iprange = IPRange.objects.create(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.13/24'),
        )
        IPAddress.objects.bulk_create((
            IPAddress(address=IPNetwork('192.0.2.10/24')),
            IPAddress(address=IPNetwork('192.0.2.10/32')),
        ))

        self.assertEqual(iprange.get_available_ips(), IPSet(['192.0.2.11/32', '192.0.2.12/31']))

    def test_get_available_ips_mark_populated(self):
        """
        Tests that a populated range reports no available IPs.
        """
        iprange = IPRange.objects.create(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.13/24'),
            mark_populated=True,
        )

        self.assertEqual(iprange.get_available_ips(), IPSet())

    def test_get_available_ips_vrf(self):
        """
        Tests that IPs in other VRFs do not consume range space.
        """
        vrf1 = VRF.objects.create(name='VRF 1')
        vrf2 = VRF.objects.create(name='VRF 2')
        iprange = IPRange.objects.create(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.11/24'),
            vrf=vrf1,
        )
        IPAddress.objects.create(address=IPNetwork('192.0.2.10/24'), vrf=vrf2)

        self.assertEqual(iprange.get_available_ips(), IPSet(['192.0.2.10/31']))

    def test_iter_available_ips(self):
        """
        Tests that iter_available_ips() yields the same addresses as get_available_ips() in order.
        """
        iprange = IPRange.objects.create(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.13/24'),
        )
        IPAddress.objects.create(address=IPNetwork('192.0.2.11/24'))

        self.assertEqual(list(iprange.iter_available_ips()), sorted(iprange.get_available_ips()))

    def test_available_ip_count(self):
        iprange = IPRange.objects.create(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.19/24'),
        )

        IPAddress.objects.create(address=IPNetwork('192.0.2.12/24'))

        self.assertEqual(iprange.get_available_ip_count(), 9)

    def test_available_ip_count_distinct_hosts(self):
        iprange = IPRange.objects.create(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.19/24'),
        )

        # Two rows for .10 (different masks) must dedupe to a single occupied host.
        IPAddress.objects.bulk_create((
            IPAddress(address=IPNetwork('192.0.2.10/24')),
            IPAddress(address=IPNetwork('192.0.2.10/32')),
            IPAddress(address=IPNetwork('192.0.2.11/24')),
        ))

        self.assertEqual(iprange.get_available_ip_count(), 8)

    def test_available_ip_count_vrf(self):
        vrf1 = VRF.objects.create(name='VRF 1')
        vrf2 = VRF.objects.create(name='VRF 2')

        iprange = IPRange.objects.create(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.19/24'),
            vrf=vrf1,
        )

        IPAddress.objects.create(address=IPNetwork('192.0.2.12/24'), vrf=vrf1)
        IPAddress.objects.create(address=IPNetwork('192.0.2.13/24'), vrf=vrf2)

        # Only the VRF 1 IP should count.
        self.assertEqual(iprange.get_available_ip_count(), 9)

    def test_available_ip_count_populated(self):
        iprange = IPRange.objects.create(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.19/24'),
            mark_populated=True,
        )

        self.assertEqual(iprange.get_available_ip_count(), 0)

    def test_first_available_ip_full(self):
        iprange = IPRange.objects.create(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.11/24'),
        )

        IPAddress.objects.create(address=IPNetwork('192.0.2.10/24'))
        IPAddress.objects.create(address=IPNetwork('192.0.2.11/24'))

        self.assertIsNone(iprange.get_first_available_ip())

    def test_first_available_ip_populated(self):
        iprange = IPRange.objects.create(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.19/24'),
            mark_populated=True,
        )

        self.assertIsNone(iprange.get_first_available_ip())

    def test_first_available_ip_ipv6(self):
        iprange = IPRange.objects.create(
            start_address=IPNetwork('::/126'),
            end_address=IPNetwork('::3/126'),
        )

        self.assertEqual(iprange.get_first_available_ip(), '::/126')

    def test_utilization_distinct_hosts(self):
        iprange = IPRange.objects.create(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.19/24'),
        )

        IPAddress.objects.bulk_create((
            IPAddress(address=IPNetwork('192.0.2.10/24')),
            IPAddress(address=IPNetwork('192.0.2.10/32')),
            IPAddress(address=IPNetwork('192.0.2.11/24')),
        ))

        # Two distinct hosts in a 10-address range.
        self.assertEqual(iprange.utilization, 2 / 10 * 100)

    def test_utilization_vrf(self):
        vrf1 = VRF.objects.create(name='VRF 1')
        vrf2 = VRF.objects.create(name='VRF 2')

        iprange = IPRange.objects.create(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.19/24'),
            vrf=vrf1,
        )

        IPAddress.objects.create(address=IPNetwork('192.0.2.12/24'), vrf=vrf1)
        IPAddress.objects.create(address=IPNetwork('192.0.2.13/24'), vrf=vrf2)

        # Only the VRF 1 IP counts toward utilization.
        self.assertEqual(iprange.utilization, 1 / 10 * 100)

    def test_utilization_duplicate_ips_vrf(self):
        """
        Tests that identical IPs in a non-unique VRF count once toward range utilization.
        """
        vrf = VRF.objects.create(name='VRF 1', enforce_unique=False)
        iprange = IPRange.objects.create(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.19/24'),
            vrf=vrf,
        )

        IPAddress.objects.bulk_create((
            IPAddress(address=IPNetwork('192.0.2.12/24'), vrf=vrf),
            IPAddress(address=IPNetwork('192.0.2.12/24'), vrf=vrf),
        ))

        self.assertEqual(iprange.utilization, 1 / 10 * 100)


class PrefixTestCase(TestCase):

    def assertAvailableIPCountMatchesIPSet(self, prefix):
        """
        Confirm that get_available_ip_count() matches get_available_ips().size for the supplied prefix.
        """
        self.assertEqual(prefix.get_available_ip_count(), prefix.get_available_ips().size)

    def test_family_string(self):
        # Test property when prefix is a string
        prefix = Prefix(prefix='10.0.0.0/8')
        self.assertEqual(prefix.family, 4)
        prefix_v6 = Prefix(prefix='2001:db8::/32')
        self.assertEqual(prefix_v6.family, 6)

    def test_mask_length_string(self):
        # Test property when prefix is a string
        prefix = Prefix(prefix='10.0.0.0/8')
        self.assertEqual(prefix.mask_length, 8)
        prefix_v6 = Prefix(prefix='2001:db8::/32')
        self.assertEqual(prefix_v6.mask_length, 32)

    def test_get_duplicates(self):
        prefixes = Prefix.objects.bulk_create((
            Prefix(prefix=IPNetwork('192.0.2.0/24')),
            Prefix(prefix=IPNetwork('192.0.2.0/24')),
            Prefix(prefix=IPNetwork('192.0.2.0/24')),
        ))
        duplicate_prefix_pks = [p.pk for p in prefixes[0].get_duplicates()]

        self.assertSetEqual(set(duplicate_prefix_pks), {prefixes[1].pk, prefixes[2].pk})

    def test_get_child_prefixes(self):
        vrfs = VRF.objects.bulk_create((
            VRF(name='VRF 1'),
            VRF(name='VRF 2'),
            VRF(name='VRF 3'),
        ))
        prefixes = Prefix.objects.bulk_create((
            Prefix(prefix=IPNetwork('10.0.0.0/16'), status=PrefixStatusChoices.STATUS_CONTAINER),
            Prefix(prefix=IPNetwork('10.0.0.0/24'), vrf=None),
            Prefix(prefix=IPNetwork('10.0.1.0/24'), vrf=vrfs[0]),
            Prefix(prefix=IPNetwork('10.0.2.0/24'), vrf=vrfs[1]),
            Prefix(prefix=IPNetwork('10.0.3.0/24'), vrf=vrfs[2]),
        ))
        child_prefix_pks = {p.pk for p in prefixes[0].get_child_prefixes()}

        # Global container should return all children
        self.assertSetEqual(child_prefix_pks, {prefixes[1].pk, prefixes[2].pk, prefixes[3].pk, prefixes[4].pk})

        prefixes[0].vrf = vrfs[0]
        prefixes[0].save()
        child_prefix_pks = {p.pk for p in prefixes[0].get_child_prefixes()}

        # VRF container is limited to its own VRF
        self.assertSetEqual(child_prefix_pks, {prefixes[2].pk})

    def test_get_child_ranges(self):
        prefix = Prefix(prefix='192.168.0.16/28')
        prefix.save()
        ranges = IPRange.objects.bulk_create(
            (
                # No overlap
                IPRange(
                    start_address=IPNetwork('192.168.0.1/24'), end_address=IPNetwork('192.168.0.10/24'), size=10
                ),
                # Partial overlap
                IPRange(
                    start_address=IPNetwork('192.168.0.11/24'), end_address=IPNetwork('192.168.0.17/24'), size=7
                ),
                # Full overlap
                IPRange(
                    start_address=IPNetwork('192.168.0.18/24'), end_address=IPNetwork('192.168.0.23/24'), size=6
                ),
                # Full overlap
                IPRange(
                    start_address=IPNetwork('192.168.0.24/24'), end_address=IPNetwork('192.168.0.30/24'), size=7
                ),
                # Partial overlap
                IPRange(
                    start_address=IPNetwork('192.168.0.31/24'), end_address=IPNetwork('192.168.0.40/24'), size=10
                ),
            )
        )

        child_ranges = prefix.get_child_ranges()

        self.assertEqual(len(child_ranges), 2)
        self.assertEqual(child_ranges[0], ranges[2])
        self.assertEqual(child_ranges[1], ranges[3])

    def test_get_child_ranges_other_family(self):
        """
        Tests that ranges of a different address family are not returned.
        """
        prefix = Prefix.objects.create(prefix=IPNetwork('192.168.0.16/28'))
        IPRange.objects.bulk_create((
            IPRange(
                start_address=IPNetwork('192.168.0.18/28'), end_address=IPNetwork('192.168.0.20/28'), size=3
            ),
            IPRange(start_address=IPNetwork('::1/64'), end_address=IPNetwork('::2/64'), size=2),
        ))

        child_ranges = prefix.get_child_ranges()

        self.assertEqual(len(child_ranges), 1)
        self.assertEqual(child_ranges[0].start_address, IPNetwork('192.168.0.18/28'))

    def test_get_child_ips(self):
        vrfs = VRF.objects.bulk_create((
            VRF(name='VRF 1'),
            VRF(name='VRF 2'),
            VRF(name='VRF 3'),
        ))
        parent_prefix = Prefix.objects.create(
            prefix=IPNetwork('10.0.0.0/16'), status=PrefixStatusChoices.STATUS_CONTAINER
        )
        ips = IPAddress.objects.bulk_create((
            IPAddress(address=IPNetwork('10.0.0.1/24'), vrf=None),
            IPAddress(address=IPNetwork('10.0.1.1/24'), vrf=vrfs[0]),
            IPAddress(address=IPNetwork('10.0.2.1/24'), vrf=vrfs[1]),
            IPAddress(address=IPNetwork('10.0.3.1/24'), vrf=vrfs[2]),
        ))
        child_ip_pks = {p.pk for p in parent_prefix.get_child_ips()}

        # Global container should return all children
        self.assertSetEqual(child_ip_pks, {ips[0].pk, ips[1].pk, ips[2].pk, ips[3].pk})

        parent_prefix.vrf = vrfs[0]
        parent_prefix.save()
        child_ip_pks = {p.pk for p in parent_prefix.get_child_ips()}

        # VRF container is limited to its own VRF
        self.assertSetEqual(child_ip_pks, {ips[1].pk})

    def test_get_available_prefixes(self):

        prefixes = Prefix.objects.bulk_create((
            Prefix(prefix=IPNetwork('10.0.0.0/16')),  # Parent prefix
            Prefix(prefix=IPNetwork('10.0.0.0/20')),
            Prefix(prefix=IPNetwork('10.0.32.0/20')),
            Prefix(prefix=IPNetwork('10.0.128.0/18')),
        ))
        missing_prefixes = IPSet([
            IPNetwork('10.0.16.0/20'),
            IPNetwork('10.0.48.0/20'),
            IPNetwork('10.0.64.0/18'),
            IPNetwork('10.0.192.0/18'),
        ])
        available_prefixes = prefixes[0].get_available_prefixes()

        self.assertEqual(available_prefixes, missing_prefixes)

    def test_get_available_ips(self):

        parent_prefix = Prefix.objects.create(prefix=IPNetwork('10.0.0.0/28'))
        IPAddress.objects.bulk_create((
            IPAddress(address=IPNetwork('10.0.0.1/26')),
            IPAddress(address=IPNetwork('10.0.0.3/26')),
            IPAddress(address=IPNetwork('10.0.0.5/26')),
            IPAddress(address=IPNetwork('10.0.0.7/26')),
        ))
        # Range is not marked as populated, so it doesn't count against available IP space
        IPRange.objects.create(
            start_address=IPNetwork('10.0.0.9/26'),
            end_address=IPNetwork('10.0.0.10/26')
        )
        # Populated range reduces available IP space
        IPRange.objects.create(
            start_address=IPNetwork('10.0.0.12/26'),
            end_address=IPNetwork('10.0.0.13/26'),
            mark_populated=True
        )
        missing_ips = IPSet([
            '10.0.0.2/32',
            '10.0.0.4/32',
            '10.0.0.6/32',
            '10.0.0.8/32',
            '10.0.0.9/32',
            '10.0.0.10/32',
            '10.0.0.11/32',
            '10.0.0.14/32',
        ])
        available_ips = parent_prefix.get_available_ips()

        self.assertEqual(available_ips, missing_ips)

    def test_iter_available_ips(self):
        """
        Tests that iter_available_ips() yields the same addresses as get_available_ips() in order.
        """
        parent_prefix = Prefix.objects.create(prefix=IPNetwork('10.0.0.0/28'))
        IPAddress.objects.bulk_create((
            IPAddress(address=IPNetwork('10.0.0.1/28')),
            IPAddress(address=IPNetwork('10.0.0.5/28')),
        ))
        IPRange.objects.create(
            start_address=IPNetwork('10.0.0.8/28'),
            end_address=IPNetwork('10.0.0.9/28'),
            mark_populated=True,
        )

        available_ips = list(parent_prefix.iter_available_ips())

        self.assertEqual(available_ips, sorted(parent_prefix.get_available_ips()))
        self.assertEqual(available_ips[0], netaddr.IPAddress('10.0.0.2'))
        self.assertEqual(available_ips[-1], netaddr.IPAddress('10.0.0.14'))

    def test_get_available_ips_ipv6(self):
        """
        Tests that the subnet-router anycast address is excluded and the last address included.
        """
        parent_prefix = Prefix.objects.create(prefix=IPNetwork('2001:db8::/126'))
        IPAddress.objects.create(address=IPNetwork('2001:db8::1/126'))

        self.assertEqual(parent_prefix.get_available_ips(), IPSet(['2001:db8::2/127']))

    def test_get_available_ips_pool(self):
        """
        Tests that pool prefixes include the network and broadcast addresses.
        """
        parent_prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/30'), is_pool=True)
        IPAddress.objects.create(address=IPNetwork('192.0.2.1/30'))

        self.assertEqual(parent_prefix.get_available_ips(), IPSet(['192.0.2.0/32', '192.0.2.2/31']))

    def test_available_ip_count_distinct_hosts(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/29'),
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        IPAddress.objects.bulk_create((
            IPAddress(address=IPNetwork('192.0.2.1/29')),
            IPAddress(address=IPNetwork('192.0.2.1/32')),
            IPAddress(address=IPNetwork('192.0.2.3/29')),
        ))

        # Usable hosts in /29: 6. Two unique hosts occupy .1 and .3.
        self.assertEqual(prefix.get_available_ip_count(), 4)
        self.assertAvailableIPCountMatchesIPSet(prefix)

    def test_available_ip_count_populated_ranges(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/29'),
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        IPAddress.objects.bulk_create((
            IPAddress(address=IPNetwork('192.0.2.1/29')),
            IPAddress(address=IPNetwork('192.0.2.3/29')),  # Inside the populated range; not double-counted.
        ))

        IPRange.objects.create(
            start_address=IPNetwork('192.0.2.3/29'),
            end_address=IPNetwork('192.0.2.4/29'),
            mark_populated=True,
        )

        # Usable 6, one IP outside the range at .1, populated range covers .3-.4.
        # Available: .2, .5, .6.
        self.assertEqual(prefix.get_available_ip_count(), 3)
        self.assertAvailableIPCountMatchesIPSet(prefix)

    def test_available_ip_count_ipv4_pool(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/30'),
            status=PrefixStatusChoices.STATUS_ACTIVE,
            is_pool=True,
        )

        self.assertEqual(prefix.get_available_ip_count(), 4)
        self.assertAvailableIPCountMatchesIPSet(prefix)

    def test_available_ip_count_ipv4_non_pool(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/30'),
            status=PrefixStatusChoices.STATUS_ACTIVE,
            is_pool=False,
        )

        self.assertEqual(prefix.get_available_ip_count(), 2)
        self.assertAvailableIPCountMatchesIPSet(prefix)

    def test_available_ip_count_ipv4_non_pool_ignores_unusable_ips(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/30'),
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        # Network and broadcast addresses are unusable for non-pool IPv4 prefixes;
        # an IP assigned to either must not reduce the available count.
        IPAddress.objects.create(address=IPNetwork('192.0.2.0/30'))
        IPAddress.objects.create(address=IPNetwork('192.0.2.3/30'))

        self.assertEqual(prefix.get_available_ip_count(), 2)
        self.assertEqual(prefix.get_first_available_ip(), '192.0.2.1/30')
        self.assertAvailableIPCountMatchesIPSet(prefix)

    def test_available_ip_count_ipv6(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('2001:db8::/126'),
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        # /126 has 4 addresses; normal IPv6 prefix excludes the first.
        self.assertEqual(prefix.get_available_ip_count(), 3)
        self.assertAvailableIPCountMatchesIPSet(prefix)

    def test_available_ip_count_ipv6_ignores_subnet_router_anycast(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('2001:db8::/126'),
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        # The subnet-router anycast (::) address is unusable for normal IPv6 prefixes;
        # an IP assigned there must not reduce the available count.
        IPAddress.objects.create(address=IPNetwork('2001:db8::/126'))

        self.assertEqual(prefix.get_available_ip_count(), 3)
        self.assertEqual(prefix.get_first_available_ip(), '2001:db8::1/126')
        self.assertAvailableIPCountMatchesIPSet(prefix)

    def test_available_ip_count_ipv6_127(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('2001:db8::/127'),
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        self.assertEqual(prefix.get_available_ip_count(), 2)
        self.assertAvailableIPCountMatchesIPSet(prefix)

    def test_available_ip_count_ipv6_populated_range(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('2001:db8::/126'),
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        IPRange.objects.create(
            start_address=IPNetwork('2001:db8::1/126'),
            end_address=IPNetwork('2001:db8::2/126'),
            mark_populated=True,
        )

        # Usable IPv6 hosts in /126: ::1, ::2, ::3. Populated: ::1-::2.
        self.assertEqual(prefix.get_available_ip_count(), 1)
        self.assertEqual(prefix.get_first_available_ip(), '2001:db8::3/126')
        self.assertAvailableIPCountMatchesIPSet(prefix)

    def test_available_ip_count_overlapping_ranges(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/29'),
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        IPRange.objects.create(
            start_address=IPNetwork('192.0.2.1/29'),
            end_address=IPNetwork('192.0.2.3/29'),
            mark_populated=True,
        )
        IPRange.objects.create(
            start_address=IPNetwork('192.0.2.2/29'),
            end_address=IPNetwork('192.0.2.4/29'),
            mark_populated=True,
        )

        # Usable hosts: .1-.6 => 6. Populated union: .1-.4 => 4. Available: .5-.6 => 2.
        self.assertEqual(prefix.get_available_ip_count(), 2)
        self.assertEqual(prefix.get_first_available_ip(), '192.0.2.5/29')
        self.assertAvailableIPCountMatchesIPSet(prefix)

    def test_available_ip_count_vrf(self):
        vrf1 = VRF.objects.create(name='VRF 1')
        vrf2 = VRF.objects.create(name='VRF 2')

        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/29'),
            vrf=vrf1,
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        IPAddress.objects.create(address=IPNetwork('192.0.2.1/29'), vrf=vrf1)
        IPAddress.objects.create(address=IPNetwork('192.0.2.2/29'), vrf=vrf2)

        # Usable .1-.6 => 6. Only the VRF 1 IP should count.
        self.assertEqual(prefix.get_available_ip_count(), 5)
        self.assertAvailableIPCountMatchesIPSet(prefix)

    def test_available_ip_count_vrf_ranges(self):
        vrf1 = VRF.objects.create(name='VRF 1')
        vrf2 = VRF.objects.create(name='VRF 2')

        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/29'),
            vrf=vrf1,
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        # Covers every usable host, but in a different VRF.
        IPRange.objects.create(
            start_address=IPNetwork('192.0.2.1/29'),
            end_address=IPNetwork('192.0.2.6/29'),
            vrf=vrf2,
            mark_populated=True,
        )

        self.assertEqual(prefix.get_available_ip_count(), 6)
        self.assertEqual(prefix.get_first_available_ip(), '192.0.2.1/29')
        self.assertAvailableIPCountMatchesIPSet(prefix)

    def test_available_ip_count_fully_populated(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/30'),
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        # Populated range covers every usable address (.1-.2 in a non-pool /30).
        IPRange.objects.create(
            start_address=IPNetwork('192.0.2.1/30'),
            end_address=IPNetwork('192.0.2.2/30'),
            mark_populated=True,
        )

        # Exercises the early-return paths that skip the child-IP count and
        # the host-stream iterator entirely.
        self.assertEqual(prefix.get_available_ip_count(), 0)
        self.assertIsNone(prefix.get_first_available_ip())
        self.assertAvailableIPCountMatchesIPSet(prefix)

    def test_available_ip_count_query_count(self):
        """
        Tests that the count runs one interval query plus exactly one host scan.
        """
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/24'))

        IPAddress.objects.bulk_create(
            IPAddress(address=IPNetwork(f'192.0.2.{i}/24')) for i in range(1, 11)
        )

        IPRange.objects.create(
            start_address=IPNetwork('192.0.2.20/24'),
            end_address=IPNetwork('192.0.2.29/24'),
            mark_populated=True,
        )

        with self.assertNumQueries(2):
            prefix.get_available_ip_count()

    def test_available_ip_count_container(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/24'),
            status=PrefixStatusChoices.STATUS_CONTAINER,
        )

        # A child prefix exists but does not reduce the available IP count.
        Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/26'),
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        self.assertEqual(prefix.get_available_ip_count(), 254)
        self.assertAvailableIPCountMatchesIPSet(prefix)

    def test_available_ip_count_container_vrf_duplicate_hosts(self):
        vrf1 = VRF.objects.create(name='VRF 1')
        vrf2 = VRF.objects.create(name='VRF 2')

        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/24'),
            status=PrefixStatusChoices.STATUS_CONTAINER,
        )

        IPAddress.objects.create(address=IPNetwork('192.0.2.1/24'), vrf=vrf1)
        IPAddress.objects.create(address=IPNetwork('192.0.2.1/24'), vrf=vrf2)
        IPAddress.objects.create(address=IPNetwork('192.0.2.2/24'), vrf=vrf2)

        # A global container counts child IPs from all VRFs; the duplicate host
        # counts once. 254 usable - 2 distinct hosts.
        self.assertEqual(prefix.get_available_ip_count(), 252)
        self.assertAvailableIPCountMatchesIPSet(prefix)

    def test_available_ip_count_container_vrf_ip_in_populated_range(self):
        vrf1 = VRF.objects.create(name='VRF 1')

        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/24'),
            status=PrefixStatusChoices.STATUS_CONTAINER,
        )

        IPRange.objects.create(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.19/24'),
            mark_populated=True,
        )
        IPAddress.objects.create(address=IPNetwork('192.0.2.15/24'), vrf=vrf1)

        # The range covers 10 hosts; the VRF 1 IP inside it is not counted again.
        self.assertEqual(prefix.get_available_ip_count(), 244)
        self.assertAvailableIPCountMatchesIPSet(prefix)

    def test_get_first_available_prefix(self):

        prefixes = Prefix.objects.bulk_create((
            Prefix(prefix=IPNetwork('10.0.0.0/16')),  # Parent prefix
            Prefix(prefix=IPNetwork('10.0.0.0/24')),
            Prefix(prefix=IPNetwork('10.0.1.0/24')),
            Prefix(prefix=IPNetwork('10.0.2.0/24')),
        ))
        self.assertEqual(prefixes[0].get_first_available_prefix(), IPNetwork('10.0.3.0/24'))

        Prefix.objects.create(prefix=IPNetwork('10.0.3.0/24'))
        self.assertEqual(prefixes[0].get_first_available_prefix(), IPNetwork('10.0.4.0/22'))

    def test_get_first_available_ip(self):

        parent_prefix = Prefix.objects.create(prefix=IPNetwork('10.0.0.0/24'))
        IPAddress.objects.bulk_create((
            IPAddress(address=IPNetwork('10.0.0.1/24')),
            IPAddress(address=IPNetwork('10.0.0.2/24')),
            IPAddress(address=IPNetwork('10.0.0.3/24')),
        ))
        self.assertEqual(parent_prefix.get_first_available_ip(), '10.0.0.4/24')

        IPAddress.objects.create(address=IPNetwork('10.0.0.4/24'))
        self.assertEqual(parent_prefix.get_first_available_ip(), '10.0.0.5/24')

    def test_get_first_available_ip_ipv6(self):
        parent_prefix = Prefix.objects.create(prefix=IPNetwork('2001:db8:500::/64'))
        self.assertEqual(parent_prefix.get_first_available_ip(), '2001:db8:500::1/64')

    def test_get_first_available_ip_ipv6_rfc3627(self):
        parent_prefix = Prefix.objects.create(prefix=IPNetwork('2001:db8:500:4::/126'))
        self.assertEqual(parent_prefix.get_first_available_ip(), '2001:db8:500:4::1/126')

    def test_get_first_available_ip_ipv6_rfc6164(self):
        parent_prefix = Prefix.objects.create(prefix=IPNetwork('2001:db8:500:5::/127'))
        self.assertEqual(parent_prefix.get_first_available_ip(), '2001:db8:500:5::/127')

    def test_get_first_available_ip_ipv6_zero_address(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('::/126'),
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        # Normal IPv6 prefixes exclude the subnet-router anycast address ::.
        self.assertEqual(prefix.get_first_available_ip(), '::1/126')

    def test_get_first_available_ip_populated_ranges(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/29'),
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        IPAddress.objects.create(address=IPNetwork('192.0.2.1/29'))

        IPRange.objects.create(
            start_address=IPNetwork('192.0.2.2/29'),
            end_address=IPNetwork('192.0.2.3/29'),
            mark_populated=True,
        )

        self.assertEqual(prefix.get_first_available_ip(), '192.0.2.4/29')

    def test_get_first_available_ip_full(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/30'),
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        IPAddress.objects.create(address=IPNetwork('192.0.2.1/30'))
        IPAddress.objects.create(address=IPNetwork('192.0.2.2/30'))

        self.assertIsNone(prefix.get_first_available_ip())

    def test_get_utilization_container(self):
        prefixes = (
            Prefix(prefix=IPNetwork('10.0.0.0/24'), status=PrefixStatusChoices.STATUS_CONTAINER),
            Prefix(prefix=IPNetwork('10.0.0.0/26')),
            Prefix(prefix=IPNetwork('10.0.0.128/26')),
        )
        Prefix.objects.bulk_create(prefixes)
        self.assertEqual(prefixes[0].get_utilization(), 50)  # 50% utilization

    def test_get_utilization_noncontainer(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('10.0.0.0/24'),
            status=PrefixStatusChoices.STATUS_ACTIVE
        )

        # Create 32 child IPs
        IPAddress.objects.bulk_create([
            IPAddress(address=IPNetwork(f'10.0.0.{i}/24')) for i in range(1, 33)
        ])
        self.assertEqual(prefix.get_utilization(), 32 / 254 * 100)  # ~12.5% utilization

        # Create a utilized child range with 32 additional IPs
        IPRange.objects.create(
            start_address=IPNetwork('10.0.0.33/24'),
            end_address=IPNetwork('10.0.0.64/24'),
            mark_utilized=True
        )
        self.assertEqual(prefix.get_utilization(), 64 / 254 * 100)  # ~25% utilization

    def test_get_utilization_distinct_hosts(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/24'),
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        IPAddress.objects.bulk_create((
            IPAddress(address=IPNetwork('192.0.2.10/24')),
            IPAddress(address=IPNetwork('192.0.2.10/32')),
            IPAddress(address=IPNetwork('192.0.2.11/24')),
        ))

        # Two unique occupied hosts over 254 usable IPv4 addresses.
        self.assertEqual(prefix.get_utilization(), 2 / 254 * 100)

    @override_settings(ENFORCE_GLOBAL_UNIQUE=False)
    def test_get_utilization_duplicate_ips_global(self):
        """
        Tests that identical global IPs permitted by disabled uniqueness count as one host.
        """
        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/24'),
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        IPAddress.objects.create(address=IPNetwork('192.0.2.10/24'))
        duplicate_ip = IPAddress(address=IPNetwork('192.0.2.10/24'))
        self.assertIsNone(duplicate_ip.clean())
        duplicate_ip.save()

        self.assertEqual(prefix.get_utilization(), 1 / 254 * 100)

    def test_get_utilization_duplicate_ips_vrf(self):
        """
        Tests that identical IPs in a non-unique VRF count as one host.
        """
        vrf = VRF.objects.create(name='VRF 1', enforce_unique=False)
        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/24'),
            vrf=vrf,
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        IPAddress.objects.create(address=IPNetwork('192.0.2.10/24'), vrf=vrf)
        duplicate_ip = IPAddress(address=IPNetwork('192.0.2.10/24'), vrf=vrf)
        self.assertIsNone(duplicate_ip.clean())
        duplicate_ip.save()

        self.assertEqual(prefix.get_utilization(), 1 / 254 * 100)

    def test_available_ip_count_duplicate_ips_vrf(self):
        """
        Tests that identical IPs in a non-unique VRF reduce availability once.
        """
        vrf = VRF.objects.create(name='VRF 1', enforce_unique=False)
        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/29'),
            vrf=vrf,
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        IPAddress.objects.bulk_create((
            IPAddress(address=IPNetwork('192.0.2.1/29'), vrf=vrf),
            IPAddress(address=IPNetwork('192.0.2.1/29'), vrf=vrf),
        ))

        # Usable hosts in /29: 6. The duplicate occupies a single host.
        self.assertEqual(prefix.get_available_ip_count(), 5)
        self.assertAvailableIPCountMatchesIPSet(prefix)

    @override_settings(ENFORCE_GLOBAL_UNIQUE=False)
    def test_get_ip_usage_summary_duplicate_ips_global(self):
        """
        Tests that the usage summary deduplicates identical global IPs in both values.
        """
        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/24'),
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        IPAddress.objects.bulk_create((
            IPAddress(address=IPNetwork('192.0.2.10/24')),
            IPAddress(address=IPNetwork('192.0.2.10/24')),
        ))

        summary = prefix.get_ip_usage_summary()

        self.assertEqual(summary['available_ip_count'], 253)
        self.assertEqual(summary['utilization'], 1 / 254 * 100)

    def test_get_utilization_utilized_ranges(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/24'),
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        IPRange.objects.create(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.19/24'),
            mark_utilized=True,
        )

        IPAddress.objects.bulk_create((
            IPAddress(address=IPNetwork('192.0.2.1/24')),
            IPAddress(address=IPNetwork('192.0.2.10/24')),
            IPAddress(address=IPNetwork('192.0.2.11/24')),
            IPAddress(address=IPNetwork('192.0.2.20/24')),
        ))

        # Utilized range contributes 10 hosts; IPs inside the range are not double-counted.
        # Outside IPs: .1 and .20 => 2 more.
        self.assertEqual(prefix.get_utilization(), 12 / 254 * 100)

    def test_get_utilization_overlapping_utilized_ranges(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/24'),
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        IPRange.objects.create(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.19/24'),
            mark_utilized=True,
        )
        IPRange.objects.create(
            start_address=IPNetwork('192.0.2.15/24'),
            end_address=IPNetwork('192.0.2.24/24'),
            mark_utilized=True,
        )

        # Union is .10-.24 => 15 hosts, not 20.
        self.assertEqual(prefix.get_utilization(), 15 / 254 * 100)

    def test_get_utilization_fully_utilized_range(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/24'),
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        # Utilized range covers every usable host (.1-.254 in a non-pool /24).
        IPRange.objects.create(
            start_address=IPNetwork('192.0.2.1/24'),
            end_address=IPNetwork('192.0.2.254/24'),
            mark_utilized=True,
        )

        # Exercises the early-return path that skips the child-IP count entirely.
        self.assertEqual(prefix.get_utilization(), 100)

    def test_get_utilization_ipv6_utilized_range(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('2001:db8::/126'),
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        IPRange.objects.create(
            start_address=IPNetwork('2001:db8::1/126'),
            end_address=IPNetwork('2001:db8::2/126'),
            mark_utilized=True,
        )

        self.assertEqual(prefix.get_utilization(), 2 / 4 * 100)

    def test_get_utilization_vrf(self):
        vrf1 = VRF.objects.create(name='VRF 1')
        vrf2 = VRF.objects.create(name='VRF 2')

        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/24'),
            vrf=vrf1,
            status=PrefixStatusChoices.STATUS_ACTIVE,
        )

        IPAddress.objects.create(address=IPNetwork('192.0.2.1/24'), vrf=vrf1)
        IPAddress.objects.create(address=IPNetwork('192.0.2.15/24'), vrf=vrf1)
        IPAddress.objects.create(address=IPNetwork('192.0.2.2/24'), vrf=vrf2)
        IPRange.objects.create(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.19/24'),
            vrf=vrf2,
            mark_utilized=True,
        )

        # VRF 2 objects are ignored entirely; the VRF 1 IP at .15 still counts even
        # though it falls inside the VRF 2 range's host span (exclusion intervals are
        # built only from same-VRF ranges).
        self.assertEqual(prefix.get_utilization(), 2 / 254 * 100)

    def test_get_utilization_query_count(self):
        """
        Tests that utilization for a non-container prefix uses two queries.
        """
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/24'))

        with self.assertNumQueries(2):
            prefix.get_utilization()

    def test_get_ip_usage_summary(self):
        """
        Tests that the combined summary matches the independent methods.
        """
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/24'))
        IPAddress.objects.bulk_create((
            IPAddress(address=IPNetwork('192.0.2.1/24')),
            IPAddress(address=IPNetwork('192.0.2.2/24')),
        ))
        IPRange.objects.create(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.19/24'),
            mark_utilized=True,
        )
        IPRange.objects.create(
            start_address=IPNetwork('192.0.2.30/24'),
            end_address=IPNetwork('192.0.2.39/24'),
            mark_populated=True,
        )

        summary = prefix.get_ip_usage_summary()

        self.assertEqual(summary['available_ip_count'], prefix.get_available_ip_count())
        self.assertEqual(summary['utilization'], prefix.get_utilization())

    def test_get_ip_usage_summary_query_count(self):
        """
        Tests that the combined summary uses a single distinct-host scan (three queries).
        """
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/24'))

        with self.assertNumQueries(3):
            prefix.get_ip_usage_summary()

    def test_get_ip_usage_summary_container(self):
        """
        Tests that the summary delegates to the independent methods for containers.
        """
        container = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/24'),
            status=PrefixStatusChoices.STATUS_CONTAINER,
        )

        summary = container.get_ip_usage_summary()

        self.assertEqual(summary['available_ip_count'], container.get_available_ip_count())
        self.assertEqual(summary['utilization'], container.get_utilization())

    def test_get_ip_usage_summary_mark_utilized(self):
        """
        Tests that a marked-utilized prefix reports 100% utilization in the summary.
        """
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/24'), mark_utilized=True)

        summary = prefix.get_ip_usage_summary()

        self.assertEqual(summary['utilization'], 100)
        self.assertEqual(summary['available_ip_count'], prefix.get_available_ip_count())

    def test_usable_size(self):
        self.assertEqual(Prefix(prefix=IPNetwork('192.0.2.0/24')).usable_size, 254)
        self.assertEqual(Prefix(prefix=IPNetwork('192.0.2.0/24'), is_pool=True).usable_size, 256)
        self.assertEqual(Prefix(prefix=IPNetwork('2001:db8::/126')).usable_size, 3)

    def test_usable_ip_bounds_string_prefix(self):
        """
        Tests that usable bounds are computed for a string-assigned prefix.
        """
        first_ip, last_ip = Prefix(prefix='192.0.2.0/24').usable_ip_bounds

        self.assertEqual(first_ip, netaddr.IPAddress('192.0.2.1'))
        self.assertEqual(last_ip, netaddr.IPAddress('192.0.2.254'))

    #
    # Uniqueness enforcement tests
    #

    @override_settings(ENFORCE_GLOBAL_UNIQUE=False)
    def test_duplicate_global(self):
        Prefix.objects.create(prefix=IPNetwork('192.0.2.0/24'))
        duplicate_prefix = Prefix(prefix=IPNetwork('192.0.2.0/24'))
        self.assertIsNone(duplicate_prefix.clean())

    def test_duplicate_global_unique(self):
        Prefix.objects.create(prefix=IPNetwork('192.0.2.0/24'))
        duplicate_prefix = Prefix(prefix=IPNetwork('192.0.2.0/24'))
        self.assertRaises(ValidationError, duplicate_prefix.clean)

    def test_duplicate_vrf(self):
        vrf = VRF.objects.create(name='Test', rd='1:1', enforce_unique=False)
        Prefix.objects.create(vrf=vrf, prefix=IPNetwork('192.0.2.0/24'))
        duplicate_prefix = Prefix(vrf=vrf, prefix=IPNetwork('192.0.2.0/24'))
        self.assertIsNone(duplicate_prefix.clean())

    def test_duplicate_vrf_unique(self):
        vrf = VRF.objects.create(name='Test', rd='1:1', enforce_unique=True)
        Prefix.objects.create(vrf=vrf, prefix=IPNetwork('192.0.2.0/24'))
        duplicate_prefix = Prefix(vrf=vrf, prefix=IPNetwork('192.0.2.0/24'))
        self.assertRaises(ValidationError, duplicate_prefix.clean)


class PrefixHierarchyTestCase(TestCase):
    """
    Test the automatic updating of depth and child count in response to changes made within
    the prefix hierarchy.
    """
    @classmethod
    def setUpTestData(cls):

        prefixes = (

            # IPv4
            Prefix(prefix='10.0.0.0/8', _depth=0, _children=2),
            Prefix(prefix='10.0.0.0/16', _depth=1, _children=1),
            Prefix(prefix='10.0.0.0/24', _depth=2, _children=0),

            # IPv6
            Prefix(prefix='2001:db8::/32', _depth=0, _children=2),
            Prefix(prefix='2001:db8::/40', _depth=1, _children=1),
            Prefix(prefix='2001:db8::/48', _depth=2, _children=0),

        )
        Prefix.objects.bulk_create(prefixes)

    def test_create_prefix4(self):
        # Create 10.0.0.0/12
        Prefix(prefix='10.0.0.0/12').save()

        prefixes = Prefix.objects.filter(prefix__family=4)
        self.assertEqual(prefixes[0].prefix, IPNetwork('10.0.0.0/8'))
        self.assertEqual(prefixes[0]._depth, 0)
        self.assertEqual(prefixes[0]._children, 3)
        self.assertEqual(prefixes[1].prefix, IPNetwork('10.0.0.0/12'))
        self.assertEqual(prefixes[1]._depth, 1)
        self.assertEqual(prefixes[1]._children, 2)
        self.assertEqual(prefixes[2].prefix, IPNetwork('10.0.0.0/16'))
        self.assertEqual(prefixes[2]._depth, 2)
        self.assertEqual(prefixes[2]._children, 1)
        self.assertEqual(prefixes[3].prefix, IPNetwork('10.0.0.0/24'))
        self.assertEqual(prefixes[3]._depth, 3)
        self.assertEqual(prefixes[3]._children, 0)

    def test_create_prefix6(self):
        # Create 2001:db8::/36
        Prefix(prefix='2001:db8::/36').save()

        prefixes = Prefix.objects.filter(prefix__family=6)
        self.assertEqual(prefixes[0].prefix, IPNetwork('2001:db8::/32'))
        self.assertEqual(prefixes[0]._depth, 0)
        self.assertEqual(prefixes[0]._children, 3)
        self.assertEqual(prefixes[1].prefix, IPNetwork('2001:db8::/36'))
        self.assertEqual(prefixes[1]._depth, 1)
        self.assertEqual(prefixes[1]._children, 2)
        self.assertEqual(prefixes[2].prefix, IPNetwork('2001:db8::/40'))
        self.assertEqual(prefixes[2]._depth, 2)
        self.assertEqual(prefixes[2]._children, 1)
        self.assertEqual(prefixes[3].prefix, IPNetwork('2001:db8::/48'))
        self.assertEqual(prefixes[3]._depth, 3)
        self.assertEqual(prefixes[3]._children, 0)

    def test_update_prefix4(self):
        # Change 10.0.0.0/24 to 10.0.0.0/12
        p = Prefix.objects.get(prefix='10.0.0.0/24')
        p.prefix = '10.0.0.0/12'
        p.save()

        prefixes = Prefix.objects.filter(prefix__family=4)
        self.assertEqual(prefixes[0].prefix, IPNetwork('10.0.0.0/8'))
        self.assertEqual(prefixes[0]._depth, 0)
        self.assertEqual(prefixes[0]._children, 2)
        self.assertEqual(prefixes[1].prefix, IPNetwork('10.0.0.0/12'))
        self.assertEqual(prefixes[1]._depth, 1)
        self.assertEqual(prefixes[1]._children, 1)
        self.assertEqual(prefixes[2].prefix, IPNetwork('10.0.0.0/16'))
        self.assertEqual(prefixes[2]._depth, 2)
        self.assertEqual(prefixes[2]._children, 0)

    def test_update_prefix6(self):
        # Change 2001:db8::/48 to 2001:db8::/36
        p = Prefix.objects.get(prefix='2001:db8::/48')
        p.prefix = '2001:db8::/36'
        p.save()

        prefixes = Prefix.objects.filter(prefix__family=6)
        self.assertEqual(prefixes[0].prefix, IPNetwork('2001:db8::/32'))
        self.assertEqual(prefixes[0]._depth, 0)
        self.assertEqual(prefixes[0]._children, 2)
        self.assertEqual(prefixes[1].prefix, IPNetwork('2001:db8::/36'))
        self.assertEqual(prefixes[1]._depth, 1)
        self.assertEqual(prefixes[1]._children, 1)
        self.assertEqual(prefixes[2].prefix, IPNetwork('2001:db8::/40'))
        self.assertEqual(prefixes[2]._depth, 2)
        self.assertEqual(prefixes[2]._children, 0)

    def test_update_prefix_vrf4(self):
        vrf = VRF(name='VRF A')
        vrf.save()

        # Move 10.0.0.0/16 to a VRF
        p = Prefix.objects.get(prefix='10.0.0.0/16')
        p.vrf = vrf
        p.save()

        prefixes = Prefix.objects.filter(vrf__isnull=True, prefix__family=4)
        self.assertEqual(prefixes[0].prefix, IPNetwork('10.0.0.0/8'))
        self.assertEqual(prefixes[0]._depth, 0)
        self.assertEqual(prefixes[0]._children, 1)
        self.assertEqual(prefixes[1].prefix, IPNetwork('10.0.0.0/24'))
        self.assertEqual(prefixes[1]._depth, 1)
        self.assertEqual(prefixes[1]._children, 0)

        prefixes = Prefix.objects.filter(vrf=vrf)
        self.assertEqual(prefixes[0].prefix, IPNetwork('10.0.0.0/16'))
        self.assertEqual(prefixes[0]._depth, 0)
        self.assertEqual(prefixes[0]._children, 0)

    def test_update_prefix_vrf6(self):
        vrf = VRF(name='VRF A')
        vrf.save()

        # Move 2001:db8::/40 to a VRF
        p = Prefix.objects.get(prefix='2001:db8::/40')
        p.vrf = vrf
        p.save()

        prefixes = Prefix.objects.filter(vrf__isnull=True, prefix__family=6)
        self.assertEqual(prefixes[0].prefix, IPNetwork('2001:db8::/32'))
        self.assertEqual(prefixes[0]._depth, 0)
        self.assertEqual(prefixes[0]._children, 1)
        self.assertEqual(prefixes[1].prefix, IPNetwork('2001:db8::/48'))
        self.assertEqual(prefixes[1]._depth, 1)
        self.assertEqual(prefixes[1]._children, 0)

        prefixes = Prefix.objects.filter(vrf=vrf)
        self.assertEqual(prefixes[0].prefix, IPNetwork('2001:db8::/40'))
        self.assertEqual(prefixes[0]._depth, 0)
        self.assertEqual(prefixes[0]._children, 0)

    def test_delete_prefix4(self):
        # Delete 10.0.0.0/16
        Prefix.objects.filter(prefix='10.0.0.0/16').delete()

        prefixes = Prefix.objects.filter(prefix__family=4)
        self.assertEqual(prefixes[0].prefix, IPNetwork('10.0.0.0/8'))
        self.assertEqual(prefixes[0]._depth, 0)
        self.assertEqual(prefixes[0]._children, 1)
        self.assertEqual(prefixes[1].prefix, IPNetwork('10.0.0.0/24'))
        self.assertEqual(prefixes[1]._depth, 1)
        self.assertEqual(prefixes[1]._children, 0)

    def test_delete_prefix6(self):
        # Delete 2001:db8::/40
        Prefix.objects.filter(prefix='2001:db8::/40').delete()

        prefixes = Prefix.objects.filter(prefix__family=6)
        self.assertEqual(prefixes[0].prefix, IPNetwork('2001:db8::/32'))
        self.assertEqual(prefixes[0]._depth, 0)
        self.assertEqual(prefixes[0]._children, 1)
        self.assertEqual(prefixes[1].prefix, IPNetwork('2001:db8::/48'))
        self.assertEqual(prefixes[1]._depth, 1)
        self.assertEqual(prefixes[1]._children, 0)

    def test_duplicate_prefix4(self):
        # Duplicate 10.0.0.0/16
        Prefix(prefix='10.0.0.0/16').save()

        prefixes = Prefix.objects.filter(prefix__family=4)
        self.assertEqual(prefixes[0].prefix, IPNetwork('10.0.0.0/8'))
        self.assertEqual(prefixes[0]._depth, 0)
        self.assertEqual(prefixes[0]._children, 3)
        self.assertEqual(prefixes[1].prefix, IPNetwork('10.0.0.0/16'))
        self.assertEqual(prefixes[1]._depth, 1)
        self.assertEqual(prefixes[1]._children, 1)
        self.assertEqual(prefixes[2].prefix, IPNetwork('10.0.0.0/16'))
        self.assertEqual(prefixes[2]._depth, 1)
        self.assertEqual(prefixes[2]._children, 1)
        self.assertEqual(prefixes[3].prefix, IPNetwork('10.0.0.0/24'))
        self.assertEqual(prefixes[3]._depth, 2)
        self.assertEqual(prefixes[3]._children, 0)

    def test_duplicate_prefix6(self):
        # Duplicate 2001:db8::/40
        Prefix(prefix='2001:db8::/40').save()

        prefixes = Prefix.objects.filter(prefix__family=6)
        self.assertEqual(prefixes[0].prefix, IPNetwork('2001:db8::/32'))
        self.assertEqual(prefixes[0]._depth, 0)
        self.assertEqual(prefixes[0]._children, 3)
        self.assertEqual(prefixes[1].prefix, IPNetwork('2001:db8::/40'))
        self.assertEqual(prefixes[1]._depth, 1)
        self.assertEqual(prefixes[1]._children, 1)
        self.assertEqual(prefixes[2].prefix, IPNetwork('2001:db8::/40'))
        self.assertEqual(prefixes[2]._depth, 1)
        self.assertEqual(prefixes[2]._children, 1)
        self.assertEqual(prefixes[3].prefix, IPNetwork('2001:db8::/48'))
        self.assertEqual(prefixes[3]._depth, 2)
        self.assertEqual(prefixes[3]._children, 0)

    def test_rebuild_prefixes_accepts_vrf_identifier(self):
        # None means "global table". Wipe the precomputed hierarchy so the rebuild is observable.
        Prefix.objects.update(_depth=0, _children=0)

        rebuild_prefixes(None)

        top = Prefix.objects.get(prefix='10.0.0.0/8')
        mid = Prefix.objects.get(prefix='10.0.0.0/16')
        leaf = Prefix.objects.get(prefix='10.0.0.0/24')
        self.assertEqual((top._depth, top._children), (0, 2))
        self.assertEqual((mid._depth, mid._children), (1, 1))
        self.assertEqual((leaf._depth, leaf._children), (2, 0))

    def test_rebuild_prefixes_accepts_vrf_pk(self):
        # A VRF pk filters to that VRF's prefixes.
        vrf = VRF.objects.create(name='VRF 1')
        Prefix.objects.create(prefix=IPNetwork('192.0.2.0/24'), vrf=vrf)
        Prefix.objects.create(prefix=IPNetwork('192.0.2.0/25'), vrf=vrf)

        # Reset depth/children so the rebuild has something to restore.
        Prefix.objects.filter(vrf=vrf).update(_depth=0, _children=0)

        rebuild_prefixes(vrf.pk)

        parent = Prefix.objects.get(prefix='192.0.2.0/24', vrf=vrf)
        child = Prefix.objects.get(prefix='192.0.2.0/25', vrf=vrf)
        self.assertEqual((parent._depth, parent._children), (0, 1))
        self.assertEqual((child._depth, child._children), (1, 0))


class IPAddressTestCase(TestCase):

    def test_family_string(self):
        # Test property when address is a string
        ip = IPAddress(address='10.0.0.1/24')
        self.assertEqual(ip.family, 4)
        ip_v6 = IPAddress(address='2001:db8::1/64')
        self.assertEqual(ip_v6.family, 6)

    def test_get_duplicates(self):
        ips = IPAddress.objects.bulk_create((
            IPAddress(address=IPNetwork('192.0.2.1/24')),
            IPAddress(address=IPNetwork('192.0.2.1/24')),
            IPAddress(address=IPNetwork('192.0.2.1/24')),
        ))
        duplicate_ip_pks = [p.pk for p in ips[0].get_duplicates()]

        self.assertSetEqual(set(duplicate_ip_pks), {ips[1].pk, ips[2].pk})

    #
    # Uniqueness enforcement tests
    #

    @override_settings(ENFORCE_GLOBAL_UNIQUE=False)
    def test_duplicate_global(self):
        IPAddress.objects.create(address=IPNetwork('192.0.2.1/24'))
        duplicate_ip = IPAddress(address=IPNetwork('192.0.2.1/24'))
        self.assertIsNone(duplicate_ip.clean())

    def test_duplicate_global_unique(self):
        IPAddress.objects.create(address=IPNetwork('192.0.2.1/24'))
        duplicate_ip = IPAddress(address=IPNetwork('192.0.2.1/24'))
        self.assertRaises(ValidationError, duplicate_ip.clean)

    def test_duplicate_vrf(self):
        vrf = VRF.objects.create(name='Test', rd='1:1', enforce_unique=False)
        IPAddress.objects.create(vrf=vrf, address=IPNetwork('192.0.2.1/24'))
        duplicate_ip = IPAddress(vrf=vrf, address=IPNetwork('192.0.2.1/24'))
        self.assertIsNone(duplicate_ip.clean())

    def test_duplicate_vrf_unique(self):
        vrf = VRF.objects.create(name='Test', rd='1:1', enforce_unique=True)
        IPAddress.objects.create(vrf=vrf, address=IPNetwork('192.0.2.1/24'))
        duplicate_ip = IPAddress(vrf=vrf, address=IPNetwork('192.0.2.1/24'))
        self.assertRaises(ValidationError, duplicate_ip.clean)

    def test_duplicate_nonunique_nonrole_role(self):
        IPAddress.objects.create(address=IPNetwork('192.0.2.1/24'))
        duplicate_ip = IPAddress(address=IPNetwork('192.0.2.1/24'), role=IPAddressRoleChoices.ROLE_VIP)
        self.assertRaises(ValidationError, duplicate_ip.clean)

    def test_duplicate_nonunique_role_nonrole(self):
        IPAddress.objects.create(address=IPNetwork('192.0.2.1/24'), role=IPAddressRoleChoices.ROLE_VIP)
        duplicate_ip = IPAddress(address=IPNetwork('192.0.2.1/24'))
        self.assertRaises(ValidationError, duplicate_ip.clean)

    def test_duplicate_nonunique_role(self):
        IPAddress.objects.create(address=IPNetwork('192.0.2.1/24'), role=IPAddressRoleChoices.ROLE_VIP)
        IPAddress.objects.create(address=IPNetwork('192.0.2.1/24'), role=IPAddressRoleChoices.ROLE_VIP)

    #
    # Range validation
    #

    def test_create_ip_in_unpopulated_range(self):
        IPRange.objects.create(
            start_address=IPNetwork('192.0.2.1/24'),
            end_address=IPNetwork('192.0.2.100/24')
        )
        ip = IPAddress(address=IPNetwork('192.0.2.10/24'))
        ip.full_clean()

    def test_create_ip_in_populated_range(self):
        IPRange.objects.create(
            start_address=IPNetwork('192.0.2.1/24'),
            end_address=IPNetwork('192.0.2.100/24'),
            mark_populated=True
        )
        ip = IPAddress(address=IPNetwork('192.0.2.10/24'))
        self.assertRaises(ValidationError, ip.full_clean)

    def test_mark_populated_single_address_range_blocks_ip(self):
        # A single-address range with mark_populated=True must still block creation
        # of an IPAddress at the same host with the same mask.
        IPRange.objects.create(
            start_address=IPNetwork('192.0.2.10/24'),
            end_address=IPNetwork('192.0.2.10/24'),
            mark_populated=True,
        )
        ipaddress = IPAddress(address=IPNetwork('192.0.2.10/24'))

        with self.assertRaisesMessage(ValidationError, 'Cannot create IP address'):
            ipaddress.clean()

    def test_populated_range_blocks_ip_with_different_mask(self):
        # The populated-range check compares by host portion, so a different mask
        # must not let an IPAddress slip past validation.
        IPRange.objects.create(
            start_address=IPNetwork('10.0.0.2/24'),
            end_address=IPNetwork('10.0.0.254/24'),
            mark_populated=True,
        )

        ip = IPAddress(address=IPNetwork('10.0.0.2/32'))

        with self.assertRaises(ValidationError):
            ip.full_clean()


class VLANGroupTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        vlangroup = VLANGroup.objects.create(
            name='VLAN Group 1',
            slug='vlan-group-1',
            vid_ranges=string_to_ranges('100-199'),
        )
        VLAN.objects.bulk_create((
            VLAN(name='VLAN 100', vid=100, group=vlangroup),
            VLAN(name='VLAN 101', vid=101, group=vlangroup),
            VLAN(name='VLAN 102', vid=102, group=vlangroup),
            VLAN(name='VLAN 103', vid=103, group=vlangroup),
        ))

    def test_get_available_vids(self):
        vlangroup = VLANGroup.objects.first()
        child_vids = VLAN.objects.filter(group=vlangroup).values_list('vid', flat=True)
        self.assertEqual(len(child_vids), 4)

        available_vids = vlangroup.get_available_vids()
        self.assertListEqual(available_vids, list(range(104, 200)))

    def test_get_available_vids_with_inclusive_ranges(self):
        vlangroup = VLANGroup.objects.create(
            name='VLAN Group 2',
            slug='vlan-group-2',
            vid_ranges=[NumericRange(200, 204, bounds='[]')],
        )
        VLAN.objects.create(name='VLAN 200', vid=200, group=vlangroup)

        # Re-assign with non-canonical bounds to exercise the unsaved in-memory path.
        vlangroup.vid_ranges = [NumericRange(200, 204, bounds='[]')]
        self.assertListEqual(vlangroup.get_available_vids(), [201, 202, 203, 204])

    def test_get_next_available_vid(self):
        vlangroup = VLANGroup.objects.first()
        self.assertEqual(vlangroup.get_next_available_vid(), 104)

        VLAN.objects.create(name='VLAN 104', vid=104, group=vlangroup)
        self.assertEqual(vlangroup.get_next_available_vid(), 105)

    def test_vid_validation(self):
        vlangroup = VLANGroup.objects.first()

        vlan = VLAN(vid=1, name='VLAN 1', group=vlangroup)
        with self.assertRaises(ValidationError):
            vlan.full_clean()

        vlan = VLAN(vid=109, name='VLAN 109', group=vlangroup)
        vlan.full_clean()

    def test_overlapping_vlan(self):
        vlangroup = VLANGroup(
            name='VLAN Group 1',
            slug='vlan-group-1',
            vid_ranges=string_to_ranges('2-4,3-5'),
        )
        with self.assertRaises(ValidationError):
            vlangroup.full_clean()

        # make sure single vlan range works
        vlangroup.vid_ranges = string_to_ranges('2-2')
        vlangroup.full_clean()
        vlangroup.save()

    def test_total_vlan_ids(self):
        vlangroup = VLANGroup.objects.first()
        self.assertEqual(vlangroup.total_vlan_ids, 100)

    def test_total_vlan_ids_with_inclusive_ranges(self):
        test_cases = (
            (
                NumericRange(100, 199, bounds='[]'),
                100,
                NumericRange(100, 200, bounds='[)'),
            ),
            (
                NumericRange(100, 100, bounds='[]'),
                1,
                NumericRange(100, 101, bounds='[)'),
            ),
            (
                NumericRange(99, 199, bounds='(]'),
                100,
                NumericRange(100, 200, bounds='[)'),
            ),
        )

        for i, (vid_range, total_vlan_ids, normalized_range) in enumerate(test_cases, start=1):
            vlangroup = VLANGroup(
                name=f'VLAN Group Inclusive {i}',
                slug=f'vlan-group-inclusive-{i}',
                vid_ranges=[vid_range],
            )

            vlangroup.full_clean()
            vlangroup.save()
            self.assertEqual(vlangroup.vid_ranges, [normalized_range])
            self.assertEqual(vlangroup.total_vlan_ids, total_vlan_ids)

    def test_total_vlan_ids_with_inclusive_ranges_without_full_clean(self):
        vlangroup = VLANGroup.objects.create(
            name='VLAN Group Inclusive Save',
            slug='vlan-group-inclusive-save',
            vid_ranges=[NumericRange(100, 100, bounds='[]')],
        )

        self.assertEqual(vlangroup.vid_ranges, [NumericRange(100, 101, bounds='[)')])
        self.assertEqual(vlangroup.total_vlan_ids, 1)

    def test_total_vlan_ids_with_update_fields(self):
        vlangroup = VLANGroup.objects.create(
            name='VLAN Group Update Fields',
            slug='vlan-group-update-fields',
            vid_ranges=[NumericRange(100, 200, bounds='[)')],
        )

        vlangroup.vid_ranges = [NumericRange(100, 100, bounds='[]')]
        vlangroup.save(update_fields=['vid_ranges'])
        vlangroup.refresh_from_db()

        self.assertEqual(vlangroup.vid_ranges, [NumericRange(100, 101, bounds='[)')])
        self.assertEqual(vlangroup.total_vlan_ids, 1)

    def test_annotate_utilization_with_zero_total_vlan_ids(self):
        vlangroup = VLANGroup.objects.create(
            name='VLAN Group Zero Total',
            slug='vlan-group-zero-total',
            vid_ranges=[NumericRange(100, 101)],
        )
        VLANGroup.objects.filter(pk=vlangroup.pk).update(total_vlan_ids=0)

        vlangroup = VLANGroup.objects.annotate_utilization().get(pk=vlangroup.pk)
        self.assertIsNone(vlangroup.utilization)


class VLANTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        VLAN.objects.bulk_create((
            VLAN(name='VLAN 1', vid=1, qinq_role=VLANQinQRoleChoices.ROLE_SERVICE),
        ))

    def test_qinq_role(self):
        svlan = VLAN.objects.filter(qinq_role=VLANQinQRoleChoices.ROLE_SERVICE).first()

        vlan = VLAN(
            name='VLAN X',
            vid=999,
            qinq_role=VLANQinQRoleChoices.ROLE_SERVICE,
            qinq_svlan=svlan
        )
        with self.assertRaises(ValidationError):
            vlan.full_clean()

    def test_vlan_group_site_validation(self):
        sitegroup = SiteGroup.objects.create(
            name='Site Group 1',
            slug='site-group-1',
        )
        sites = Site.objects.bulk_create((
            Site(
                name='Site 1',
                slug='site-1',
            ),
            Site(
                name='Site 2',
                slug='site-2',
            ),
        ))
        sitegroup.sites.add(sites[0])
        vlangroups = VLANGroup.objects.bulk_create((
            VLANGroup(
                name='VLAN Group 1',
                slug='vlan-group-1',
                scope=sitegroup,
                scope_type=ContentType.objects.get_for_model(SiteGroup),
            ),
            VLANGroup(
                name='VLAN Group 2',
                slug='vlan-group-2',
                scope=sites[0],
                scope_type=ContentType.objects.get_for_model(Site),
            ),
            VLANGroup(
                name='VLAN Group 2',
                slug='vlan-group-2',
                scope=sites[1],
                scope_type=ContentType.objects.get_for_model(Site),
            ),
        ))
        vlan = VLAN(
            name='VLAN 1',
            vid=1,
            group=vlangroups[0],
            site=sites[0],
        )

        # VLAN Group 1 and 2 should be valid
        vlan.full_clean()
        vlan.group = vlangroups[1]
        vlan.full_clean()
        vlan.group = vlangroups[2]
        with self.assertRaises(ValidationError):
            vlan.full_clean()

    def test_vlan_group_vid_validation_with_null_vid(self):
        """A missing VID on a grouped VLAN raises a ValidationError, not a TypeError."""
        group = VLANGroup.objects.create(name='VLAN Group 1', slug='vlan-group-1')
        vlan = VLAN(name='VLAN X', vid=None, group=group)
        with self.assertRaises(ValidationError):
            vlan.full_clean()


class PrefixGetChildIPsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.prefix = Prefix.objects.create(prefix='10.0.0.0/24')
        IPAddress.objects.bulk_create((
            IPAddress(address='10.0.0.0/24'),    # Network address (inside containment)
            IPAddress(address='10.0.0.1/24'),
            IPAddress(address='10.0.0.255/24'),  # Broadcast address (inside containment)
            IPAddress(address='10.0.1.1/24'),    # Outside the prefix
        ))

    def test_get_child_ips_matches_net_host_contained(self):
        """get_child_ips returns the same IPs as the net_host_contained containment lookup."""
        expected = set(
            IPAddress.objects.filter(
                address__net_host_contained=str(self.prefix.prefix), vrf=None
            ).values_list('pk', flat=True)
        )
        actual = set(self.prefix.get_child_ips().values_list('pk', flat=True))
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), 3)

    def test_get_child_ips_sql_avoids_containment_recheck(self):
        """get_child_ips filters on an inet host range, not the <<= containment operator."""
        sql = str(self.prefix.get_child_ips().query)
        self.assertNotIn('<<=', sql)

    def test_get_child_ips_container_in_global_table_spans_vrfs(self):
        """A container prefix in the global table returns child IPs from any VRF."""
        vrf = VRF.objects.create(name='VRF 1')
        container = Prefix.objects.create(
            prefix='10.1.0.0/24', status=PrefixStatusChoices.STATUS_CONTAINER,
        )
        in_vrf = IPAddress.objects.create(address='10.1.0.5/24', vrf=vrf)
        in_global = IPAddress.objects.create(address='10.1.0.6/24')
        child_pks = set(container.get_child_ips().values_list('pk', flat=True))
        self.assertEqual(child_pks, {in_vrf.pk, in_global.pk})


class ServiceTemplateTestCase(TestCase):

    def test_servicetemplate_lowest_port(self):
        """
        Test lowest port setting for servicetemplate
        """
        template = ServiceTemplate(
            name='Template 1',
            protocol=ServiceProtocolChoices.PROTOCOL_TCP,
            ports=[80, 443, 22, 8080],  # small test list
        )
        template.full_clean()
        template.save()
        self.assertEqual(template._ports_lowest, 22)

    def test_servicetemplate_single_port(self):
        """
        Test with a single port
        """
        template = ServiceTemplate(
            name='Template 2',
            protocol=ServiceProtocolChoices.PROTOCOL_UDP,
            ports=[53],
        )
        template.full_clean()
        template.save()
        self.assertEqual(template._ports_lowest, 53)

    def test_servicetemplate_empty_ports(self):
        """
        Test with empty ports list
        """
        template = ServiceTemplate(
            name='Template 3',
            protocol=ServiceProtocolChoices.PROTOCOL_TCP,
            ports=[],
        )
        self.assertRaises(ValidationError, template.full_clean)

    def test_servicetemplate_port_assignments(self):
        """
        Test a template defined directly via port_assignments, mixing protocols on the same port.
        """
        template = ServiceTemplate(
            name='Template 4',
            port_assignments=[
                {'protocol': ServiceProtocolChoices.PROTOCOL_TCP, 'port': 53},
                {'protocol': ServiceProtocolChoices.PROTOCOL_UDP, 'port': 53},
            ],
        )
        template.full_clean()
        template.save()
        self.assertEqual(template._ports_lowest, 53)
        # Deprecated accessors: protocol is None when mixed, ports is the flattened set
        self.assertIsNone(template.protocol)
        self.assertEqual(template.ports, [53])

    def test_servicetemplate_uniform_protocol_accessor(self):
        """
        The deprecated protocol accessor returns the single protocol when assignments are uniform.
        """
        template = ServiceTemplate(
            name='Template 5',
            port_assignments=[
                {'protocol': ServiceProtocolChoices.PROTOCOL_TCP, 'port': 80},
                {'protocol': ServiceProtocolChoices.PROTOCOL_TCP, 'port': 443},
            ],
        )
        template.full_clean()
        self.assertEqual(template.protocol, ServiceProtocolChoices.PROTOCOL_TCP)
        self.assertEqual(template.ports, [80, 443])

    def test_servicetemplate_invalid_port_assignment(self):
        """
        Invalid protocol/port values are rejected.
        """
        template = ServiceTemplate(
            name='Template 6',
            port_assignments=[{'protocol': 'bogus', 'port': 80}],
        )
        self.assertRaises(ValidationError, template.full_clean)

        template = ServiceTemplate(
            name='Template 7',
            port_assignments=[{'protocol': ServiceProtocolChoices.PROTOCOL_TCP, 'port': 99999}],
        )
        self.assertRaises(ValidationError, template.full_clean)


class ServiceTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(
            name='Site 1',
            slug='site-1',
        )
        VirtualMachine.objects.create(
            name='virtual machine 1',
            site=site,
        )

    def test_large_service(self):
        """
        Test creation of service with large number of ports.
        Related to issue #22273
        """
        service = Service(
            name='Service 1',
            protocol=ServiceProtocolChoices.PROTOCOL_TCP,
            ports=list(range(SERVICE_PORT_MIN, SERVICE_PORT_MAX)),
            parent=VirtualMachine.objects.first(),
        )
        service.full_clean()
        # Testing .save() is the important part, to check for database problems
        service.save()
        self.assertEqual(service._ports_lowest, SERVICE_PORT_MIN)
