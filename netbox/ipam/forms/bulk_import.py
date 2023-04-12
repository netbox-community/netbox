from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from dcim.models import Device, Interface, Site
from ipam.choices import *
from ipam.constants import *
from ipam.models import *
from netbox.forms import NetBoxModelImportForm
from tenancy.models import Tenant
from utilities.forms import CSVChoiceField, CSVContentTypeField, CSVModelChoiceField, SlugField
from virtualization.models import VirtualMachine, VMInterface

__all__ = (
    'AggregateImportForm',
    'ASNImportForm',
    'FHRPGroupImportForm',
    'IPAddressImportForm',
    'IPRangeImportForm',
    'L2VPNImportForm',
    'L2VPNTerminationImportForm',
    'PrefixImportForm',
    'RIRImportForm',
    'RoleImportForm',
    'RouteTargetImportForm',
    'ServiceImportForm',
    'ServiceTemplateImportForm',
    'VLANImportForm',
    'VLANGroupImportForm',
    'VRFImportForm',
)


class VRFImportForm(NetBoxModelImportForm):
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )

    class Meta:
        model = VRF
        fields = ('name', 'rd', 'tenant', 'enforce_unique', 'description', 'comments', 'tags')


class RouteTargetImportForm(NetBoxModelImportForm):
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )

    class Meta:
        model = RouteTarget
        fields = ('name', 'tenant', 'description', 'comments', 'tags')


class RIRImportForm(NetBoxModelImportForm):
    slug = SlugField()

    class Meta:
        model = RIR
        fields = ('name', 'slug', 'is_private', 'description', 'tags')
        help_texts = {
            'name': _('RIR name'),
        }


class AggregateImportForm(NetBoxModelImportForm):
    rir = CSVModelChoiceField(
        queryset=RIR.objects.all(),
        to_field_name='name',
        help_text=_('Assigned RIR')
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )

    class Meta:
        model = Aggregate
        fields = ('prefix', 'rir', 'tenant', 'date_added', 'description', 'comments', 'tags')


class ASNImportForm(NetBoxModelImportForm):
    rir = CSVModelChoiceField(
        queryset=RIR.objects.all(),
        to_field_name='name',
        help_text=_('Assigned RIR')
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )

    class Meta:
        model = ASN
        fields = ('asn', 'rir', 'tenant', 'description', 'comments', 'tags')


class RoleImportForm(NetBoxModelImportForm):
    slug = SlugField()

    class Meta:
        model = Role
        fields = ('name', 'slug', 'weight', 'description', 'tags')


class PrefixImportForm(NetBoxModelImportForm):
    vrf = CSVModelChoiceField(
        queryset=VRF.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Assigned VRF')
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned site')
    )
    vlan_group = CSVModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_("VLAN's group (if any)")
    )
    vlan = CSVModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        to_field_name='vid',
        help_text=_("Assigned VLAN")
    )
    status = CSVChoiceField(
        choices=PrefixStatusChoices,
        help_text=_('Operational status')
    )
    role = CSVModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Functional role')
    )

    class Meta:
        model = Prefix
        fields = (
            'prefix', 'vrf', 'tenant', 'site', 'vlan_group', 'vlan', 'status', 'role', 'is_pool', 'mark_utilized',
            'description', 'comments', 'tags',
        )

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit VLAN queryset by assigned site and/or group (if specified)
            params = {}
            if data.get('site'):
                params[f"site__{self.fields['site'].to_field_name}"] = data.get('site')
            if data.get('vlan_group'):
                params[f"group__{self.fields['vlan_group'].to_field_name}"] = data.get('vlan_group')
            if params:
                self.fields['vlan'].queryset = self.fields['vlan'].queryset.filter(**params)


class IPRangeImportForm(NetBoxModelImportForm):
    vrf = CSVModelChoiceField(
        queryset=VRF.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Assigned VRF')
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )
    status = CSVChoiceField(
        choices=IPRangeStatusChoices,
        help_text=_('Operational status')
    )
    role = CSVModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Functional role')
    )

    class Meta:
        model = IPRange
        fields = (
            'start_address', 'end_address', 'vrf', 'tenant', 'status', 'role', 'description', 'comments', 'tags',
        )


