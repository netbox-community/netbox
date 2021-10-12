from extras.forms import CustomFieldModelCSVForm
from ipam.models import VLAN
from utilities.forms import CSVModelChoiceField
from wireless.models import WirelessLAN

__all__ = (
    'WirelessLANCSVForm',
)


class WirelessLANCSVForm(CustomFieldModelCSVForm):
    vlan = CSVModelChoiceField(
        queryset=VLAN.objects.all(),
        to_field_name='name',
        help_text='Bridged VLAN'
    )

    class Meta:
        model = WirelessLAN
        fields = ('ssid', 'description', 'vlan')
