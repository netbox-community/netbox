from django.contrib.contenttypes.models import ContentType
from wireless.choices import *
from wireless.models import *
from dcim.choices import InterfaceTypeChoices, LinkStatusChoices
from dcim.models import Interface, Site
from netbox.choices import DistanceUnitChoices
from tenancy.models import Tenant
from utilities.testing import ViewTestCases, create_tags, create_test_device


class WirelessLANGroupTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = WirelessLANGroup

    @classmethod
    def setUpTestData(cls):

        groups = (
            WirelessLANGroup(name='Wireless LAN Group 1', slug='wireless-lan-group-1'),
            WirelessLANGroup(name='Wireless LAN Group 2', slug='wireless-lan-group-2'),
            WirelessLANGroup(name='Wireless LAN Group 3', slug='wireless-lan-group-3'),
        )
        for group in groups:
            group.save()

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Wireless LAN Group X',
            'slug': 'wireless-lan-group-x',
            'parent': groups[2].pk,
            'description': 'A new wireless LAN group',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug,description",
            "Wireless LAN Group 4,wireless-lan-group-4,Fourth wireless LAN group",
            "Wireless LAN Group 5,wireless-lan-group-5,Fifth wireless LAN group",
            "Wireless LAN Group 6,wireless-lan-group-6,Sixth wireless LAN group",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{groups[0].pk},Wireless LAN Group 7,Fourth wireless LAN group7",
            f"{groups[1].pk},Wireless LAN Group 8,Fifth wireless LAN group8",
            f"{groups[2].pk},Wireless LAN Group 0,Sixth wireless LAN group9",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }


class WirelessLANTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = WirelessLAN

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1'),
            Tenant(name='Tenant 2', slug='tenant-2'),
            Tenant(name='Tenant 3', slug='tenant-3'),
        )
        Tenant.objects.bulk_create(tenants)

        groups = (
            WirelessLANGroup(name='Wireless LAN Group 1', slug='wireless-lan-group-1'),
            WirelessLANGroup(name='Wireless LAN Group 2', slug='wireless-lan-group-2'),
        )
        for group in groups:
            group.save()

        wireless_lans = (
            WirelessLAN(
                group=groups[0],
                ssid='WLAN1',
                status=WirelessLANStatusChoices.STATUS_ACTIVE,
                tenant=tenants[0]
            ),
            WirelessLAN(
                group=groups[0],
                ssid='WLAN2',
                status=WirelessLANStatusChoices.STATUS_ACTIVE,
                tenant=tenants[0]
            ),
            WirelessLAN(
                group=groups[0],
                ssid='WLAN3',
                status=WirelessLANStatusChoices.STATUS_ACTIVE,
                tenant=tenants[0]
            ),
        )
        WirelessLAN.objects.bulk_create(wireless_lans)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'ssid': 'WLAN2',
            'group': groups[1].pk,
            'status': WirelessLANStatusChoices.STATUS_DISABLED,
            'scope_type': ContentType.objects.get_for_model(Site).pk,
            'scope': sites[1].pk,
            'tenant': tenants[1].pk,
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "group,ssid,status,tenant,scope_type,scope_id",
            f"Wireless LAN Group 2,WLAN4,{WirelessLANStatusChoices.STATUS_ACTIVE},{tenants[0].name},,",
            f"Wireless LAN Group 2,WLAN5,{WirelessLANStatusChoices.STATUS_DISABLED},{tenants[1].name},dcim.site,{sites[0].pk}",
            f"Wireless LAN Group 2,WLAN6,{WirelessLANStatusChoices.STATUS_RESERVED},{tenants[2].name},dcim.site,{sites[1].pk}",
        )

        cls.csv_update_data = (
            "id,ssid",
            f"{wireless_lans[0].pk},WLAN7",
            f"{wireless_lans[1].pk},WLAN8",
            f"{wireless_lans[2].pk},WLAN9",
        )

        cls.bulk_edit_data = {
            'status': WirelessLANStatusChoices.STATUS_DISABLED,
            'description': 'New description',
        }


class WirelessLinkTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = WirelessLink

    @classmethod
    def setUpTestData(cls):

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1'),
            Tenant(name='Tenant 2', slug='tenant-2'),
            Tenant(name='Tenant 3', slug='tenant-3'),
        )
        Tenant.objects.bulk_create(tenants)

        device = create_test_device('test-device')
        interfaces = [
            Interface(
                device=device,
                name=f'radio{i}',
                type=InterfaceTypeChoices.TYPE_80211AC,
                rf_channel=WirelessChannelChoices.CHANNEL_5G_32,
                rf_channel_frequency=5160,
                rf_channel_width=20
            ) for i in range(12)
        ]
        Interface.objects.bulk_create(interfaces)

        wirelesslink1 = WirelessLink(interface_a=interfaces[0], interface_b=interfaces[1], ssid='LINK1', tenant=tenants[0])
        wirelesslink1.save()
        wirelesslink2 = WirelessLink(interface_a=interfaces[2], interface_b=interfaces[3], ssid='LINK2', tenant=tenants[0])
        wirelesslink2.save()
        wirelesslink3 = WirelessLink(interface_a=interfaces[4], interface_b=interfaces[5], ssid='LINK3', tenant=tenants[0])
        wirelesslink3.save()

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'interface_a': interfaces[6].pk,
            'interface_b': interfaces[7].pk,
            'status': LinkStatusChoices.STATUS_PLANNED,
            'distance': 100,
            'distance_unit': DistanceUnitChoices.UNIT_FOOT,
            'tenant': tenants[1].pk,
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "interface_a,interface_b,status,tenant",
            f"{interfaces[6].pk},{interfaces[7].pk},connected,{tenants[0].name}",
            f"{interfaces[8].pk},{interfaces[9].pk},connected,{tenants[1].name}",
            f"{interfaces[10].pk},{interfaces[11].pk},connected,{tenants[2].name}",
        )

        cls.csv_update_data = (
            "id,ssid,description",
            f"{wirelesslink1.pk},LINK7,New decription 7",
            f"{wirelesslink2.pk},LINK8,New decription 8",
            f"{wirelesslink3.pk},LINK9,New decription 9",
        )

        cls.bulk_edit_data = {
            'status': LinkStatusChoices.STATUS_PLANNED,
            'distance': 50,
            'distance_unit': DistanceUnitChoices.UNIT_METER,
        }