class IPAddressImportForm(NetBoxModelImportForm):
    vrf = CSVModelChoiceField(
        queryset=VRF.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Assigned VRF')
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Assigned tenant')
    )
    status = CSVChoiceField(
        choices=IPAddressStatusChoices,
        help_text=_('Operational status')
    )
    role = CSVChoiceField(
        choices=IPAddressRoleChoices,
        required=False,
        help_text=_('Functional role')
    )
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Parent device of assigned interface (if any)')
    )
    virtual_machine = CSVModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Parent VM of assigned interface (if any)')
    )
    interface = CSVModelChoiceField(
        queryset=Interface.objects.none(),  # Can also refer to VMInterface
        required=False,
        to_field_name='name',
        help_text=_('Assigned interface')
    )
    is_primary = forms.BooleanField(
        help_text=_('Make this the primary IP for the assigned device'),
        required=False
    )

    class Meta:
        model = IPAddress
        fields = [
            'address', 'vrf', 'tenant', 'status', 'role', 'device', 'virtual_machine', 'interface', 'is_primary',
            'dns_name', 'description', 'comments', 'tags',
        ]

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit interface queryset by assigned device
            if data.get('device'):
                self.fields['interface'].queryset = Interface.objects.filter(
                    **{f"device__{self.fields['device'].to_field_name}": data['device']}
                )

            # Limit interface queryset by assigned device
            elif data.get('virtual_machine'):
                self.fields['interface'].queryset = VMInterface.objects.filter(
                    **{f"virtual_machine__{self.fields['virtual_machine'].to_field_name}": data['virtual_machine']}
                )

    def clean(self):
        super().clean()

        device = self.cleaned_data.get('device')
        virtual_machine = self.cleaned_data.get('virtual_machine')
        interface = self.cleaned_data.get('interface')
        is_primary = self.cleaned_data.get('is_primary')

        # Validate is_primary
        if is_primary and not device and not virtual_machine:
            raise forms.ValidationError({
                "is_primary": "No device or virtual machine specified; cannot set as primary IP"
            })
        if is_primary and not interface:
            raise forms.ValidationError({
                "is_primary": "No interface specified; cannot set as primary IP"
            })

    def save(self, *args, **kwargs):

        # Set interface assignment
        if self.cleaned_data.get('interface'):
            self.instance.assigned_object = self.cleaned_data['interface']

        ipaddress = super().save(*args, **kwargs)

        # Set as primary for device/VM
        if self.cleaned_data.get('is_primary'):
            parent = self.cleaned_data['device'] or self.cleaned_data['virtual_machine']
            if self.instance.address.version == 4:
                parent.primary_ip4 = ipaddress
            elif self.instance.address.version == 6:
                parent.primary_ip6 = ipaddress
            parent.save()

        return ipaddress


class FHRPGroupImportForm(NetBoxModelImportForm):
    protocol = CSVChoiceField(
        choices=FHRPGroupProtocolChoices
    )
    auth_type = CSVChoiceField(
        choices=FHRPGroupAuthTypeChoices,
        required=False
    )

    class Meta:
        model = FHRPGroup
        fields = ('protocol', 'group_id', 'auth_type', 'auth_key', 'name', 'description', 'comments', 'tags')


class VLANGroupImportForm(NetBoxModelImportForm):
    slug = SlugField()
    scope_type = CSVContentTypeField(
        queryset=ContentType.objects.filter(model__in=VLANGROUP_SCOPE_TYPES),
        required=False,
        label=_('Scope type (app & model)')
    )
    min_vid = forms.IntegerField(
        min_value=VLAN_VID_MIN,
        max_value=VLAN_VID_MAX,
        required=False,
        label=f'Minimum child VLAN VID (default: {VLAN_VID_MIN})'
    )
    max_vid = forms.IntegerField(
        min_value=VLAN_VID_MIN,
        max_value=VLAN_VID_MAX,
        required=False,
        label=f'Maximum child VLAN VID (default: {VLAN_VID_MIN})'
    )

    class Meta:
        model = VLANGroup
        fields = ('name', 'slug', 'scope_type', 'scope_id', 'min_vid', 'max_vid', 'description', 'tags')
        labels = {
            'scope_id': 'Scope ID',
        }


