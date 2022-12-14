from django.utils.translation import gettext as _
from dcim.choices import LinkStatusChoices
from dcim.models import Interface
from ipam.models import VLAN
from netbox.forms import NetBoxModelImportForm
from tenancy.models import Tenant
from utilities.forms import CSVChoiceField, CSVModelChoiceField, SlugField
from wireless.choices import *
from wireless.models import *

__all__ = (
    'WirelessLANImportForm',
    'WirelessLANGroupImportForm',
    'WirelessLinkImportForm',
)


class WirelessLANGroupImportForm(NetBoxModelImportForm):
    parent = CSVModelChoiceField(
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
        queryset=WirelessLANGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned group')
    )
    status = CSVChoiceField(
        choices=WirelessLANStatusChoices,
        help_text='Operational status'
    )
    vlan = CSVModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Bridged VLAN')
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )
    auth_type = CSVChoiceField(
        choices=WirelessAuthTypeChoices,
        required=False,
        help_text=_('Authentication type')
    )
    auth_cipher = CSVChoiceField(
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
        choices=LinkStatusChoices,
        help_text=_('Connection status')
    )
    interface_a = CSVModelChoiceField(
        queryset=Interface.objects.all()
    )
    interface_b = CSVModelChoiceField(
        queryset=Interface.objects.all()
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )
    auth_type = CSVChoiceField(
        choices=WirelessAuthTypeChoices,
        required=False,
        help_text=_('Authentication type')
    )
    auth_cipher = CSVChoiceField(
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
