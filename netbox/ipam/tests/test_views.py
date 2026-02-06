from django.urls import reverse

from netbox.tests import NetBoxTestCase
from ipam.models import Prefix, IPRange, IPAddress, VRF, Role
from tenancy.models import Tenant

class PrefixIPAddressesViewTest(NetBoxTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.vrf = VRF.objects.create(name='Test VRF')
        cls.tenant = Tenant.objects.create(name='Test Tenant')
        cls.role = Role.objects.create(name='Test Role', slug='test-role')
        cls.prefix = Prefix.objects.create(prefix='192.168.0.0/24', vrf=cls.vrf, tenant=cls.tenant, role=cls.role)
        cls.ip_range = IPRange.objects.create(start_address='192.168.0.10', end_address='192.168.0.20', vrf=cls.vrf, tenant=cls.tenant, role=cls.role)
        cls.ip_address = IPAddress.objects.create(address='192.168.0.5', vrf=cls.vrf, tenant=cls.tenant)

    def test_ip_range_buttons_present(self):
        """
        Test that the edit, delete, and changelog buttons are present for IP ranges.
        """
        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': self.prefix.pk})
        response = self.client.get(url)

        # Check for IP range buttons
        self.assertIn(b'ipam:iprange_edit', response.content)
        self.assertIn(b'ipam:iprange_delete', response.content)
        self.assertIn(b'ipam:iprange_changelog', response.content)

        # Check for IP address buttons
        self.assertIn(b'ipam:ipaddress_edit', response.content)
        self.assertIn(b'ipam:ipaddress_delete', response.content)
        self.assertIn(b'ipam:ipaddress_changelog', response.content)