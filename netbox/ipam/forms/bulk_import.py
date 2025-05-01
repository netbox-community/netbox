from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from dcim.models import Device, Interface, Site
from dcim.forms.mixins import ScopedImportForm
from ipam.choices import *
from ipam.constants import *
from ipam.models import *
from netbox.forms import NetBoxModelImportForm
from tenancy.models import Tenant
from utilities.forms.fields import (
    CSVChoiceField, CSVContentTypeField, CSVModelChoiceField, CSVModelMultipleChoiceField, SlugField,
    NumericRangeArrayField,
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
    'VLANTranslationPolicyImportForm',
    'VLANTranslationRuleImportForm',
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


class PrefixImportForm(ScopedImportForm, NetBoxModelImportForm):
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
    vlan_group = CSVModelChoiceField(
        label=_('VLAN group'),
        queryset=VLANGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_("VLAN's group (if any)")
    )
    vlan_site = CSVModelChoiceField(
        label=_('VLAN Site'),
        queryset=Site.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_("VLAN's site (if any)")
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
            'prefix', 'vrf', 'tenant', 'vlan_group', 'vlan_site', 'vlan', 'status', 'role', 'scope_type', 'scope_id',
            'is_pool', 'mark_utilized', 'description', 'comments', 'tags',
        )
        labels = {
            'scope_id': _('Scope ID'),
        }

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if not data:
            return

        vlan_site = data.get('vlan_site')
        vlan_group = data.get('vlan_group')

        # Limit VLAN queryset by assigned site and/or group (if specified)
        query = Q()

        if vlan_site:
            query |= Q(**{
                f"site__{self.fields['vlan_site'].to_field_name}": vlan_site
            })
            # Don't Forget to include VLANs without a site in the filter
            query |= Q(**{
                f"site__{self.fields['vlan_site'].to_field_name}__isnull": True
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
            'start_address', 'end_address', 'vrf', 'tenant', 'status', 'role', 'mark_populated', 'mark_utilized',
            'description', 'comments', 'tags',
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
    fhrp_group = CSVModelChoiceField(
        label=_('FHRP Group'),
        queryset=FHRPGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned FHRP Group name')
    )
    is_primary = forms.BooleanField(
        label=_('Is primary'),
        help_text=_('Make this the primary IP for the assigned device'),
        required=False
    )
    is_oob = forms.BooleanField(
        label=_('Is out-of-band'),
        help_text=_('Designate this as the out-of-band IP address for the assigned device'),
        required=False
    )

    class Meta:
        model = IPAddress
        fields = [
            'address', 'vrf', 'tenant', 'status', 'role', 'device', 'virtual_machine', 'interface', 'fhrp_group',
            'is_primary', 'is_oob', 'dns_name', 'description', 'comments', 'tags',
        ]

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit interface queryset by assigned device
            if data.get('device'):
                self.fields['interface'].queryset = Interface.objects.filter(
                    **{f"device__{self.fields['device'].to_field_name}": data['device']}
                )

            # Limit interface queryset by assigned VM
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
        is_oob = self.cleaned_data.get('is_oob')

        # Validate is_primary and is_oob
        if is_primary and not device and not virtual_machine:
            raise forms.ValidationError({
                "is_primary": _("No device or virtual machine specified; cannot set as primary IP")
            })
        if is_oob and not device:
            raise forms.ValidationError({
                "is_oob": _("No device specified; cannot set as out-of-band IP")
            })
        if is_oob and virtual_machine:
            raise forms.ValidationError({
                "is_oob": _("Cannot set out-of-band IP for virtual machines")
            })
        if is_primary and not interface:
            raise forms.ValidationError({
                "is_primary": _("No interface specified; cannot set as primary IP")
            })
        if is_oob and not interface:
            raise forms.ValidationError({
                "is_oob": _("No interface specified; cannot set as out-of-band IP")
            })

    def save(self, *args, **kwargs):

        # Set interface assignment
        if self.cleaned_data.get('interface'):
            self.instance.assigned_object = self.cleaned_data['interface']
        if self.cleaned_data.get('fhrp_group'):
            self.instance.assigned_object = self.cleaned_data['fhrp_group']

        ipaddress = super().save(*args, **kwargs)

        # Set as primary for device/VM
        if self.cleaned_data.get('is_primary'):
            parent = self.cleaned_data.get('device') or self.cleaned_data.get('virtual_machine')
            if self.instance.address.version == 4:
                parent.primary_ip4 = ipaddress
            elif self.instance.address.version == 6:
                parent.primary_ip6 = ipaddress
            parent.save()

        # Set as OOB for device
        if self.cleaned_data.get('is_oob'):
            parent = self.cleaned_data.get('device')
            parent.oob_ip = ipaddress
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
    vid_ranges = NumericRangeArrayField(
        required=False
    )
    tenant = CSVModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )

    class Meta:
        model = VLANGroup
        fields = ('name', 'slug', 'scope_type', 'scope_id', 'vid_ranges', 'tenant', 'description', 'tags')
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
    qinq_role = CSVChoiceField(
        label=_('Q-in-Q role'),
        choices=VLANQinQRoleChoices,
        required=False,
        help_text=_('Operational status')
    )
    qinq_svlan = CSVModelChoiceField(
        label=_('Q-in-Q SVLAN'),
        queryset=VLAN.objects.all(),
        required=False,
        to_field_name='vid',
        help_text=_("Service VLAN (for Q-in-Q/802.1ad customer VLANs)")
    )

    class Meta:
        model = VLAN
        fields = (
            'site', 'group', 'vid', 'name', 'tenant', 'status', 'role', 'description', 'qinq_role', 'qinq_svlan',
            'comments', 'tags',
        )


class VLANTranslationPolicyImportForm(NetBoxModelImportForm):

    class Meta:
        model = VLANTranslationPolicy
        fields = ('name', 'description', 'tags')


class VLANTranslationRuleImportForm(NetBoxModelImportForm):
    policy = CSVModelChoiceField(
        label=_('Policy'),
        queryset=VLANTranslationPolicy.objects.all(),
        to_field_name='name',
        help_text=_('VLAN translation policy')
    )

    class Meta:
        model = VLANTranslationRule
        fields = ('policy', 'local_vid', 'remote_vid')


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
    parent_object_type = CSVContentTypeField(
        queryset=ContentType.objects.filter(SERVICE_ASSIGNMENT_MODELS),
        required=True,
        label=_('Parent type (app & model)')
    )
    parent = CSVModelChoiceField(
        label=_('Parent'),
        queryset=Device.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Parent object name')
    )
    parent_object_id = forms.IntegerField(
        required=False,
        help_text=_('Parent object ID'),
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
            'ipaddresses', 'name', 'protocol', 'ports', 'description', 'comments', 'tags',
        )

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        # Limit parent queryset by assigned parent object type
        if data:
            match data.get('parent_object_type'):
                case 'dcim.device':
                    self.fields['parent'].queryset = Device.objects.all()
                case 'ipam.fhrpgroup':
                    self.fields['parent'].queryset = FHRPGroup.objects.all()
                case 'virtualization.virtualmachine':
                    self.fields['parent'].queryset = VirtualMachine.objects.all()

    def save(self, *args, **kwargs):
        if (parent := self.cleaned_data.get('parent')):
            self.instance.parent = parent

        return super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        if (parent_ct := self.cleaned_data.get('parent_object_type')):
            if (parent := self.cleaned_data.get('parent')):
                self.cleaned_data['parent_object_id'] = parent.pk
            elif (parent_id := self.cleaned_data.get('parent_object_id')):
                parent = parent_ct.model_class().objects.filter(id=parent_id).first()
                self.cleaned_data['parent'] = parent
            else:
                # If a parent object type is passed and we've made it here, then raise a validation
                # error since an associated parent object or parent object id has not been passed
                raise forms.ValidationError(
                    _("One of parent or parent_object_id must be included with parent_object_type")
                )

        # making sure parent is defined. In cases where an import is resulting in an update, the
        # import data might not include the parent object and so the above logic might not be
        # triggered
        parent = self.cleaned_data.get('parent')
        for ip_address in self.cleaned_data.get('ipaddresses', []):
            if not ip_address.assigned_object or getattr(ip_address.assigned_object, 'parent_object') != parent:
                raise forms.ValidationError(
                    _("{ip} is not assigned to this parent.").format(ip=ip_address)
                )

        return self.cleaned_data
