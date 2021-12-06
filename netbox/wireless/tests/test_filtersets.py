from django.test import TestCase

from dcim.choices import InterfaceTypeChoices, LinkStatusChoices
from dcim.models import Interface
from ipam.models import VLAN
from wireless.choices import *
from wireless.filtersets import *
from wireless.models import *
from utilities.testing import ChangeLoggedFilterSetTests, create_test_device


class WirelessLANGroupTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = WirelessLANGroup.objects.all()
    filterset = WirelessLANGroupFilterSet

    @classmethod
    def setUpTestData(cls):

        groups = (
            WirelessLANGroup(name='Wireless LAN Group 1', slug='wireless-lan-group-1', description='A'),
            WirelessLANGroup(name='Wireless LAN Group 2', slug='wireless-lan-group-2', description='B'),
            WirelessLANGroup(name='Wireless LAN Group 3', slug='wireless-lan-group-3', description='C'),
        )
        for group in groups:
            group.save()

        child_groups = (
            WirelessLANGroup(name='Wireless LAN Group 1A', slug='wireless-lan-group-1a', parent=groups[0]),
            WirelessLANGroup(name='Wireless LAN Group 1B', slug='wireless-lan-group-1b', parent=groups[0]),
            WirelessLANGroup(name='Wireless LAN Group 2A', slug='wireless-lan-group-2a', parent=groups[1]),
            WirelessLANGroup(name='Wireless LAN Group 2B', slug='wireless-lan-group-2b', parent=groups[1]),
            WirelessLANGroup(name='Wireless LAN Group 3A', slug='wireless-lan-group-3a', parent=groups[2]),
            WirelessLANGroup(name='Wireless LAN Group 3B', slug='wireless-lan-group-3b', parent=groups[2]),
        )
        for group in child_groups:
            group.save()

    def test_name(self):
        params = {'name': ['Wireless LAN Group 1', 'Wireless LAN Group 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['wireless-lan-group-1', 'wireless-lan-group-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['A', 'B']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_parent(self):
        parent_groups = WirelessLANGroup.objects.filter(parent__isnull=True)[:2]
        params = {'parent_id': [parent_groups[0].pk, parent_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'parent': [parent_groups[0].slug, parent_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)


class WirelessLANTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = WirelessLAN.objects.all()
    filterset = WirelessLANFilterSet

    @classmethod
    def setUpTestData(cls):

        groups = (
            WirelessLANGroup(name='Wireless LAN Group 1', slug='wireless-lan-group-1'),
            WirelessLANGroup(name='Wireless LAN Group 2', slug='wireless-lan-group-2'),
            WirelessLANGroup(name='Wireless LAN Group 3', slug='wireless-lan-group-3'),
        )
        for group in groups:
            group.save()

        vlans = (
            VLAN(name='VLAN1', vid=1),
            VLAN(name='VLAN2', vid=2),
            VLAN(name='VLAN3', vid=3),
        )
        VLAN.objects.bulk_create(vlans)

        wireless_lans = (
            WirelessLAN(ssid='WLAN1', group=groups[0], vlan=vlans[0], auth_type=WirelessAuthTypeChoices.TYPE_OPEN, auth_cipher=WirelessAuthCipherChoices.CIPHER_AUTO, auth_psk='PSK1'),
            WirelessLAN(ssid='WLAN2', group=groups[1], vlan=vlans[1], auth_type=WirelessAuthTypeChoices.TYPE_WEP, auth_cipher=WirelessAuthCipherChoices.CIPHER_TKIP, auth_psk='PSK2'),
            WirelessLAN(ssid='WLAN3', group=groups[2], vlan=vlans[2], auth_type=WirelessAuthTypeChoices.TYPE_WPA_PERSONAL, auth_cipher=WirelessAuthCipherChoices.CIPHER_AES, auth_psk='PSK3'),
        )
        WirelessLAN.objects.bulk_create(wireless_lans)

    def test_ssid(self):
        params = {'ssid': ['WLAN1', 'WLAN2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_group(self):
        groups = WirelessLANGroup.objects.all()[:2]
        params = {'group_id': [groups[0].pk, groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'group': [groups[0].slug, groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_vlan(self):
        vlans = VLAN.objects.all()[:2]
        params = {'vlan_id': [vlans[0].pk, vlans[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_auth_type(self):
        params = {'auth_type': [WirelessAuthTypeChoices.TYPE_OPEN, WirelessAuthTypeChoices.TYPE_WEP]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_auth_cipher(self):
        params = {'auth_cipher': [WirelessAuthCipherChoices.CIPHER_AUTO, WirelessAuthCipherChoices.CIPHER_TKIP]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_auth_psk(self):
        params = {'auth_psk': ['PSK1', 'PSK2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class WirelessLinkTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = WirelessLink.objects.all()
    filterset = WirelessLinkFilterSet

    @classmethod
    def setUpTestData(cls):

        devices = (
            create_test_device('device1'),
            create_test_device('device2'),
            create_test_device('device3'),
            create_test_device('device4'),
        )

        interfaces = (
            Interface(device=devices[0], name='Interface 1', type=InterfaceTypeChoices.TYPE_80211AC),
            Interface(device=devices[0], name='Interface 2', type=InterfaceTypeChoices.TYPE_80211AC),
            Interface(device=devices[1], name='Interface 3', type=InterfaceTypeChoices.TYPE_80211AC),
            Interface(device=devices[1], name='Interface 4', type=InterfaceTypeChoices.TYPE_80211AC),
            Interface(device=devices[2], name='Interface 5', type=InterfaceTypeChoices.TYPE_80211AC),
            Interface(device=devices[2], name='Interface 6', type=InterfaceTypeChoices.TYPE_80211AC),
            Interface(device=devices[3], name='Interface 7', type=InterfaceTypeChoices.TYPE_80211AC),
            Interface(device=devices[3], name='Interface 8', type=InterfaceTypeChoices.TYPE_80211AC),
        )
        Interface.objects.bulk_create(interfaces)

        # Wireless links
        WirelessLink(
            interface_a=interfaces[0],
            interface_b=interfaces[2],
            ssid='LINK1',
            status=LinkStatusChoices.STATUS_CONNECTED,
            auth_type=WirelessAuthTypeChoices.TYPE_OPEN,
            auth_cipher=WirelessAuthCipherChoices.CIPHER_AUTO,
            auth_psk='PSK1'
        ).save()
        WirelessLink(
            interface_a=interfaces[1],
            interface_b=interfaces[3],
            ssid='LINK2',
            status=LinkStatusChoices.STATUS_PLANNED,
            auth_type=WirelessAuthTypeChoices.TYPE_WEP,
            auth_cipher=WirelessAuthCipherChoices.CIPHER_TKIP,
            auth_psk='PSK2'
        ).save()
        WirelessLink(
            interface_a=interfaces[4],
            interface_b=interfaces[6],
            ssid='LINK3',
            status=LinkStatusChoices.STATUS_DECOMMISSIONING,
            auth_type=WirelessAuthTypeChoices.TYPE_WPA_PERSONAL,
            auth_cipher=WirelessAuthCipherChoices.CIPHER_AES,
            auth_psk='PSK3'
        ).save()
        WirelessLink(
            interface_a=interfaces[5],
            interface_b=interfaces[7],
            ssid='LINK4'
        ).save()

    def test_ssid(self):
        params = {'ssid': ['LINK1', 'LINK2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {'status': [LinkStatusChoices.STATUS_PLANNED, LinkStatusChoices.STATUS_DECOMMISSIONING]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_auth_type(self):
        params = {'auth_type': [WirelessAuthTypeChoices.TYPE_OPEN, WirelessAuthTypeChoices.TYPE_WEP]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_auth_cipher(self):
        params = {'auth_cipher': [WirelessAuthCipherChoices.CIPHER_AUTO, WirelessAuthCipherChoices.CIPHER_TKIP]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_auth_psk(self):
        params = {'auth_psk': ['PSK1', 'PSK2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
