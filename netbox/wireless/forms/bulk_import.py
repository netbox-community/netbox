from dcim.choices import LinkStatusChoices
from dcim.models import Interface
from extras.forms import CustomFieldModelCSVForm
from ipam.models import VLAN
from utilities.forms import CSVChoiceField, CSVModelChoiceField
from wireless.models import *

__all__ = (
    'WirelessLANCSVForm',
    'WirelessLinkCSVForm',
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


class WirelessLinkCSVForm(CustomFieldModelCSVForm):
    status = CSVChoiceField(
        choices=LinkStatusChoices,
        help_text='Connection status'
    )
    interface_a = CSVModelChoiceField(
        queryset=Interface.objects.all()
    )
    interface_b = CSVModelChoiceField(
        queryset=Interface.objects.all()
    )

    class Meta:
        model = WirelessLink
        fields = ('interface_a', 'interface_b', 'ssid', 'description')
