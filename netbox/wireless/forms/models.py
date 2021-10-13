from dcim.models import Interface
from extras.forms import CustomFieldModelForm
from extras.models import Tag
from ipam.models import VLAN
from utilities.forms import BootstrapMixin, DynamicModelChoiceField, DynamicModelMultipleChoiceField, StaticSelect
from wireless.models import *

__all__ = (
    'WirelessLANForm',
    'WirelessLinkForm',
)


class WirelessLANForm(BootstrapMixin, CustomFieldModelForm):
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
            'ssid', 'description', 'vlan', 'tags',
        ]
        fieldsets = (
            ('Wireless LAN', ('ssid', 'description', 'tags')),
            ('VLAN', ('vlan',)),
        )


class WirelessLinkForm(BootstrapMixin, CustomFieldModelForm):
    interface_a = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        query_params={
            'kind': 'wireless'
        },
        label='Interface A'
    )
    interface_b = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        query_params={
            'kind': 'wireless'
        },
        label='Interface B'
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = WirelessLink
        fields = [
            'interface_a', 'interface_b', 'status', 'ssid', 'description', 'tags',
        ]
        widgets = {
            'status': StaticSelect,
        }
