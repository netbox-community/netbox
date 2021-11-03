from django import forms
from django.contrib.contenttypes.models import ContentType

from dcim.models import Device, Interface, Site
from extras.forms import CustomFieldModelCSVForm
from ipam.choices import *
from ipam.constants import *
from ipam.models import *
from tenancy.models import Tenant
from utilities.forms import CSVChoiceField, CSVContentTypeField, CSVModelChoiceField, SlugField
from virtualization.models import VirtualMachine, VMInterface

__all__ = (
    'AggregateCSVForm',
    'ASNCSVForm',
    'FHRPGroupCSVForm',
    'IPAddressCSVForm',
    'IPRangeCSVForm',
    'PrefixCSVForm',
    'RIRCSVForm',
    'RoleCSVForm',
    'RouteTargetCSVForm',
    'ServiceCSVForm',
    'VLANCSVForm',
    'VLANGroupCSVForm',
    'VRFCSVForm',
)


class VRFCSVForm(CustomFieldModelCSVForm):
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned tenant'
    )

    class Meta:
        model = VRF
        fields = ('name', 'rd', 'tenant', 'enforce_unique', 'description')


class RouteTargetCSVForm(CustomFieldModelCSVForm):
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned tenant'
    )

    class Meta:
        model = RouteTarget
        fields = ('name', 'description', 'tenant')


class RIRCSVForm(CustomFieldModelCSVForm):
    slug = SlugField()

    class Meta:
        model = RIR
        fields = ('name', 'slug', 'is_private', 'description')
        help_texts = {
            'name': 'RIR name',
        }


class AggregateCSVForm(CustomFieldModelCSVForm):
    rir = CSVModelChoiceField(
        queryset=RIR.objects.all(),
        to_field_name='name',
        help_text='Assigned RIR'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned tenant'
    )

    class Meta:
        model = Aggregate
        fields = ('prefix', 'rir', 'tenant', 'date_added', 'description')


class ASNCSVForm(CustomFieldModelCSVForm):
    rir = CSVModelChoiceField(
        queryset=RIR.objects.all(),
        to_field_name='name',
        help_text='Assigned RIR'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned tenant'
    )

    class Meta:
        model = ASN
        fields = ('asn', 'rir', 'tenant', 'description')
        help_texts = {}


class RoleCSVForm(CustomFieldModelCSVForm):
    slug = SlugField()

    class Meta:
        model = Role
        fields = ('name', 'slug', 'weight', 'description')


class PrefixCSVForm(CustomFieldModelCSVForm):
    vrf = CSVModelChoiceField(
        queryset=VRF.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Assigned VRF'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned tenant'
    )
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned site'
    )
    vlan_group = CSVModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text="VLAN's group (if any)"
    )
    vlan = CSVModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        to_field_name='vid',
        help_text="Assigned VLAN"
    )
    status = CSVChoiceField(
        choices=PrefixStatusChoices,
        help_text='Operational status'
    )
    role = CSVModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Functional role'
    )

    class Meta:
        model = Prefix
        fields = (
            'prefix', 'vrf', 'tenant', 'site', 'vlan_group', 'vlan', 'status', 'role', 'is_pool', 'mark_utilized',
            'description',
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


class IPRangeCSVForm(CustomFieldModelCSVForm):
    vrf = CSVModelChoiceField(
        queryset=VRF.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Assigned VRF'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned tenant'
    )
    status = CSVChoiceField(
        choices=IPRangeStatusChoices,
        help_text='Operational status'
    )
    role = CSVModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Functional role'
    )

    class Meta:
        model = IPRange
        fields = (
            'start_address', 'end_address', 'vrf', 'tenant', 'status', 'role', 'description',
        )


class IPAddressCSVForm(CustomFieldModelCSVForm):
    vrf = CSVModelChoiceField(
        queryset=VRF.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Assigned VRF'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Assigned tenant'
    )
    status = CSVChoiceField(
        choices=IPAddressStatusChoices,
        help_text='Operational status'
    )
    role = CSVChoiceField(
        choices=IPAddressRoleChoices,
        required=False,
        help_text='Functional role'
    )
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Parent device of assigned interface (if any)'
    )
    virtual_machine = CSVModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Parent VM of assigned interface (if any)'
    )
    interface = CSVModelChoiceField(
        queryset=Interface.objects.none(),  # Can also refer to VMInterface
        required=False,
        to_field_name='name',
        help_text='Assigned interface'
    )
    is_primary = forms.BooleanField(
        help_text='Make this the primary IP for the assigned device',
        required=False
    )

    class Meta:
        model = IPAddress
        fields = [
            'address', 'vrf', 'tenant', 'status', 'role', 'device', 'virtual_machine', 'interface', 'is_primary',
            'dns_name', 'description',
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
        if self.cleaned_data['interface']:
            self.instance.assigned_object = self.cleaned_data['interface']

        ipaddress = super().save(*args, **kwargs)

        # Set as primary for device/VM
        if self.cleaned_data['is_primary']:
            parent = self.cleaned_data['device'] or self.cleaned_data['virtual_machine']
            if self.instance.address.version == 4:
                parent.primary_ip4 = ipaddress
            elif self.instance.address.version == 6:
                parent.primary_ip6 = ipaddress
            parent.save()

        return ipaddress


class FHRPGroupCSVForm(CustomFieldModelCSVForm):
    protocol = CSVChoiceField(
        choices=FHRPGroupProtocolChoices
    )
    auth_type = CSVChoiceField(
        choices=FHRPGroupAuthTypeChoices,
        required=False
    )

    class Meta:
        model = FHRPGroup
        fields = ('protocol', 'group_id', 'auth_type', 'auth_key', 'description')


class VLANGroupCSVForm(CustomFieldModelCSVForm):
    slug = SlugField()
    scope_type = CSVContentTypeField(
        queryset=ContentType.objects.filter(model__in=VLANGROUP_SCOPE_TYPES),
        required=False,
        label='Scope type (app & model)'
    )

    class Meta:
        model = VLANGroup
        fields = ('name', 'slug', 'scope_type', 'scope_id', 'description')
        labels = {
            'scope_id': 'Scope ID',
        }


class VLANCSVForm(CustomFieldModelCSVForm):
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned site'
    )
    group = CSVModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned VLAN group'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Assigned tenant'
    )
    status = CSVChoiceField(
        choices=VLANStatusChoices,
        help_text='Operational status'
    )
    role = CSVModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Functional role'
    )

    class Meta:
        model = VLAN
        fields = ('site', 'group', 'vid', 'name', 'tenant', 'status', 'role', 'description')
        help_texts = {
            'vid': 'Numeric VLAN ID (1-4095)',
            'name': 'VLAN name',
        }


class ServiceCSVForm(CustomFieldModelCSVForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Required if not assigned to a VM'
    )
    virtual_machine = CSVModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Required if not assigned to a device'
    )
    protocol = CSVChoiceField(
        choices=ServiceProtocolChoices,
        help_text='IP protocol'
    )

    class Meta:
        model = Service
        fields = ('device', 'virtual_machine', 'name', 'protocol', 'ports', 'description')
