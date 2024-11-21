from django.test import TestCase

from dcim.choices import InterfaceTypeChoices, LinkStatusChoices
from dcim.models import Interface, Location, Region, Site, SiteGroup
from ipam.models import VLAN
from netbox.choices import DistanceUnitChoices
from tenancy.models import Tenant
from wireless.choices import *
from wireless.filtersets import *
from wireless.models import *
from utilities.testing import ChangeLoggedFilterSetTests, create_test_device


class WirelessLANGroupTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = WirelessLANGroup.objects.all()
    filterset = WirelessLANGroupFilterSet

    @classmethod
    def setUpTestData(cls):

        parent_groups = (
            WirelessLANGroup(name='Wireless LAN Group 1', slug='wireless-lan-group-1', description='A'),
            WirelessLANGroup(name='Wireless LAN Group 2', slug='wireless-lan-group-2', description='B'),
            WirelessLANGroup(name='Wireless LAN Group 3', slug='wireless-lan-group-3', description='C'),
        )
        for group in parent_groups:
            group.save()

        groups = (
            WirelessLANGroup(
                name='Wireless LAN Group 1A',
                slug='wireless-lan-group-1a',
                parent=parent_groups[0],
                description='foobar1',
            ),
            WirelessLANGroup(
                name='Wireless LAN Group 1B',
                slug='wireless-lan-group-1b',
                parent=parent_groups[0],
                description='foobar2',
            ),
            WirelessLANGroup(name='Wireless LAN Group 2A', slug='wireless-lan-group-2a', parent=parent_groups[1]),
            WirelessLANGroup(name='Wireless LAN Group 2B', slug='wireless-lan-group-2b', parent=parent_groups[1]),
            WirelessLANGroup(name='Wireless LAN Group 3A', slug='wireless-lan-group-3a', parent=parent_groups[2]),
            WirelessLANGroup(name='Wireless LAN Group 3B', slug='wireless-lan-group-3b', parent=parent_groups[2]),
        )
        for group in groups:
            group.save()

        child_groups = (
            WirelessLANGroup(name='Wireless LAN Group 1A1', slug='wireless-lan-group-1a1', parent=groups[0]),
            WirelessLANGroup(name='Wireless LAN Group 1B1', slug='wireless-lan-group-1b1', parent=groups[1]),
            WirelessLANGroup(name='Wireless LAN Group 2A1', slug='wireless-lan-group-2a1', parent=groups[2]),
            WirelessLANGroup(name='Wireless LAN Group 2B1', slug='wireless-lan-group-2b1', parent=groups[3]),
            WirelessLANGroup(name='Wireless LAN Group 3A1', slug='wireless-lan-group-3a1', parent=groups[4]),
            WirelessLANGroup(name='Wireless LAN Group 3B1', slug='wireless-lan-group-3b1', parent=groups[5]),
        )
        for group in child_groups:
            group.save()

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Wireless LAN Group 1', 'Wireless LAN Group 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['wireless-lan-group-1', 'wireless-lan-group-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_parent(self):
        groups = WirelessLANGroup.objects.filter(parent__isnull=True)[:2]
        params = {'parent_id': [groups[0].pk, groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'parent': [groups[0].slug, groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_ancestor(self):
        groups = WirelessLANGroup.objects.filter(parent__isnull=True)[:2]
        params = {'ancestor_id': [groups[0].pk, groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 8)
        params = {'ancestor': [groups[0].slug, groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 8)


class WirelessLANTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = WirelessLAN.objects.all()
    filterset = WirelessLANFilterSet

    @classmethod
    def setUpTestData(cls):

        groups = (
            WirelessLANGroup(
                name='Wireless LAN Group 1',
                slug='wireless-lan-group-1'
            ),
            WirelessLANGroup(
                name='Wireless LAN Group 2',
                slug='wireless-lan-group-2'
            ),
            WirelessLANGroup(
                name='Wireless LAN Group 3',
                slug='wireless-lan-group-3'
            ),
        )
        for group in groups:
            group.save()

        vlans = (
            VLAN(name='VLAN1', vid=1),
            VLAN(name='VLAN2', vid=2),
            VLAN(name='VLAN3', vid=3),
        )
        VLAN.objects.bulk_create(vlans)

        regions = (
            Region(name='Test Region 1', slug='test-region-1'),
            Region(name='Test Region 2', slug='test-region-2'),
            Region(name='Test Region 3', slug='test-region-3'),
        )
        for r in regions:
            r.save()

        site_groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for site_group in site_groups:
            site_group.save()

        sites = (
            Site(name='Test Site 1', slug='test-site-1', region=regions[0], group=site_groups[0]),
            Site(name='Test Site 2', slug='test-site-2', region=regions[1], group=site_groups[1]),
            Site(name='Test Site 3', slug='test-site-3', region=regions[2], group=site_groups[2]),
        )
        Site.objects.bulk_create(sites)

        locations = (
            Location(name='Location 1', slug='location-1', site=sites[0]),
            Location(name='Location 2', slug='location-2', site=sites[2]),
        )
        for location in locations:
            location.save()

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1'),
            Tenant(name='Tenant 2', slug='tenant-2'),
            Tenant(name='Tenant 3', slug='tenant-3'),
        )
        Tenant.objects.bulk_create(tenants)

        wireless_lans = (
            WirelessLAN(
                ssid='WLAN1',
                group=groups[0],
                status=WirelessLANStatusChoices.STATUS_ACTIVE,
                vlan=vlans[0],
                tenant=tenants[0],
                auth_type=WirelessAuthTypeChoices.TYPE_OPEN,
                auth_cipher=WirelessAuthCipherChoices.CIPHER_AUTO,
                auth_psk='PSK1',
                description='foobar1',
                scope=sites[0]
            ),
            WirelessLAN(
                ssid='WLAN2',
                group=groups[1],
                status=WirelessLANStatusChoices.STATUS_DISABLED,
                vlan=vlans[1],
                tenant=tenants[1],
                auth_type=WirelessAuthTypeChoices.TYPE_WEP,
                auth_cipher=WirelessAuthCipherChoices.CIPHER_TKIP,
                auth_psk='PSK2',
                description='foobar2',
                scope=locations[0]
            ),
            WirelessLAN(
                ssid='WLAN3',
                group=groups[2],
                status=WirelessLANStatusChoices.STATUS_RESERVED,
                vlan=vlans[2],
                tenant=tenants[2],
                auth_type=WirelessAuthTypeChoices.TYPE_WPA_PERSONAL,
                auth_cipher=WirelessAuthCipherChoices.CIPHER_AES,
                auth_psk='PSK3',
                description='foobar3',
                scope=locations[1]
            ),
        )
        for wireless_lan in wireless_lans:
            wireless_lan.save()

        device = create_test_device('Device 1', site=sites[0])
        interfaces = (
            Interface(device=device, name='Interface 1', type=InterfaceTypeChoices.TYPE_80211N),
            Interface(device=device, name='Interface 2', type=InterfaceTypeChoices.TYPE_80211N),
            Interface(device=device, name='Interface 3', type=InterfaceTypeChoices.TYPE_80211N),
        )
        Interface.objects.bulk_create(interfaces)
        interfaces[0].wireless_lans.add(wireless_lans[0])
        interfaces[1].wireless_lans.add(wireless_lans[1])
        interfaces[2].wireless_lans.add(wireless_lans[2])

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_ssid(self):
        params = {'ssid': ['WLAN1', 'WLAN2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_group(self):
        groups = WirelessLANGroup.objects.all()[:2]
        params = {'group_id': [groups[0].pk, groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'group': [groups[0].slug, groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {'status': [WirelessLANStatusChoices.STATUS_ACTIVE, WirelessLANStatusChoices.STATUS_DISABLED]}
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

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant(self):
        tenants = Tenant.objects.all()[:2]
        params = {'tenant_id': [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'tenant': [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_interface(self):
        interfaces = Interface.objects.all()[:2]
        params = {'interface_id': [interfaces[0].pk, interfaces[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site_group(self):
        site_groups = SiteGroup.objects.all()[:2]
        params = {'site_group_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site_group': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_location(self):
        locations = Location.objects.all()[:1]
        params = {'location_id': [locations[0].pk,]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {'location': [locations[0].slug,]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_scope_type(self):
        params = {'scope_type': 'dcim.location'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class WirelessLinkTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = WirelessLink.objects.all()
    filterset = WirelessLinkFilterSet

    @classmethod
    def setUpTestData(cls):

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1'),
            Tenant(name='Tenant 2', slug='tenant-2'),
            Tenant(name='Tenant 3', slug='tenant-3'),
        )
        Tenant.objects.bulk_create(tenants)

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
            auth_psk='PSK1',
            tenant=tenants[0],
            distance=10,
            distance_unit=DistanceUnitChoices.UNIT_FOOT,
            description='foobar1'
        ).save()
        WirelessLink(
            interface_a=interfaces[1],
            interface_b=interfaces[3],
            ssid='LINK2',
            status=LinkStatusChoices.STATUS_PLANNED,
            auth_type=WirelessAuthTypeChoices.TYPE_WEP,
            auth_cipher=WirelessAuthCipherChoices.CIPHER_TKIP,
            auth_psk='PSK2',
            tenant=tenants[1],
            distance=20,
            distance_unit=DistanceUnitChoices.UNIT_METER,
            description='foobar2'
        ).save()
        WirelessLink(
            interface_a=interfaces[4],
            interface_b=interfaces[6],
            ssid='LINK3',
            status=LinkStatusChoices.STATUS_DECOMMISSIONING,
            auth_type=WirelessAuthTypeChoices.TYPE_WPA_PERSONAL,
            auth_cipher=WirelessAuthCipherChoices.CIPHER_AES,
            auth_psk='PSK3',
            distance=30,
            distance_unit=DistanceUnitChoices.UNIT_METER,
            tenant=tenants[2],
        ).save()
        WirelessLink(
            interface_a=interfaces[5],
            interface_b=interfaces[7],
            ssid='LINK4'
        ).save()

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

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

    def test_distance(self):
        params = {'distance': [10, 20]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_distance_unit(self):
        params = {'distance_unit': DistanceUnitChoices.UNIT_FOOT}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant(self):
        tenants = Tenant.objects.all()[:2]
        params = {'tenant_id': [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'tenant': [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
