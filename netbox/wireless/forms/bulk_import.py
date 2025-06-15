from django.utils.translation import gettext_lazy as _

from dcim.choices import LinkStatusChoices
from dcim.forms.mixins import ScopedImportForm
from dcim.models import Device, Interface, Site
from ipam.models import VLAN
from netbox.choices import *
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
        fields = ('name', 'slug', 'parent', 'description', 'tags', 'comments')


class WirelessLANImportForm(ScopedImportForm, NetBoxModelImportForm):
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
            'ssid', 'group', 'status', 'vlan', 'tenant', 'auth_type', 'auth_cipher', 'auth_psk', 'scope_type',
            'scope_id', 'description', 'comments', 'tags',
        )
        labels = {
            'scope_id': _('Scope ID'),
        }


class WirelessLinkImportForm(NetBoxModelImportForm):
    # Termination A
    site_a = CSVModelChoiceField(
        label=_('Site A'),
        queryset=Site.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Site of parent device A (if any)'),
    )
    device_a = CSVModelChoiceField(
        label=_('Device A'),
        queryset=Device.objects.all(),
        to_field_name='name',
        help_text=_('Parent device of assigned interface A'),
    )
    interface_a = CSVModelChoiceField(
        label=_('Interface A'),
        queryset=Interface.objects.all(),
        to_field_name='name',
        help_text=_('Assigned interface A'),
    )

    # Termination B
    site_b = CSVModelChoiceField(
        label=_('Site B'),
        queryset=Site.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Site of parent device B (if any)'),
    )
    device_b = CSVModelChoiceField(
        label=_('Device B'),
        queryset=Device.objects.all(),
        to_field_name='name',
        help_text=_('Parent device of assigned interface B'),
    )
    interface_b = CSVModelChoiceField(
        label=_('Interface B'),
        queryset=Interface.objects.all(),
        to_field_name='name',
        help_text=_('Assigned interface B'),
    )

    # WirelessLink attributes
    status = CSVChoiceField(
        label=_('Status'),
        choices=LinkStatusChoices,
        help_text=_('Connection status'),
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
    distance_unit = CSVChoiceField(
        label=_('Distance unit'),
        choices=DistanceUnitChoices,
        required=False,
        help_text=_('Distance unit')
    )

    class Meta:
        model = WirelessLink
        fields = (
            'site_a', 'device_a', 'interface_a', 'site_b', 'device_b', 'interface_b', 'status', 'ssid', 'tenant',
            'auth_type', 'auth_cipher', 'auth_psk', 'distance', 'distance_unit', 'description', 'comments', 'tags',
        )

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:
            # Limit choices for interface_a to the assigned device_a
            interface_a_params = {f'device__{self.fields["device_a"].to_field_name}': data.get('device_a')}
            # Limit choices for device_a to the assigned site_a
            if site_a := data.get('site_a'):
                device_a_params = {f'site__{self.fields["site_a"].to_field_name}': site_a}
                self.fields['device_a'].queryset = self.fields['device_a'].queryset.filter(**device_a_params)
                interface_a_params.update({f'device__site__{self.fields["site_a"].to_field_name}': site_a})
            self.fields['interface_a'].queryset = self.fields['interface_a'].queryset.filter(**interface_a_params)

            # Limit choices for interface_b to the assigned device_b
            interface_b_params = {f'device__{self.fields["device_b"].to_field_name}': data.get('device_b')}
            # Limit choices for device_b to the assigned site_b
            if site_b := data.get('site_b'):
                device_b_params = {f'site__{self.fields["site_b"].to_field_name}': site_b}
                self.fields['device_b'].queryset = self.fields['device_b'].queryset.filter(**device_b_params)
                interface_b_params.update({f'device__site__{self.fields["site_b"].to_field_name}': site_b})
            self.fields['interface_b'].queryset = self.fields['interface_b'].queryset.filter(**interface_b_params)
