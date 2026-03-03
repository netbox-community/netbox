from django.test import RequestFactory, TestCase
from netaddr import IPNetwork

from ipam.models import IPAddress, IPRange, Prefix
from ipam.tables import AnnotatedIPAddressTable
from ipam.utils import annotate_ip_space


class AnnotatedIPAddressTableTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.prefix = Prefix.objects.create(
            prefix=IPNetwork('10.1.1.0/24'),
            status='active'
        )

        cls.ip_address = IPAddress.objects.create(
            address='10.1.1.1/24',
            status='active'
        )

        cls.ip_range = IPRange.objects.create(
            start_address=IPNetwork('10.1.1.2/24'),
            end_address=IPNetwork('10.1.1.10/24'),
            status='active'
        )

    def test_ipaddress_has_checkbox_iprange_does_not(self):
        data = annotate_ip_space(self.prefix)
        table = AnnotatedIPAddressTable(data, orderable=False)
        table.columns.show('pk')

        request = RequestFactory().get('/')
        html = table.as_html(request)

        ipaddress_checkbox_count = html.count(f'name="pk" value="{self.ip_address.pk}"')
        self.assertEqual(ipaddress_checkbox_count, 1)

        iprange_checkbox_count = html.count(f'name="pk" value="{self.ip_range.pk}"')
        self.assertEqual(iprange_checkbox_count, 0)

    def test_annotate_ip_space_ipv4_non_pool_excludes_network_and_broadcast(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.0/29'),  # 8 addresses total
            status='active',
            is_pool=False,
        )

        data = annotate_ip_space(prefix)

        self.assertEqual(len(data), 1)
        available = data[0]

        # /29 non-pool: exclude .0 (network) and .7 (broadcast)
        self.assertEqual(available.first_ip, '192.0.2.1/29')
        self.assertEqual(available.size, 6)

    def test_annotate_ip_space_ipv4_pool_includes_network_and_broadcast(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.8/29'),  # 8 addresses total
            status='active',
            is_pool=True,
        )

        data = annotate_ip_space(prefix)

        self.assertEqual(len(data), 1)
        available = data[0]

        # Pool: all addresses are usable, including network/broadcast
        self.assertEqual(available.first_ip, '192.0.2.8/29')
        self.assertEqual(available.size, 8)

    def test_annotate_ip_space_ipv4_31_includes_all_ips(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.16/31'),  # 2 addresses total
            status='active',
            is_pool=False,
        )

        data = annotate_ip_space(prefix)

        self.assertEqual(len(data), 1)
        available = data[0]

        # /31: fully usable
        self.assertEqual(available.first_ip, '192.0.2.16/31')
        self.assertEqual(available.size, 2)

    def test_annotate_ip_space_ipv4_32_includes_single_ip(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('192.0.2.100/32'),  # 1 address total
            status='active',
            is_pool=False,
        )

        data = annotate_ip_space(prefix)

        self.assertEqual(len(data), 1)
        available = data[0]

        # /32: single usable address
        self.assertEqual(available.first_ip, '192.0.2.100/32')
        self.assertEqual(available.size, 1)

    def test_annotate_ip_space_ipv6_non_pool_excludes_anycast_first_ip(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('2001:db8::/126'),  # 4 addresses total
            status='active',
            is_pool=False,
        )

        data = annotate_ip_space(prefix)

        # No child records -> expect one AvailableIPSpace entry
        self.assertEqual(len(data), 1)
        available = data[0]

        # For IPv6 non-pool prefixes (except /127-/128), the first address is reserved (subnet-router anycast)
        self.assertEqual(available.first_ip, '2001:db8::1/126')
        self.assertEqual(available.size, 3)  # 4 total - 1 reserved anycast

    def test_annotate_ip_space_ipv6_127_includes_all_ips(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('2001:db8::/127'),  # 2 addresses total
            status='active',
            is_pool=False,
        )

        data = annotate_ip_space(prefix)

        self.assertEqual(len(data), 1)
        available = data[0]

        # /127 is fully usable (no anycast exclusion)
        self.assertEqual(available.first_ip, '2001:db8::/127')
        self.assertEqual(available.size, 2)

    def test_annotate_ip_space_ipv6_128_includes_single_ip(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('2001:db8::1/128'),  # 1 address total
            status='active',
            is_pool=False,
        )

        data = annotate_ip_space(prefix)

        self.assertEqual(len(data), 1)
        available = data[0]

        # /128 is fully usable (single host address)
        self.assertEqual(available.first_ip, '2001:db8::1/128')
        self.assertEqual(available.size, 1)

    def test_annotate_ip_space_ipv6_pool_includes_anycast_first_ip(self):
        prefix = Prefix.objects.create(
            prefix=IPNetwork('2001:db8:1::/126'),  # 4 addresses total
            status='active',
            is_pool=True,
        )

        data = annotate_ip_space(prefix)

        self.assertEqual(len(data), 1)
        available = data[0]

        # Pools are fully usable
        self.assertEqual(available.first_ip, '2001:db8:1::/126')
        self.assertEqual(available.size, 4)
