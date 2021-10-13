from dcim.choices import LinkStatusChoices
from dcim.models import Interface
from extras.forms import CustomFieldModelCSVForm
from ipam.models import VLAN
from utilities.forms import CSVChoiceField, CSVModelChoiceField, SlugField
from wireless.models import *

__all__ = (
    'WirelessLANCSVForm',
    'WirelessLANGroupCSVForm',
    'WirelessLinkCSVForm',
)


class WirelessLANGroupCSVForm(CustomFieldModelCSVForm):
    parent = CSVModelChoiceField(
        queryset=WirelessLANGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Parent group'
    )
    slug = SlugField()

    class Meta:
        model = WirelessLANGroup
        fields = ('name', 'slug', 'parent', 'description')


class WirelessLANCSVForm(CustomFieldModelCSVForm):
    group = CSVModelChoiceField(
        queryset=WirelessLANGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned group'
    )
    vlan = CSVModelChoiceField(
        queryset=VLAN.objects.all(),
        to_field_name='name',
        help_text='Bridged VLAN'
    )

    class Meta:
        model = WirelessLAN
        fields = ('ssid', 'group', 'description', 'vlan')


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
