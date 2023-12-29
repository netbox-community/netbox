from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from dcim.models import Device, Interface, Site
from ipam.choices import *
from ipam.constants import *
from ipam.models import *
from netbox.forms import NetBoxModelImportForm
from tenancy.models import Tenant
from utilities.forms.fields import (
    CSVChoiceField, CSVContentTypeField, CSVModelChoiceField, CSVModelMultipleChoiceField, SlugField
)
from virtualization.models import VirtualMachine, VMInterface

__all__ = (
    'AggregateImportForm',
    'ASNImportForm',
    'ASNRangeImportForm',
    'FHRPGroupImportForm',
    'IPAddressImportForm',
    'IPRangeImportForm',
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
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )
    import_targets = CSVModelMultipleChoiceField(
        queryset=RouteTarget.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Import route targets')
    )
    export_targets = CSVModelMultipleChoiceField(
        queryset=RouteTarget.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Export route targets')
    )

    class Meta:
        model = VRF
        fields = (
            'name', 'rd', 'tenant', 'enforce_unique', 'description', 'import_targets', 'export_targets', 'comments',
            'tags',
        )


class RouteTargetImportForm(NetBoxModelImportForm):
    tenant = CSVModelChoiceField(
        label=_('Tenant'),
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


class AggregateImportForm(NetBoxModelImportForm):
    rir = CSVModelChoiceField(
        label=_('RIR'),
        queryset=RIR.objects.all(),
        to_field_name='name',
        help_text=_('Assigned RIR')
    )
    tenant = CSVModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )

    class Meta:
        model = Aggregate
        fields = ('prefix', 'rir', 'tenant', 'date_added', 'description', 'comments', 'tags')


class ASNRangeImportForm(NetBoxModelImportForm):
    rir = CSVModelChoiceField(
        label=_('RIR'),
        queryset=RIR.objects.all(),
        to_field_name='name',
        help_text=_('Assigned RIR')
    )
    tenant = CSVModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )

    class Meta:
        model = ASNRange
        fields = ('name', 'slug', 'rir', 'start', 'end', 'tenant', 'description', 'tags')


class ASNImportForm(NetBoxModelImportForm):
    rir = CSVModelChoiceField(
        label=_('RIR'),
        queryset=RIR.objects.all(),
        to_field_name='name',
        help_text=_('Assigned RIR')
    )
    tenant = CSVModelChoiceField(
        label=_('Tenant'),
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
        label=_('VRF'),
        queryset=VRF.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Assigned VRF')
    )
    tenant = CSVModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )
    site = CSVModelChoiceField(
        label=_('Site'),
        queryset=Site.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned site')
    )
    vlan_group = CSVModelChoiceField(
        label=_('VLAN group'),
        queryset=VLANGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_("VLAN's group (if any)")
    )
    vlan = CSVModelChoiceField(
        label=_('VLAN'),
        queryset=VLAN.objects.all(),
        required=False,
        to_field_name='vid',
        help_text=_("Assigned VLAN")
    )
    status = CSVChoiceField(
        label=_('Status'),
        choices=PrefixStatusChoices,
        help_text=_('Operational status')
    )
    role = CSVModelChoiceField(
        label=_('Role'),
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

        if not data:
            return

        site = data.get('site')
        vlan_group = data.get('vlan_group')

        # Limit VLAN queryset by assigned site and/or group (if specified)
        query = Q()

        if site:
            query |= Q(**{
                f"site__{self.fields['site'].to_field_name}": site
            })
            # Don't Forget to include VLANs without a site in the filter
            query |= Q(**{
                f"site__{self.fields['site'].to_field_name}__isnull": True
            })

        if vlan_group:
            query &= Q(**{
                f"group__{self.fields['vlan_group'].to_field_name}": vlan_group
            })

        queryset = self.fields['vlan'].queryset.filter(query)
        self.fields['vlan'].queryset = queryset


class IPRangeImportForm(NetBoxModelImportForm):
    vrf = CSVModelChoiceField(
        label=_('VRF'),
        queryset=VRF.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Assigned VRF')
    )
    tenant = CSVModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )
    status = CSVChoiceField(
        label=_('Status'),
        choices=IPRangeStatusChoices,
        help_text=_('Operational status')
    )
    role = CSVModelChoiceField(
        label=_('Role'),
        queryset=Role.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Functional role')
    )

    class Meta:
        model = IPRange
        fields = (
            'start_address', 'end_address', 'vrf', 'tenant', 'status', 'role', 'mark_utilized', 'description',
            'comments', 'tags',
        )


