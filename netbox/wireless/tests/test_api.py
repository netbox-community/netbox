from django.urls import reverse

from dcim.choices import InterfaceTypeChoices
from dcim.models import Interface
from tenancy.models import Tenant
from utilities.testing import APITestCase, APIViewTestCases, create_test_device
from wireless.choices import *
from wireless.models import *


class AppTest(APITestCase):

    def test_root(self):
        url = reverse('wireless-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class WirelessLANGroupTest(APIViewTestCases.APIViewTestCase):
    model = WirelessLANGroup
    brief_fields = ['_depth', 'description', 'display', 'id', 'name', 'slug', 'url', 'wirelesslan_count']
    create_data = [
        {
            'name': 'Wireless LAN Group 4',
            'slug': 'wireless-lan-group-4',
        },
        {
            'name': 'Wireless LAN Group 5',
            'slug': 'wireless-lan-group-5',
        },
        {
            'name': 'Wireless LAN Group 6',
            'slug': 'wireless-lan-group-6',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        WirelessLANGroup.objects.create(name='Wireless LAN Group 1', slug='wireless-lan-group-1')
        WirelessLANGroup.objects.create(name='Wireless LAN Group 2', slug='wireless-lan-group-2')
        WirelessLANGroup.objects.create(name='Wireless LAN Group 3', slug='wireless-lan-group-3')


class WirelessLANTest(APIViewTestCases.APIViewTestCase):
    model = WirelessLAN
    brief_fields = ['description', 'display', 'id', 'ssid', 'url']

    @classmethod
    def setUpTestData(cls):

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1'),
            Tenant(name='Tenant 2', slug='tenant-2'),
        )
        Tenant.objects.bulk_create(tenants)

        groups = (
            WirelessLANGroup(name='Group 1', slug='group-1'),
            WirelessLANGroup(name='Group 2', slug='group-2'),
            WirelessLANGroup(name='Group 3', slug='group-3'),
        )
        for group in groups:
            group.save()

        wireless_lans = (
            WirelessLAN(ssid='WLAN1', status=WirelessLANStatusChoices.STATUS_ACTIVE),
            WirelessLAN(ssid='WLAN2', status=WirelessLANStatusChoices.STATUS_ACTIVE),
            WirelessLAN(ssid='WLAN3', status=WirelessLANStatusChoices.STATUS_ACTIVE),
        )
        WirelessLAN.objects.bulk_create(wireless_lans)

        cls.create_data = [
            {
                'ssid': 'WLAN4',
                'group': groups[0].pk,
                'status': WirelessLANStatusChoices.STATUS_DISABLED,
                'tenant': tenants[0].pk,
                'auth_type': WirelessAuthTypeChoices.TYPE_OPEN,
            },
            {
                'ssid': 'WLAN5',
                'group': groups[1].pk,
                'status': WirelessLANStatusChoices.STATUS_DISABLED,
                'tenant': tenants[0].pk,
                'auth_type': WirelessAuthTypeChoices.TYPE_WPA_PERSONAL,
            },
            {
                'ssid': 'WLAN6',
                'status': WirelessLANStatusChoices.STATUS_DISABLED,
                'tenant': tenants[0].pk,
                'auth_type': WirelessAuthTypeChoices.TYPE_WPA_ENTERPRISE,
            },
        ]

        cls.bulk_update_data = {
            'status': WirelessLANStatusChoices.STATUS_DEPRECATED,
            'group': groups[2].pk,
            'tenant': tenants[1].pk,
            'description': 'New description',
            'auth_type': WirelessAuthTypeChoices.TYPE_WPA_PERSONAL,
            'auth_cipher': WirelessAuthCipherChoices.CIPHER_AES,
            'auth_psk': 'abc123def456',
        }


class WirelessLinkTest(APIViewTestCases.APIViewTestCase):
    model = WirelessLink
    brief_fields = ['description', 'display', 'id', 'ssid', 'url']
    bulk_update_data = {
        'status': 'planned',
    }

    @classmethod
    def setUpTestData(cls):
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

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1'),
            Tenant(name='Tenant 2', slug='tenant-2'),
        )
        Tenant.objects.bulk_create(tenants)

        wireless_links = (
            WirelessLink(ssid='LINK1', interface_a=interfaces[0], interface_b=interfaces[1], tenant=tenants[0]),
            WirelessLink(ssid='LINK2', interface_a=interfaces[2], interface_b=interfaces[3], tenant=tenants[0]),
            WirelessLink(ssid='LINK3', interface_a=interfaces[4], interface_b=interfaces[5], tenant=tenants[0]),
        )
        WirelessLink.objects.bulk_create(wireless_links)

        cls.create_data = [
            {
                'interface_a': interfaces[6].pk,
                'interface_b': interfaces[7].pk,
                'ssid': 'LINK4',
                'tenant': tenants[1].pk,
            },
            {
                'interface_a': interfaces[8].pk,
                'interface_b': interfaces[9].pk,
                'ssid': 'LINK5',
                'tenant': tenants[1].pk,
            },
            {
                'interface_a': interfaces[10].pk,
                'interface_b': interfaces[11].pk,
                'ssid': 'LINK6',
                'tenant': tenants[1].pk,
            },
        ]
