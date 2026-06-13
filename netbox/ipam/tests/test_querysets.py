import netaddr
from django.test import TestCase
from netaddr import IPNetwork

from ipam.models import IPAddress, IPRange


class IPAddressQuerySetTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        IPAddress.objects.bulk_create((
            IPAddress(address=IPNetwork('192.0.2.1/24')),
            IPAddress(address=IPNetwork('192.0.2.1/32')),
            IPAddress(address=IPNetwork('192.0.2.2/24')),
        ))

    def test_count_distinct_hosts(self):
        """
        Tests that duplicate hosts with different masks are counted once.
        """
        self.assertEqual(IPAddress.objects.count_distinct_hosts(), 2)

    def test_count_distinct_hosts_empty(self):
        """
        Tests that an empty queryset counts zero hosts.
        """
        self.assertEqual(IPAddress.objects.none().count_distinct_hosts(), 0)

    def test_count_distinct_hosts_exclude_intervals(self):
        """
        Tests that hosts covered by an excluded interval are not counted.
        """
        interval = (netaddr.IPAddress('192.0.2.1'), netaddr.IPAddress('192.0.2.1'))
        self.assertEqual(IPAddress.objects.count_distinct_hosts(exclude_intervals=[interval]), 1)

    def test_count_distinct_hosts_pair(self):
        """
        Tests that the bounded and total distinct host counts are computed correctly.
        """
        counts = IPAddress.objects.count_distinct_hosts_pair(
            bounds=(netaddr.IPAddress('192.0.2.2'), netaddr.IPAddress('192.0.2.10')),
            bounded_exclude=[(netaddr.IPAddress('192.0.2.2'), netaddr.IPAddress('192.0.2.2'))],
            total_exclude=[(netaddr.IPAddress('192.0.2.1'), netaddr.IPAddress('192.0.2.1'))],
        )
        self.assertEqual(counts, {'bounded': 0, 'total': 1})

    def test_count_distinct_hosts_pair_no_excludes(self):
        """
        Tests that both counts dedupe hosts and respect the bounds without excludes.
        """
        counts = IPAddress.objects.count_distinct_hosts_pair(
            bounds=(netaddr.IPAddress('192.0.2.2'), netaddr.IPAddress('192.0.2.10')),
        )
        self.assertEqual(counts, {'bounded': 1, 'total': 2})

    def test_first_available_host(self):
        """
        Tests that occupied hosts and excluded intervals are skipped, including hosts behind the sweep.
        """
        interval = (netaddr.IPAddress('192.0.2.1'), netaddr.IPAddress('192.0.2.5'))
        self.assertEqual(
            IPAddress.objects.first_available_host(
                netaddr.IPAddress('192.0.2.1'), netaddr.IPAddress('192.0.2.10'), exclude_intervals=[interval]
            ),
            netaddr.IPAddress('192.0.2.6'),
        )

    def test_first_available_host_inverted_bounds(self):
        """
        Tests that an inverted bounds pair yields None.
        """
        self.assertIsNone(
            IPAddress.objects.first_available_host(netaddr.IPAddress('192.0.2.10'), netaddr.IPAddress('192.0.2.5'))
        )

    def test_available_intervals(self):
        """
        Tests that gaps around occupied hosts and excluded intervals are yielded in order.
        """
        interval = (netaddr.IPAddress('192.0.2.5'), netaddr.IPAddress('192.0.2.6'))
        self.assertEqual(
            list(IPAddress.objects.available_intervals(
                netaddr.IPAddress('192.0.2.1'), netaddr.IPAddress('192.0.2.10'), exclude_intervals=[interval]
            )),
            [
                (netaddr.IPAddress('192.0.2.3'), netaddr.IPAddress('192.0.2.4')),
                (netaddr.IPAddress('192.0.2.7'), netaddr.IPAddress('192.0.2.10')),
            ],
        )

    def test_available_intervals_leading_gap(self):
        """
        Tests that the gap before the first occupied host is yielded.
        """
        self.assertEqual(
            list(IPAddress.objects.available_intervals(
                netaddr.IPAddress('192.0.2.0'), netaddr.IPAddress('192.0.2.2')
            )),
            [(netaddr.IPAddress('192.0.2.0'), netaddr.IPAddress('192.0.2.0'))],
        )

    def test_available_intervals_empty_queryset(self):
        """
        Tests that an empty queryset yields the full span.
        """
        self.assertEqual(
            list(IPAddress.objects.none().available_intervals(
                netaddr.IPAddress('192.0.2.1'), netaddr.IPAddress('192.0.2.3')
            )),
            [(netaddr.IPAddress('192.0.2.1'), netaddr.IPAddress('192.0.2.3'))],
        )

    def test_available_intervals_inverted_bounds(self):
        """
        Tests that an inverted bounds pair yields nothing.
        """
        self.assertEqual(
            list(IPAddress.objects.available_intervals(
                netaddr.IPAddress('192.0.2.10'), netaddr.IPAddress('192.0.2.5')
            )),
            [],
        )

    def test_available_intervals_fully_excluded(self):
        """
        Tests that a span covered by an excluded interval yields nothing.
        """
        interval = (netaddr.IPAddress('192.0.2.0'), netaddr.IPAddress('192.0.2.20'))
        self.assertEqual(
            list(IPAddress.objects.available_intervals(
                netaddr.IPAddress('192.0.2.1'), netaddr.IPAddress('192.0.2.10'), exclude_intervals=[interval]
            )),
            [],
        )

    def test_available_intervals_mixed_family_exclude(self):
        """
        Tests that an exclude interval spanning address families is ignored.
        """
        interval = (netaddr.IPAddress('192.0.2.5'), netaddr.IPAddress('2001:db8::5'))
        self.assertEqual(
            list(IPAddress.objects.available_intervals(
                netaddr.IPAddress('192.0.2.1'), netaddr.IPAddress('192.0.2.10'), exclude_intervals=[interval]
            )),
            [(netaddr.IPAddress('192.0.2.3'), netaddr.IPAddress('192.0.2.10'))],
        )

    def test_available_intervals_invalid_batch_size(self):
        """
        Tests that a non-positive batch size raises ValueError.
        """
        intervals = IPAddress.objects.available_intervals(
            netaddr.IPAddress('192.0.2.1'), netaddr.IPAddress('192.0.2.10'), batch_size=0
        )
        with self.assertRaises(ValueError):
            next(intervals)

    def test_available_intervals_first_interval_single_query(self):
        """
        Tests that consuming only the first interval issues a single batch query.
        """
        IPAddress.objects.bulk_create((
            IPAddress(address=IPNetwork('192.0.2.12/24')),
            IPAddress(address=IPNetwork('192.0.2.14/24')),
            IPAddress(address=IPNetwork('192.0.2.16/24')),
        ))

        intervals = IPAddress.objects.available_intervals(
            netaddr.IPAddress('192.0.2.10'), netaddr.IPAddress('192.0.2.20'), batch_size=1
        )

        with self.assertNumQueries(1):
            self.assertEqual(
                next(intervals),
                (netaddr.IPAddress('192.0.2.10'), netaddr.IPAddress('192.0.2.11')),
            )

    def test_available_intervals_unsorted_exclude_intervals(self):
        """
        Tests that unsorted, overlapping exclude intervals are normalized internally.
        """
        intervals = list(IPAddress.objects.none().available_intervals(
            netaddr.IPAddress('192.0.2.1'),
            netaddr.IPAddress('192.0.2.40'),
            exclude_intervals=[
                (netaddr.IPAddress('192.0.2.20'), netaddr.IPAddress('192.0.2.30')),
                (netaddr.IPAddress('192.0.2.1'), netaddr.IPAddress('192.0.2.10')),
                (netaddr.IPAddress('192.0.2.25'), netaddr.IPAddress('192.0.2.30')),
            ],
        ))

        self.assertEqual(intervals, [
            (netaddr.IPAddress('192.0.2.11'), netaddr.IPAddress('192.0.2.19')),
            (netaddr.IPAddress('192.0.2.31'), netaddr.IPAddress('192.0.2.40')),
        ])

    def test_available_intervals_batching(self):
        """
        Tests that gaps spanning multiple fetch batches are yielded completely and in order.
        """
        IPAddress.objects.bulk_create(
            IPAddress(address=IPNetwork(f'192.0.3.{i}/24')) for i in range(2, 82, 2)
        )
        expected = [
            (netaddr.IPAddress(f'192.0.3.{i}'), netaddr.IPAddress(f'192.0.3.{i}'))
            for i in range(1, 83, 2)
        ]
        self.assertEqual(
            list(IPAddress.objects.available_intervals(
                netaddr.IPAddress('192.0.3.1'), netaddr.IPAddress('192.0.3.81'), batch_size=8
            )),
            expected,
        )

    def test_iter_distinct_hosts_stops_at_upper_bound(self):
        """
        Tests that batch resumption stops once the last fetched host reaches the upper bound.
        """
        IPAddress.objects.bulk_create(
            IPAddress(address=IPNetwork(f'192.0.4.{i}/24')) for i in (2, 4)
        )
        self.assertEqual(
            list(IPAddress.objects.all()._iter_distinct_hosts(
                netaddr.IPAddress('192.0.4.2'), netaddr.IPAddress('192.0.4.4'), batch_size=1
            )),
            [netaddr.IPAddress('192.0.4.2'), netaddr.IPAddress('192.0.4.4')],
        )

    def test_available_intervals_batch_size_one(self):
        """
        Tests that fetching one host per batch still terminates and yields every gap.
        """
        IPAddress.objects.bulk_create(
            IPAddress(address=IPNetwork(f'192.0.3.{i}/24')) for i in (2, 3, 5)
        )
        self.assertEqual(
            list(IPAddress.objects.available_intervals(
                netaddr.IPAddress('192.0.3.1'), netaddr.IPAddress('192.0.3.6'), batch_size=1
            )),
            [
                (netaddr.IPAddress('192.0.3.1'), netaddr.IPAddress('192.0.3.1')),
                (netaddr.IPAddress('192.0.3.4'), netaddr.IPAddress('192.0.3.4')),
                (netaddr.IPAddress('192.0.3.6'), netaddr.IPAddress('192.0.3.6')),
            ],
        )


class IPRangeQuerySetTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        IPRange.objects.bulk_create((
            IPRange(start_address=IPNetwork('192.0.2.10/24'), end_address=IPNetwork('192.0.2.19/24'), size=10),
            IPRange(start_address=IPNetwork('192.0.2.15/24'), end_address=IPNetwork('192.0.2.24/24'), size=10),
            IPRange(start_address=IPNetwork('192.0.2.40/24'), end_address=IPNetwork('192.0.2.49/24'), size=10),
        ))

    def test_get_intervals_merges_overlaps(self):
        """
        Tests that overlapping ranges merge and disjoint ranges stay separate.
        """
        self.assertEqual(
            IPRange.objects.get_intervals(),
            [
                (netaddr.IPAddress('192.0.2.10'), netaddr.IPAddress('192.0.2.24')),
                (netaddr.IPAddress('192.0.2.40'), netaddr.IPAddress('192.0.2.49')),
            ],
        )

    def test_get_intervals_clips_to_bounds(self):
        """
        Tests that ranges are clipped to the bounds and out-of-bounds ranges are dropped.
        """
        self.assertEqual(
            IPRange.objects.get_intervals(netaddr.IPAddress('192.0.2.20'), netaddr.IPAddress('192.0.2.30')),
            [(netaddr.IPAddress('192.0.2.20'), netaddr.IPAddress('192.0.2.24'))],
        )

    def test_get_intervals_drops_ranges_below_bounds(self):
        """
        Tests that ranges entirely below the lower bound are dropped.
        """
        self.assertEqual(
            IPRange.objects.get_intervals(netaddr.IPAddress('192.0.2.30'), netaddr.IPAddress('192.0.2.60')),
            [(netaddr.IPAddress('192.0.2.40'), netaddr.IPAddress('192.0.2.49'))],
        )

    def test_get_intervals_drops_ranges_above_bounds(self):
        """
        Tests that ranges entirely above the upper bound are dropped.
        """
        self.assertEqual(
            IPRange.objects.get_intervals(netaddr.IPAddress('192.0.2.0'), netaddr.IPAddress('192.0.2.30')),
            [(netaddr.IPAddress('192.0.2.10'), netaddr.IPAddress('192.0.2.24'))],
        )

    def test_get_intervals_clips_to_upper_bound(self):
        """
        Tests that a range straddling the upper bound is clipped to it.
        """
        self.assertEqual(
            IPRange.objects.get_intervals(netaddr.IPAddress('192.0.2.0'), netaddr.IPAddress('192.0.2.15')),
            [(netaddr.IPAddress('192.0.2.10'), netaddr.IPAddress('192.0.2.15'))],
        )

    def test_get_intervals_mixed_families(self):
        """
        Tests that int-adjacent intervals of different address families are not merged.
        """
        IPRange.objects.bulk_create((
            IPRange(
                start_address=IPNetwork('255.255.255.254/32'),
                end_address=IPNetwork('255.255.255.255/32'),
                size=2,
            ),
            IPRange(start_address=IPNetwork('::1/128'), end_address=IPNetwork('::2/128'), size=2),
        ))

        self.assertEqual(
            IPRange.objects.get_intervals(),
            [
                (netaddr.IPAddress('192.0.2.10'), netaddr.IPAddress('192.0.2.24')),
                (netaddr.IPAddress('192.0.2.40'), netaddr.IPAddress('192.0.2.49')),
                (netaddr.IPAddress('255.255.255.254'), netaddr.IPAddress('255.255.255.255')),
                (netaddr.IPAddress('::1'), netaddr.IPAddress('::2')),
            ],
        )

    def test_get_intervals_ipv6(self):
        """
        Tests that IPv6 ranges merge and clip by host address.
        """
        IPRange.objects.create(
            start_address=IPNetwork('2001:db8::10/64'),
            end_address=IPNetwork('2001:db8::1f/64'),
        )
        IPRange.objects.create(
            start_address=IPNetwork('2001:db8::18/64'),
            end_address=IPNetwork('2001:db8::2f/64'),
        )

        self.assertEqual(
            IPRange.objects.get_intervals(netaddr.IPAddress('2001:db8::'), netaddr.IPAddress('2001:db8::ffff')),
            [(netaddr.IPAddress('2001:db8::10'), netaddr.IPAddress('2001:db8::2f'))],
        )
