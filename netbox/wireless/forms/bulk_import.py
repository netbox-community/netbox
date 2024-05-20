from django.utils.translation import gettext_lazy as _

from dcim.choices import LinkStatusChoices
from dcim.models import Interface
from ipam.models import VLAN
from netbox.forms import NetBoxModelImportForm
from tenancy.models import Tenant
from utilities.forms.fields import CSVChoiceField, CSVModelChoiceField, SlugField
from wireless.choices import *
from wireless.models import *

__all__ = (
    'WirelessLANImportForm',
    'WirelessLANGroupImportForm',
    'WirelessLinkImportForm',
)


class WirelessLANGroupImportForm(NetBoxModelImportForm):
    parent = CSVModelChoiceField(
        label=_('Parent'),
        queryset=WirelessLANGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Parent group')
    )
    slug = SlugField()

    class Meta:
        model = WirelessLANGroup
        fields = ('name', 'slug', 'parent', 'description', 'tags')


class WirelessLANImportForm(NetBoxModelImportForm):
    group = CSVModelChoiceField(
        label=_('Group'),
        queryset=WirelessLANGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned group')
    )
    status = CSVChoiceField(
        label=_('Status'),
        choices=WirelessLANStatusChoices,
        help_text=_('Operational status')
    )
    vlan = CSVModelChoiceField(
        label=_('VLAN'),
        queryset=VLAN.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Bridged VLAN')
    )
    tenant = CSVModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )
    auth_type = CSVChoiceField(
        label=_('Authentication type'),
        choices=WirelessAuthTypeChoices,
        required=False,
        help_text=_('Authentication type')
    )
    auth_cipher = CSVChoiceField(
        label=_('Authentication cipher'),
        choices=WirelessAuthCipherChoices,
        required=False,
        help_text=_('Authentication cipher')
    )

    class Meta:
        model = WirelessLAN
        fields = (
            'ssid', 'group', 'status', 'vlan', 'tenant', 'auth_type', 'auth_cipher', 'auth_psk', 'description',
            'comments', 'tags',
        )


class WirelessLinkImportForm(NetBoxModelImportForm):
    status = CSVChoiceField(
        label=_('Status'),
        choices=LinkStatusChoices,
        help_text=_('Connection status')
    )
    interface_a = CSVModelChoiceField(
        label=_('Interface A'),
        queryset=Interface.objects.all()
    )
    interface_b = CSVModelChoiceField(
        label=_('Interface B'),
        queryset=Interface.objects.all()
    )
    tenant = CSVModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )
    auth_type = CSVChoiceField(
        label=_('Authentication type'),
        choices=WirelessAuthTypeChoices,
        required=False,
        help_text=_('Authentication type')
    )
    auth_cipher = CSVChoiceField(
        label=_('Authentication cipher'),
        choices=WirelessAuthCipherChoices,
        required=False,
        help_text=_('Authentication cipher')
    )

    class Meta:
        model = WirelessLink
        fields = (
            'interface_a', 'interface_b', 'ssid', 'tenant', 'auth_type', 'auth_cipher', 'auth_psk', 'description',
            'comments', 'tags',
        )
