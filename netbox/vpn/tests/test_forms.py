from django.test import TestCase

from dcim.models import Interface
from ipam.models import VRF, IPAddress
from utilities.testing import create_test_device
from vpn.choices import L2VPNTypeChoices
from vpn.forms import L2VPNTerminationForm, L2VPNTerminationImportForm
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


class L2VPNTerminationImportFormTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        L2VPN.objects.create(name='L2VPN 1', slug='l2vpn-1', type=L2VPNTypeChoices.TYPE_VPLS)

        # The same address exists globally, in a VRF, and on a device's interface in another VRF
        cls.vrfs = (
            VRF.objects.create(name='VRF 1'),
            VRF.objects.create(name='VRF 2'),
        )
        cls.device = create_test_device('Device 1')
        interface = Interface.objects.create(device=cls.device, name='Interface 1', type='1000baset')
        cls.ip_addresses = (
            IPAddress.objects.create(address='192.0.2.1/32'),
            IPAddress.objects.create(address='192.0.2.1/32', vrf=cls.vrfs[0]),
            IPAddress.objects.create(address='192.0.2.1/32', vrf=cls.vrfs[1], assigned_object=interface),
        )

    def test_missing_assigned_object(self):
        form = L2VPNTerminationImportForm(data={'l2vpn': 'L2VPN 1'}, instance=L2VPNTermination())
        self.assertFalse(form.is_valid())
        self.assertIn('must specify an interface, a VLAN, or an IP address', str(form.errors))

    def get_assigned_object(self, data):
        form = L2VPNTerminationImportForm(data={'l2vpn': 'L2VPN 1', **data}, instance=L2VPNTermination())
        self.assertTrue(form.is_valid(), form.errors)
        return form.instance.assigned_object

    def test_ipaddress_ambiguous(self):
        form = L2VPNTerminationImportForm(
            data={'l2vpn': 'L2VPN 1', 'ipaddress': '192.0.2.1/32'}, instance=L2VPNTermination()
        )
        self.assertFalse(form.is_valid())
        self.assertIn('ipaddress', form.errors)

    def test_ipaddress_vrf(self):
        assigned_object = self.get_assigned_object({'ipaddress': '192.0.2.1/32', 'ipaddress_vrf': 'VRF 1'})
        self.assertEqual(assigned_object, self.ip_addresses[1])

    def test_ipaddress_device(self):
        assigned_object = self.get_assigned_object({'ipaddress': '192.0.2.1/32', 'device': 'Device 1'})
        self.assertEqual(assigned_object, self.ip_addresses[2])

    def test_ipaddress_not_on_device(self):
        form = L2VPNTerminationImportForm(
            data={'l2vpn': 'L2VPN 1', 'ipaddress': '192.0.2.1/32', 'ipaddress_vrf': 'VRF 1', 'device': 'Device 1'},
            instance=L2VPNTermination()
        )
        self.assertFalse(form.is_valid())
        self.assertIn('ipaddress', form.errors)
