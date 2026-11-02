from django.test import TestCase

from ipam.models import IPAddress
from vpn.choices import L2VPNTypeChoices
from vpn.forms import L2VPNTerminationForm
from vpn.models import L2VPN, L2VPNTermination


class L2VPNTerminationFormTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.ip_address = IPAddress.objects.create(address='192.0.2.1/32')
        cls.l2vpns = (
            L2VPN.objects.create(name='L2VPN 1', slug='l2vpn-1', type=L2VPNTypeChoices.TYPE_VPLS),
            L2VPN.objects.create(name='L2VPN 2', slug='l2vpn-2', type=L2VPNTypeChoices.TYPE_VPLS),
        )
        L2VPNTermination.objects.create(l2vpn=cls.l2vpns[0], assigned_object=cls.ip_address)

    def test_ipaddress_terminates_another_l2vpn(self):
        form = L2VPNTerminationForm(data={'l2vpn': self.l2vpns[1].pk, 'ipaddress': self.ip_address.pk})
        self.assertTrue(form.is_valid(), form.errors)

    def test_duplicate_ipaddress_termination(self):
        form = L2VPNTerminationForm(data={'l2vpn': self.l2vpns[0].pk, 'ipaddress': self.ip_address.pk})
        self.assertFalse(form.is_valid())
        self.assertIn('already terminates', str(form.errors))
