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
        required=False
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = WirelessLAN
        fields = [
            'ssid', 'group', 'description', 'vlan', 'tags',
        ]
        fieldsets = (
            ('Wireless LAN', ('ssid', 'group', 'description', 'tags')),
            ('VLAN', ('vlan',)),
        )


class WirelessLinkForm(BootstrapMixin, CustomFieldModelForm):
    device_a = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        label='Device A'
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
        label='Device B'
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
            'device_a', 'interface_a', 'device_b', 'interface_b', 'status', 'ssid', 'description', 'tags',
        ]
        widgets = {
            'status': StaticSelect,
        }
