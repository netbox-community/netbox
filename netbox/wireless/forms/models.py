from dcim.models import Device, Interface, Location, Site
from extras.forms import CustomFieldModelForm
from extras.models import Tag
from ipam.models import VLAN
from utilities.forms import (
    BootstrapMixin, DynamicModelChoiceField, DynamicModelMultipleChoiceField, SlugField, StaticSelect,
)
from wireless.models import *

__all__ = (
    'WirelessLANForm',
    'WirelessLANGroupForm',
    'WirelessLinkForm',
)


class WirelessLANGroupForm(BootstrapMixin, CustomFieldModelForm):
    parent = DynamicModelChoiceField(
        queryset=WirelessLANGroup.objects.all(),
        required=False
    )
    slug = SlugField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = WirelessLANGroup
        fields = [
            'parent', 'name', 'slug', 'description', 'tags',
        ]


class WirelessLANForm(BootstrapMixin, CustomFieldModelForm):
    group = DynamicModelChoiceField(
        queryset=WirelessLANGroup.objects.all(),
        required=False
    )
    vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label='VLAN'
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = WirelessLAN
        fields = [
            'ssid', 'group', 'description', 'vlan', 'auth_type', 'auth_cipher', 'auth_psk', 'tags',
        ]
        fieldsets = (
            ('Wireless LAN', ('ssid', 'group', 'description', 'tags')),
            ('VLAN', ('vlan',)),
            ('Authentication', ('auth_type', 'auth_cipher', 'auth_psk')),
        )
        widgets = {
            'auth_type': StaticSelect,
            'auth_cipher': StaticSelect,
        }


class WirelessLinkForm(BootstrapMixin, CustomFieldModelForm):
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
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = WirelessLink
        fields = [
            'site_a', 'location_a', 'device_a', 'interface_a', 'site_b', 'location_b', 'device_b', 'interface_b',
            'status', 'ssid', 'description', 'auth_type', 'auth_cipher', 'auth_psk', 'tags',
        ]
        fieldsets = (
            ('Side A', ('site_a', 'location_a', 'device_a', 'interface_a')),
            ('Side B', ('site_b', 'location_b', 'device_b', 'interface_b')),
            ('Link', ('status', 'ssid', 'description', 'tags')),
            ('Authentication', ('auth_type', 'auth_cipher', 'auth_psk')),
        )
        widgets = {
            'status': StaticSelect,
            'auth_type': StaticSelect,
            'auth_cipher': StaticSelect,
        }
        labels = {
            'auth_type': 'Type',
            'auth_cipher': 'Cipher',
        }
