from dcim.models import Device, Interface, Location, Region, Site, SiteGroup
from ipam.models import VLAN, VLANGroup
from netbox.forms import NetBoxModelForm
from utilities.forms import DynamicModelChoiceField, SlugField, StaticSelect
from wireless.models import *

__all__ = (
    'WirelessLANForm',
    'WirelessLANGroupForm',
    'WirelessLinkForm',
)


class WirelessLANGroupForm(NetBoxModelForm):
    parent = DynamicModelChoiceField(
        queryset=WirelessLANGroup.objects.all(),
        required=False
    )
    slug = SlugField()

    class Meta:
        model = WirelessLANGroup
        fields = [
            'parent', 'name', 'slug', 'description', 'tags',
        ]


class WirelessLANForm(NetBoxModelForm):
    group = DynamicModelChoiceField(
        queryset=WirelessLANGroup.objects.all(),
        required=False
    )

    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    vlan_group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        label='VLAN group',
        null_option='None',
        query_params={
            'site': '$site'
        },
        initial_params={
            'vlans': '$vlan'
        }
    )
    vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label='VLAN',
        query_params={
            'site_id': '$site',
            'group_id': '$vlan_group',
        }
    )

    fieldsets = (
        ('Wireless LAN', ('ssid', 'group', 'description', 'tags')),
        ('VLAN', ('region', 'site_group', 'site', 'vlan_group', 'vlan',)),
        ('Authentication', ('auth_type', 'auth_cipher', 'auth_psk')),
    )

    class Meta:
        model = WirelessLAN
        fields = [
            'ssid', 'group', 'description', 'region', 'site_group', 'site', 'vlan_group', 'vlan', 'auth_type',
            'auth_cipher', 'auth_psk', 'tags',
        ]
        widgets = {
            'auth_type': StaticSelect,
            'auth_cipher': StaticSelect,
        }


class WirelessLinkForm(NetBoxModelForm):
    site_a = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Site',
        initial_params={
            'devices': '$device_a',
        }
    )
    location_a = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        query_params={
            'site_id': '$site_a',
        },
        required=False,
        label='Location',
        initial_params={
            'devices': '$device_a',
        }
    )
    device_a = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        query_params={
            'site_id': '$site_a',
            'location_id': '$location_a',
        },
        required=False,
        label='Device',
        initial_params={
            'interfaces': '$interface_a'
        }
    )
    interface_a = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        query_params={
            'kind': 'wireless',
            'device_id': '$device_a',
        },
        disabled_indicator='_occupied',
        label='Interface'
    )
    site_b = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Site',
        initial_params={
            'devices': '$device_b',
        }
    )
    location_b = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        query_params={
            'site_id': '$site_b',
        },
        required=False,
        label='Location',
        initial_params={
            'devices': '$device_b',
        }
    )
    device_b = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        query_params={
            'site_id': '$site_b',
            'location_id': '$location_b',
        },
        required=False,
        label='Device',
        initial_params={
            'interfaces': '$interface_b'
        }
    )
    interface_b = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        query_params={
            'kind': 'wireless',
            'device_id': '$device_b',
        },
        disabled_indicator='_occupied',
        label='Interface'
    )

    fieldsets = (
        ('Side A', ('site_a', 'location_a', 'device_a', 'interface_a')),
        ('Side B', ('site_b', 'location_b', 'device_b', 'interface_b')),
        ('Link', ('status', 'ssid', 'description', 'tags')),
        ('Authentication', ('auth_type', 'auth_cipher', 'auth_psk')),
    )

    class Meta:
        model = WirelessLink
        fields = [
            'site_a', 'location_a', 'device_a', 'interface_a', 'site_b', 'location_b', 'device_b', 'interface_b',
            'status', 'ssid', 'description', 'auth_type', 'auth_cipher', 'auth_psk', 'tags',
        ]
        widgets = {
            'status': StaticSelect,
            'auth_type': StaticSelect,
            'auth_cipher': StaticSelect,
        }
        labels = {
            'auth_type': 'Type',
            'auth_cipher': 'Cipher',
        }
