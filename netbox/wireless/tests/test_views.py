from wireless.choices import *
from wireless.models import *
from dcim.choices import InterfaceTypeChoices, LinkStatusChoices
from dcim.models import Interface
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
            "Wireles sLAN Group 4,wireless-lan-group-4,Fourth wireless LAN group",
            "Wireless LAN Group 5,wireless-lan-group-5,Fifth wireless LAN group",
            "Wireless LAN Group 6,wireless-lan-group-6,Sixth wireless LAN group",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }


class WirelessLANTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = WirelessLAN

    @classmethod
    def setUpTestData(cls):

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

        WirelessLAN.objects.bulk_create([
            WirelessLAN(group=groups[0], ssid='WLAN1', tenant=tenants[0]),
            WirelessLAN(group=groups[0], ssid='WLAN2', tenant=tenants[0]),
            WirelessLAN(group=groups[0], ssid='WLAN3', tenant=tenants[0]),
        ])

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'ssid': 'WLAN2',
            'group': groups[1].pk,
            'tenant': tenants[1].pk,
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            f"group,ssid,tenant",
            f"Wireless LAN Group 2,WLAN4,{tenants[0].name}",
            f"Wireless LAN Group 2,WLAN5,{tenants[1].name}",
            f"Wireless LAN Group 2,WLAN6,{tenants[2].name}",
        )

        cls.bulk_edit_data = {
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

        WirelessLink(interface_a=interfaces[0], interface_b=interfaces[1], ssid='LINK1', tenant=tenants[0]).save()
        WirelessLink(interface_a=interfaces[2], interface_b=interfaces[3], ssid='LINK2', tenant=tenants[0]).save()
        WirelessLink(interface_a=interfaces[4], interface_b=interfaces[5], ssid='LINK3', tenant=tenants[0]).save()

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'interface_a': interfaces[6].pk,
            'interface_b': interfaces[7].pk,
            'status': LinkStatusChoices.STATUS_PLANNED,
            'tenant': tenants[1].pk,
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            f"interface_a,interface_b,status,tenant",
            f"{interfaces[6].pk},{interfaces[7].pk},connected,{tenants[0].name}",
            f"{interfaces[8].pk},{interfaces[9].pk},connected,{tenants[1].name}",
            f"{interfaces[10].pk},{interfaces[11].pk},connected,{tenants[2].name}",
        )

        cls.bulk_edit_data = {
            'status': LinkStatusChoices.STATUS_PLANNED,
        }