class VLANImportForm(NetBoxModelImportForm):
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned site')
    )
    group = CSVModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned VLAN group')
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Assigned tenant')
    )
    status = CSVChoiceField(
        choices=VLANStatusChoices,
        help_text=_('Operational status')
    )
    role = CSVModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Functional role')
    )

    class Meta:
        model = VLAN
        fields = ('site', 'group', 'vid', 'name', 'tenant', 'status', 'role', 'description', 'comments', 'tags')
        help_texts = {
            'vid': 'Numeric VLAN ID (1-4094)',
            'name': 'VLAN name',
        }


class ServiceTemplateImportForm(NetBoxModelImportForm):
    protocol = CSVChoiceField(
        choices=ServiceProtocolChoices,
        help_text=_('IP protocol')
    )

    class Meta:
        model = ServiceTemplate
        fields = ('name', 'protocol', 'ports', 'description', 'comments', 'tags')


class ServiceImportForm(NetBoxModelImportForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Required if not assigned to a VM')
    )
    virtual_machine = CSVModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Required if not assigned to a device')
    )
    protocol = CSVChoiceField(
        choices=ServiceProtocolChoices,
        help_text=_('IP protocol')
    )

    class Meta:
        model = Service
        fields = ('device', 'virtual_machine', 'name', 'protocol', 'ports', 'description', 'comments', 'tags')


class L2VPNImportForm(NetBoxModelImportForm):
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
    )
    type = CSVChoiceField(
        choices=L2VPNTypeChoices,
        help_text=_('L2VPN type')
    )

    class Meta:
        model = L2VPN
        fields = ('identifier', 'name', 'slug', 'tenant', 'type', 'description',
                  'comments', 'tags')


class L2VPNTerminationImportForm(NetBoxModelImportForm):
    l2vpn = CSVModelChoiceField(
        queryset=L2VPN.objects.all(),
        required=True,
        to_field_name='name',
        label=_('L2VPN'),
    )
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Parent device (for interface)')
    )
    virtual_machine = CSVModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Parent virtual machine (for interface)')
    )
    interface = CSVModelChoiceField(
        queryset=Interface.objects.none(),  # Can also refer to VMInterface
        required=False,
        to_field_name='name',
        help_text=_('Assigned interface (device or VM)')
    )
    vlan = CSVModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned VLAN')
    )

    class Meta:
        model = L2VPNTermination
        fields = ('l2vpn', 'device', 'virtual_machine', 'interface', 'vlan', 'tags')

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit interface queryset by device or VM
            if data.get('device'):
                self.fields['interface'].queryset = Interface.objects.filter(
                    **{f"device__{self.fields['device'].to_field_name}": data['device']}
                )
            elif data.get('virtual_machine'):
                self.fields['interface'].queryset = VMInterface.objects.filter(
                    **{f"virtual_machine__{self.fields['virtual_machine'].to_field_name}": data['virtual_machine']}
                )

    def clean(self):
        super().clean()

        if self.cleaned_data.get('device') and self.cleaned_data.get('virtual_machine'):
            raise ValidationError('Cannot import device and VM interface terminations simultaneously.')
        if not (self.cleaned_data.get('interface') or self.cleaned_data.get('vlan')):
            raise ValidationError('Each termination must specify either an interface or a VLAN.')
        if self.cleaned_data.get('interface') and self.cleaned_data.get('vlan'):
            raise ValidationError('Cannot assign both an interface and a VLAN.')

        self.instance.assigned_object = self.cleaned_data.get('interface') or self.cleaned_data.get('vlan')
