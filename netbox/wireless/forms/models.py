from extras.forms import CustomFieldModelForm
from extras.models import Tag
from ipam.models import VLAN
from utilities.forms import BootstrapMixin, DynamicModelChoiceField, DynamicModelMultipleChoiceField
from wireless.models import WirelessLAN

__all__ = (
    'WirelessLANForm',
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
