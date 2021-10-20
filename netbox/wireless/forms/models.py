from dcim.models import Device, Interface
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

    class Meta:
        model = WirelessLANGroup
        fields = [
            'parent', 'name', 'slug', 'description',
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
    device_a = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        label='Device A',
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
        label='Interface A'
    )
    device_b = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        label='Device B',
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
        label='Interface B'
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = WirelessLink
        fields = [
            'device_a', 'interface_a', 'device_b', 'interface_b', 'status', 'ssid', 'description', 'auth_type',
            'auth_cipher', 'auth_psk', 'tags',
        ]
        fieldsets = (
            ('Link', ('device_a', 'interface_a', 'device_b', 'interface_b', 'status', 'ssid', 'description', 'tags')),
            ('Authentication', ('auth_type', 'auth_cipher', 'auth_psk')),
        )
        widgets = {
            'status': StaticSelect,
            'auth_type': StaticSelect,
            'auth_cipher': StaticSelect,
        }
