import netaddr
from django.db.backends.postgresql.psycopg_any import NumericRange
from django.test import TestCase
from netaddr import IPNetwork

from ipam.models import IPAddress, VLANGroup


class VLANGroupRangeContainsLookupTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Two ranges: [1,11) and [20,31)
        cls.g1 = VLANGroup.objects.create(
            name='VlanGroup-A',
            slug='VlanGroup-A',
            vid_ranges=[NumericRange(1, 11), NumericRange(20, 31)],
        )
        # One range: [100,201)
        cls.g2 = VLANGroup.objects.create(
            name='VlanGroup-B',
            slug='VlanGroup-B',
            vid_ranges=[NumericRange(100, 201)],
        )
        cls.g_empty = VLANGroup.objects.create(
            name='VlanGroup-empty',
            slug='VlanGroup-empty',
            vid_ranges=[],
        )

    def test_contains_value_in_first_range(self):
        """
        Tests whether a specific value is contained within the first range in a queried
        set of VLANGroup objects.
        """
        names = list(
            VLANGroup.objects.filter(vid_ranges__range_contains=10).values_list('name', flat=True).order_by('name')
        )
        self.assertEqual(names, ['VlanGroup-A'])

    def test_contains_value_in_second_range(self):
        """
        Tests if a value exists in the second range of VLANGroup objects and
        validates the result against the expected list of names.
        """
        names = list(
            VLANGroup.objects.filter(vid_ranges__range_contains=25).values_list('name', flat=True).order_by('name')
        )
        self.assertEqual(names, ['VlanGroup-A'])

    def test_upper_bound_is_exclusive(self):
        """
        Tests if the upper bound of the range is exclusive in the filter method.
        """
        # 11 is NOT in [1,11)
        self.assertFalse(VLANGroup.objects.filter(vid_ranges__range_contains=11).exists())

    def test_no_match_far_outside(self):
        """
        Tests that no VLANGroup contains a VID within a specified range far outside
        common VID bounds and returns `False`.
        """
        self.assertFalse(VLANGroup.objects.filter(vid_ranges__range_contains=4095).exists())

    def test_empty_array_never_matches(self):
        """
        Tests the behavior of VLANGroup objects when an empty array is used to match a
        specific condition.
        """
        self.assertFalse(VLANGroup.objects.filter(pk=self.g_empty.pk, vid_ranges__range_contains=1).exists())


class IPAddressHostBetweenLookupTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        IPAddress.objects.bulk_create((
            IPAddress(address=IPNetwork('192.0.2.0/24')),
            IPAddress(address=IPNetwork('192.0.2.1/24')),
            IPAddress(address=IPNetwork('192.0.2.5/32')),
            IPAddress(address=IPNetwork('192.0.2.10/25')),
            IPAddress(address=IPNetwork('192.0.2.11/24')),
            IPAddress(address=IPNetwork('2001:db8::1/64')),
            IPAddress(address=IPNetwork('2001:db8::5/128')),
            IPAddress(address=IPNetwork('2001:db8::10/64')),
        ))

    def test_ipv4_boundaries_inclusive(self):
        """
        Tests that both bounds are included and hosts outside the window are excluded.
        """
        queryset = IPAddress.objects.filter(
            address__host_between=(netaddr.IPAddress('192.0.2.1'), netaddr.IPAddress('192.0.2.10'))
        )
        self.assertEqual(
            sorted(str(ip.address) for ip in queryset),
            ['192.0.2.1/24', '192.0.2.10/25', '192.0.2.5/32'],
        )

    def test_mask_insensitive(self):
        """
        Tests that hosts match regardless of their mask length.
        """
        queryset = IPAddress.objects.filter(
            address__host_between=(netaddr.IPAddress('192.0.2.5'), netaddr.IPAddress('192.0.2.5'))
        )
        self.assertEqual(queryset.count(), 1)

    def test_ipv6(self):
        """
        Tests that IPv6 hosts filter by host portion.
        """
        queryset = IPAddress.objects.filter(
            address__host_between=(netaddr.IPAddress('2001:db8::1'), netaddr.IPAddress('2001:db8::5'))
        )
        self.assertEqual(queryset.count(), 2)

    def test_bounds_mask_stripped(self):
        """
        Tests that bounds supplied with a mask compare by host portion only.
        """
        queryset = IPAddress.objects.filter(
            address__host_between=(IPNetwork('192.0.2.1/24'), IPNetwork('192.0.2.10/24'))
        )
        self.assertEqual(queryset.count(), 3)

    def test_invalid_bounds_raise(self):
        """
        Tests that a bounds value which is not a two-item pair raises ValueError.
        """
        with self.assertRaises(ValueError):
            IPAddress.objects.filter(address__host_between=(netaddr.IPAddress('192.0.2.1'),))

    def test_invalid_bound_value_raises(self):
        """
        Tests that a bound which is not a valid IP address raises ValueError.
        """
        with self.assertRaises(ValueError):
            IPAddress.objects.filter(address__host_between=('invalid', netaddr.IPAddress('192.0.2.10')))

    def test_mixed_family_bounds_raise(self):
        """
        Tests that bounds from different address families raise ValueError.
        """
        with self.assertRaises(ValueError):
            IPAddress.objects.filter(
                address__host_between=(netaddr.IPAddress('192.0.2.1'), netaddr.IPAddress('2001:db8::1'))
            )

    def test_sql_uses_cast_host_expression(self):
        """
        Tests that the compiled SQL matches the ipam_ipaddress_host index expression.
        """
        queryset = IPAddress.objects.filter(
            address__host_between=(netaddr.IPAddress('192.0.2.1'), netaddr.IPAddress('192.0.2.10'))
        )
        self.assertIn('CAST(HOST(', str(queryset.query))


class IPAddressNetLookupsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        IPAddress.objects.bulk_create((
            IPAddress(address='10.0.0.1/24'),
            IPAddress(address='10.0.0.2/24'),
            IPAddress(address='10.0.0.1/25'),  # Same host as the first, different mask
            IPAddress(address='2001:db8::1/64'),
        ))

    def test_net_host_matches_host_ignoring_mask(self):
        """net_host matches every address whose host portion equals the value."""
        qs = IPAddress.objects.filter(address__net_host='10.0.0.1')
        self.assertEqual(qs.count(), 2)

    def test_net_host_predicate_is_inet_typed(self):
        """net_host casts the host expression to inet so the inet host index applies."""
        sql = str(IPAddress.objects.filter(address__net_host='10.0.0.1').query)
        self.assertIn('CAST(HOST(', sql)
        self.assertIn('AS INET) =', sql)

    def test_net_in_without_mask(self):
        """net_in matches host values supplied without a mask."""
        qs = IPAddress.objects.filter(address__net_in=['10.0.0.1', '10.0.0.2'])
        self.assertEqual(qs.count(), 3)

    def test_net_in_with_mask(self):
        """net_in matches an exact address/mask value."""
        qs = IPAddress.objects.filter(address__net_in=['10.0.0.1/25'])
        self.assertEqual(qs.count(), 1)

    def test_net_in_normalizes_ipv6(self):
        """net_in matches an expanded IPv6 form against the canonical host value."""
        qs = IPAddress.objects.filter(
            address__net_in=['2001:0db8:0000:0000:0000:0000:0000:0001']
        )
        self.assertEqual(qs.count(), 1)

    def test_net_in_predicate_is_inet_typed(self):
        """net_in casts the host expression to inet so the inet host index applies."""
        sql = str(IPAddress.objects.filter(address__net_in=['10.0.0.1']).query)
        self.assertIn('CAST(HOST(', sql)
        self.assertIn('AS INET) IN', sql)