class IPAddressImportForm(NetBoxModelImportForm):
    vrf = CSVModelChoiceField(
        label=_('VRF'),
        queryset=VRF.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Assigned VRF')
    )
    tenant = CSVModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Assigned tenant')
    )
    status = CSVChoiceField(
        label=_('Status'),
        choices=IPAddressStatusChoices,
        help_text=_('Operational status')
    )
    role = CSVChoiceField(
        label=_('Role'),
        choices=IPAddressRoleChoices,
        required=False,
        help_text=_('Functional role')
    )
    device = CSVModelChoiceField(
        label=_('Device'),
        queryset=Device.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Parent device of assigned interface (if any)')
    )
    virtual_machine = CSVModelChoiceField(
        label=_('Virtual machine'),
        queryset=VirtualMachine.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Parent VM of assigned interface (if any)')
    )
    interface = CSVModelChoiceField(
        label=_('Interface'),
        queryset=Interface.objects.none(),  # Can also refer to VMInterface
        required=False,
        to_field_name='name',
        help_text=_('Assigned interface')
    )
    is_primary = forms.BooleanField(
        label=_('Is primary'),
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
                "is_primary": _("No device or virtual machine specified; cannot set as primary IP")
            })
        if is_primary and not interface:
            raise forms.ValidationError({
                "is_primary": _("No interface specified; cannot set as primary IP")
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
        label=_('Protocol'),
        choices=FHRPGroupProtocolChoices
    )
    auth_type = CSVChoiceField(
        label=_('Auth type'),
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
        label=_('Minimum child VLAN VID (default: {minimum})').format(minimum=VLAN_VID_MIN)
    )
    max_vid = forms.IntegerField(
        min_value=VLAN_VID_MIN,
        max_value=VLAN_VID_MAX,
        required=False,
        label=_('Maximum child VLAN VID (default: {maximum})').format(maximum=VLAN_VID_MIN)
    )

    class Meta:
        model = VLANGroup
        fields = ('name', 'slug', 'scope_type', 'scope_id', 'min_vid', 'max_vid', 'description', 'tags')
        labels = {
            'scope_id': 'Scope ID',
        }


class VLANImportForm(NetBoxModelImportForm):
    site = CSVModelChoiceField(
        label=_('Site'),
        queryset=Site.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned site')
    )
    group = CSVModelChoiceField(
        label=_('Group'),
        queryset=VLANGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned VLAN group')
    )
    tenant = CSVModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Assigned tenant')
    )
    status = CSVChoiceField(
        label=_('Status'),
        choices=VLANStatusChoices,
        help_text=_('Operational status')
    )
    role = CSVModelChoiceField(
        label=_('Role'),
        queryset=Role.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Functional role')
    )

    class Meta:
        model = VLAN
        fields = ('site', 'group', 'vid', 'name', 'tenant', 'status', 'role', 'description', 'comments', 'tags')


class ServiceTemplateImportForm(NetBoxModelImportForm):
    protocol = CSVChoiceField(
        label=_('Protocol'),
        choices=ServiceProtocolChoices,
        help_text=_('IP protocol')
    )

    class Meta:
        model = ServiceTemplate
        fields = ('name', 'protocol', 'ports', 'description', 'comments', 'tags')


class ServiceImportForm(NetBoxModelImportForm):
    device = CSVModelChoiceField(
        label=_('Device'),
        queryset=Device.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Required if not assigned to a VM')
    )
    virtual_machine = CSVModelChoiceField(
        label=_('Virtual machine'),
        queryset=VirtualMachine.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Required if not assigned to a device')
    )
    protocol = CSVChoiceField(
        label=_('Protocol'),
        choices=ServiceProtocolChoices,
        help_text=_('IP protocol')
    )
    ipaddresses = CSVModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        to_field_name='address',
        help_text=_('IP Address'),
    )

    class Meta:
        model = Service
        fields = (
            'device', 'virtual_machine', 'ipaddresses', 'name', 'protocol', 'ports', 'description', 'comments', 'tags',
        )

    def clean_ipaddresses(self):
        parent = self.cleaned_data.get('device') or self.cleaned_data.get('virtual_machine')
        for ip_address in self.cleaned_data['ipaddresses']:
            if not ip_address.assigned_object or getattr(ip_address.assigned_object, 'parent_object') != parent:
                raise forms.ValidationError(
                    _("{ip} is not assigned to this device/VM.").format(ip=ip_address)
                )

        return self.cleaned_data['ipaddresses']
