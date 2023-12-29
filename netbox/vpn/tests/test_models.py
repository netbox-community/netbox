from django.core.exceptions import ValidationError
from django.test import TestCase

from dcim.models import Interface, Device, DeviceRole, DeviceType, Manufacturer, Site
from ipam.models import VLAN
from vpn.models import *


class TestL2VPNTermination(TestCase):

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
