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
