from django.core.exceptions import ValidationError
from django.test import TestCase

from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from ipam.models import VLAN, IPAddress
from vpn.models import *


class L2VPNTerminationTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):

        site = Site.objects.create(name='Site 1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1')
        device_type = DeviceType.objects.create(model='Device Type 1', manufacturer=manufacturer)
        role = DeviceRole.objects.create(name='Switch')
        device = Device.objects.create(
            name='Device 1',
            site=site,
            device_type=device_type,
            role=role,
            status='active'
        )

        interfaces = (
            Interface(name='Interface 1', device=device, type='1000baset'),
            Interface(name='Interface 2', device=device, type='1000baset'),
            Interface(name='Interface 3', device=device, type='1000baset'),
            Interface(name='Interface 4', device=device, type='1000baset'),
            Interface(name='Interface 5', device=device, type='1000baset'),
        )

        Interface.objects.bulk_create(interfaces)

        vlans = (
            VLAN(name='VLAN 1', vid=651),
            VLAN(name='VLAN 2', vid=652),
            VLAN(name='VLAN 3', vid=653),
            VLAN(name='VLAN 4', vid=654),
            VLAN(name='VLAN 5', vid=655),
            VLAN(name='VLAN 6', vid=656),
            VLAN(name='VLAN 7', vid=657)
        )

        VLAN.objects.bulk_create(vlans)

        l2vpns = (
            L2VPN(name='L2VPN 1', slug='l2vpn-1', type='vxlan', identifier=650001),
            L2VPN(name='L2VPN 2', slug='l2vpn-2', type='vpws', identifier=650002),
            L2VPN(name='L2VPN 3', slug='l2vpn-3', type='vpls'),  # No RD
        )
        L2VPN.objects.bulk_create(l2vpns)

        l2vpnterminations = (
            L2VPNTermination(l2vpn=l2vpns[0], assigned_object=vlans[0]),
            L2VPNTermination(l2vpn=l2vpns[0], assigned_object=vlans[1]),
            L2VPNTermination(l2vpn=l2vpns[0], assigned_object=vlans[2])
        )

        L2VPNTermination.objects.bulk_create(l2vpnterminations)

    def test_duplicate_interface_terminations(self):
        device = Device.objects.first()
        interface = Interface.objects.filter(device=device).first()
        l2vpn = L2VPN.objects.first()

        L2VPNTermination.objects.create(l2vpn=l2vpn, assigned_object=interface)
        duplicate = L2VPNTermination(l2vpn=l2vpn, assigned_object=interface)

        self.assertRaises(ValidationError, duplicate.clean)

    def test_duplicate_vlan_terminations(self):
        vlan = Interface.objects.first()
        l2vpn = L2VPN.objects.first()

        L2VPNTermination.objects.create(l2vpn=l2vpn, assigned_object=vlan)
        duplicate = L2VPNTermination(l2vpn=l2vpn, assigned_object=vlan)
        self.assertRaises(ValidationError, duplicate.clean)

    def test_ipaddress_terminates_multiple_l2vpns(self):
        ip_address = IPAddress.objects.create(address='192.0.2.1/32')
        l2vpns = L2VPN.objects.all()[:2]

        L2VPNTermination.objects.create(l2vpn=l2vpns[0], assigned_object=ip_address)
        termination = L2VPNTermination(l2vpn=l2vpns[1], assigned_object=ip_address)
        termination.full_clean()
        termination.save()

        self.assertEqual(ip_address.l2vpn_terminations.count(), 2)

    def test_duplicate_ipaddress_terminations(self):
        ip_address = IPAddress.objects.create(address='192.0.2.1/32')
        l2vpn = L2VPN.objects.first()

        L2VPNTermination.objects.create(l2vpn=l2vpn, assigned_object=ip_address)
        duplicate = L2VPNTermination(l2vpn=l2vpn, assigned_object=ip_address)
        self.assertRaises(ValidationError, duplicate.clean)

    def test_ipaddress_termination_parent(self):
        interface = Interface.objects.first()
        assigned_ip = IPAddress.objects.create(address='192.0.2.1/32', assigned_object=interface)
        unassigned_ip = IPAddress.objects.create(address='192.0.2.2/32')
        l2vpn = L2VPN.objects.first()

        termination = L2VPNTermination.objects.create(l2vpn=l2vpn, assigned_object=assigned_ip)
        self.assertEqual(termination.assigned_object_parent, interface.device)
        self.assertEqual(termination.assigned_object_site, interface.device.site)

        termination = L2VPNTermination.objects.create(l2vpn=l2vpn, assigned_object=unassigned_ip)
        self.assertIsNone(termination.assigned_object_parent)
        self.assertIsNone(termination.assigned_object_site)

    def test_vlan_termination_site(self):
        site = Site.objects.first()
        vlan = VLAN.objects.create(name='VLAN 8', vid=658, site=site)
        termination = L2VPNTermination.objects.create(l2vpn=L2VPN.objects.first(), assigned_object=vlan)
        self.assertIsNone(termination.assigned_object_parent)
        self.assertEqual(termination.assigned_object_site, site)

    def test_delete_ipaddress_deletes_terminations(self):
        ip_address = IPAddress.objects.create(address='192.0.2.1/32')
        termination = L2VPNTermination.objects.create(l2vpn=L2VPN.objects.first(), assigned_object=ip_address)

        ip_address.delete()
        self.assertFalse(L2VPNTermination.objects.filter(pk=termination.pk).exists())
