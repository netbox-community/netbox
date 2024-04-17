from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from dcim.models import Device, Interface, Location, Rack, Region, Site, SiteGroup
from ipam.choices import *
from ipam.constants import *
from ipam.formfields import IPNetworkFormField
from ipam.models import *
from netbox.forms import NetBoxModelForm
from tenancy.forms import TenancyForm
from utilities.exceptions import PermissionsViolation
from utilities.forms import BootstrapMixin, add_blank_choice
from utilities.forms.fields import (
    CommentField, ContentTypeChoiceField, DynamicModelChoiceField, DynamicModelMultipleChoiceField, NumericArrayField,
    SlugField,
)
from utilities.forms.widgets import DatePicker
from virtualization.models import Cluster, ClusterGroup, VirtualMachine, VMInterface

__all__ = (
    'AggregateForm',
    'ASNForm',
    'ASNRangeForm',
    'FHRPGroupForm',
    'FHRPGroupAssignmentForm',
    'IPAddressAssignForm',
    'IPAddressBulkAddForm',
    'IPAddressForm',
    'IPRangeForm',
    'PrefixForm',
    'RIRForm',
    'RoleForm',
    'RouteTargetForm',
    'ServiceForm',
    'ServiceCreateForm',
    'ServiceTemplateForm',
    'VLANForm',
    'VLANGroupForm',
    'VRFForm',
)


class VRFForm(TenancyForm, NetBoxModelForm):
    import_targets = DynamicModelMultipleChoiceField(
        label=_('Import targets'),
        queryset=RouteTarget.objects.all(),
        required=False
    )
    export_targets = DynamicModelMultipleChoiceField(
        label=_('Export targets'),
        queryset=RouteTarget.objects.all(),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        (_('VRF'), ('name', 'rd', 'enforce_unique', 'description', 'tags')),
        (_('Route Targets'), ('import_targets', 'export_targets')),
        (_('Tenancy'), ('tenant_group', 'tenant')),
    )

    class Meta:
        model = VRF
        fields = [
            'name', 'rd', 'enforce_unique', 'import_targets', 'export_targets', 'tenant_group', 'tenant', 'description',
            'comments', 'tags',
        ]
        labels = {
            'rd': "RD",
        }


class RouteTargetForm(TenancyForm, NetBoxModelForm):
    fieldsets = (
        ('Route Target', ('name', 'description', 'tags')),
        ('Tenancy', ('tenant_group', 'tenant')),
    )
    comments = CommentField()

    class Meta:
        model = RouteTarget
        fields = [
            'name', 'tenant_group', 'tenant', 'description', 'comments', 'tags',
        ]


class RIRForm(NetBoxModelForm):
    slug = SlugField()

    fieldsets = (
        (_('RIR'), (
            'name', 'slug', 'is_private', 'description', 'tags',
        )),
    )

    class Meta:
        model = RIR
        fields = [
            'name', 'slug', 'is_private', 'description', 'tags',
        ]


class AggregateForm(TenancyForm, NetBoxModelForm):
    rir = DynamicModelChoiceField(
        queryset=RIR.objects.all(),
        label=_('RIR')
    )
    comments = CommentField()

    fieldsets = (
        (_('Aggregate'), ('prefix', 'rir', 'date_added', 'description', 'tags')),
        (_('Tenancy'), ('tenant_group', 'tenant')),
    )

    class Meta:
        model = Aggregate
        fields = [
            'prefix', 'rir', 'date_added', 'tenant_group', 'tenant', 'description', 'comments', 'tags',
        ]
        widgets = {
            'date_added': DatePicker(),
        }


class ASNRangeForm(TenancyForm, NetBoxModelForm):
    rir = DynamicModelChoiceField(
        queryset=RIR.objects.all(),
        label=_('RIR'),
    )
    slug = SlugField()
    fieldsets = (
        (_('ASN Range'), ('name', 'slug', 'rir', 'start', 'end', 'description', 'tags')),
        (_('Tenancy'), ('tenant_group', 'tenant')),
    )

    class Meta:
        model = ASNRange
        fields = [
            'name', 'slug', 'rir', 'start', 'end', 'tenant_group', 'tenant', 'description', 'tags'
        ]


class ASNForm(TenancyForm, NetBoxModelForm):
    rir = DynamicModelChoiceField(
        queryset=RIR.objects.all(),
        label=_('RIR'),
    )
    sites = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        label=_('Sites'),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        (_('ASN'), ('asn', 'rir', 'sites', 'description', 'tags')),
        (_('Tenancy'), ('tenant_group', 'tenant')),
    )

    class Meta:
        model = ASN
        fields = [
            'asn', 'rir', 'sites', 'tenant_group', 'tenant', 'description', 'comments', 'tags'
        ]
        widgets = {
            'date_added': DatePicker(),
        }

    def __init__(self, data=None, instance=None, *args, **kwargs):
        super().__init__(data=data, instance=instance, *args, **kwargs)

        if self.instance and self.instance.pk is not None:
            self.fields['sites'].initial = self.instance.sites.all().values_list('id', flat=True)

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        instance.sites.set(self.cleaned_data['sites'])
        return instance


class RoleForm(NetBoxModelForm):
    slug = SlugField()

    fieldsets = (
        (_('Role'), (
            'name', 'slug', 'weight', 'description', 'tags',
        )),
    )

    class Meta:
        model = Role
        fields = [
            'name', 'slug', 'weight', 'description', 'tags',
        ]


class PrefixForm(TenancyForm, NetBoxModelForm):
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('VRF')
    )
    site = DynamicModelChoiceField(
        label=_('Site'),
        queryset=Site.objects.all(),
        required=False,
        selector=True,
        null_option='None'
    )
    vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        selector=True,
        query_params={
            'available_at_site': '$site',
        },
        label=_('VLAN'),
    )
    role = DynamicModelChoiceField(
        label=_('Role'),
        queryset=Role.objects.all(),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        (_('Prefix'), ('prefix', 'status', 'vrf', 'role', 'is_pool', 'mark_utilized', 'description', 'tags')),
        (_('Site/VLAN Assignment'), ('site', 'vlan')),
        (_('Tenancy'), ('tenant_group', 'tenant')),
    )

    class Meta:
        model = Prefix
        fields = [
            'prefix', 'vrf', 'site', 'vlan', 'status', 'role', 'is_pool', 'mark_utilized', 'tenant_group', 'tenant',
            'description', 'comments', 'tags',
        ]


class IPRangeForm(TenancyForm, NetBoxModelForm):
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('VRF')
    )
    role = DynamicModelChoiceField(
        label=_('Role'),
        queryset=Role.objects.all(),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        (_('IP Range'), ('vrf', 'start_address', 'end_address', 'role', 'status', 'mark_utilized', 'description', 'tags')),
        (_('Tenancy'), ('tenant_group', 'tenant')),
    )

    class Meta:
        model = IPRange
        fields = [
            'vrf', 'start_address', 'end_address', 'status', 'role', 'tenant_group', 'tenant', 'mark_utilized',
            'description', 'comments', 'tags',
        ]


class IPAddressForm(TenancyForm, NetBoxModelForm):
    interface = DynamicModelChoiceField(
        label=_('Interface'),
        queryset=Interface.objects.all(),
        required=False,
        selector=True,
    )
    vminterface = DynamicModelChoiceField(
        queryset=VMInterface.objects.all(),
        required=False,
        selector=True,
        label=_('Interface'),
    )
    fhrpgroup = DynamicModelChoiceField(
        queryset=FHRPGroup.objects.all(),
        required=False,
        selector=True,
        label=_('FHRP Group')
    )
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('VRF')
    )
    nat_inside = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        selector=True,
        label=_('IP Address'),
    )
    primary_for_parent = forms.BooleanField(
        required=False,
        label=_('Make this the primary IP for the device/VM')
    )
    comments = CommentField()

    class Meta:
        model = IPAddress
        fields = [
            'address', 'vrf', 'status', 'role', 'dns_name', 'primary_for_parent', 'nat_inside', 'tenant_group',
            'tenant', 'description', 'comments', 'tags',
        ]

    def __init__(self, *args, **kwargs):

        # Initialize helper selectors
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {}).copy()
        if instance:
            if type(instance.assigned_object) is Interface:
                initial['interface'] = instance.assigned_object
            elif type(instance.assigned_object) is VMInterface:
                initial['vminterface'] = instance.assigned_object
            elif type(instance.assigned_object) is FHRPGroup:
                initial['fhrpgroup'] = instance.assigned_object
        kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

        # Initialize primary_for_parent if IP address is already assigned
        if self.instance.pk and self.instance.assigned_object:
            parent = getattr(self.instance.assigned_object, 'parent_object', None)
            if parent and (
                self.instance.address.version == 4 and parent.primary_ip4_id == self.instance.pk or
                self.instance.address.version == 6 and parent.primary_ip6_id == self.instance.pk
            ):
                self.initial['primary_for_parent'] = True

        # Disable object assignment fields if the IP address is designated as primary
        if self.initial.get('primary_for_parent'):
            self.fields['interface'].disabled = True
            self.fields['vminterface'].disabled = True
            self.fields['fhrpgroup'].disabled = True

    def clean(self):
        super().clean()

        # Handle object assignment
        selected_objects = [
            field for field in ('interface', 'vminterface', 'fhrpgroup') if self.cleaned_data[field]
        ]
        if len(selected_objects) > 1:
            raise forms.ValidationError({
                selected_objects[1]: _("An IP address can only be assigned to a single object.")
            })
        elif selected_objects:
            assigned_object = self.cleaned_data[selected_objects[0]]
            if self.instance.pk and self.instance.assigned_object and self.cleaned_data['primary_for_parent'] and assigned_object != self.instance.assigned_object:
                raise ValidationError(
                    _("Cannot reassign IP address while it is designated as the primary IP for the parent object")
                )
            self.instance.assigned_object = assigned_object
        else:
            self.instance.assigned_object = None

        # Primary IP assignment is only available if an interface has been assigned.
        interface = self.cleaned_data.get('interface') or self.cleaned_data.get('vminterface')
        if self.cleaned_data.get('primary_for_parent') and not interface:
            self.add_error(
                'primary_for_parent', _("Only IP addresses assigned to an interface can be designated as primary IPs.")
            )

    def save(self, *args, **kwargs):
        ipaddress = super().save(*args, **kwargs)

        # Assign/clear this IPAddress as the primary for the associated Device/VirtualMachine.
        interface = self.instance.assigned_object
        if type(interface) in (Interface, VMInterface):
            parent = interface.parent_object
            parent.snapshot()
            if self.cleaned_data['primary_for_parent']:
                if ipaddress.address.version == 4:
                    parent.primary_ip4 = ipaddress
                else:
                    parent.primary_ip6 = ipaddress
                parent.save()
            elif ipaddress.address.version == 4 and parent.primary_ip4 == ipaddress:
                parent.primary_ip4 = None
                parent.save()
            elif ipaddress.address.version == 6 and parent.primary_ip6 == ipaddress:
                parent.primary_ip6 = None
                parent.save()

        return ipaddress


class IPAddressBulkAddForm(TenancyForm, NetBoxModelForm):
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('VRF')
    )

    class Meta:
        model = IPAddress
        fields = [
            'address', 'vrf', 'status', 'role', 'dns_name', 'description', 'tenant_group', 'tenant', 'tags',
        ]


class IPAddressAssignForm(BootstrapMixin, forms.Form):
    vrf_id = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('VRF')
    )
    q = forms.CharField(
        required=False,
        label=_('Search'),
    )


class FHRPGroupForm(NetBoxModelForm):

    # Optionally create a new IPAddress along with the FHRPGroup
    ip_vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('VRF')
    )
    ip_address = IPNetworkFormField(
        required=False,
        label=_('Address')
    )
    ip_status = forms.ChoiceField(
        choices=add_blank_choice(IPAddressStatusChoices),
        required=False,
        label=_('Status')
    )
    comments = CommentField()

    fieldsets = (
        (_('FHRP Group'), ('protocol', 'group_id', 'name', 'description', 'tags')),
        (_('Authentication'), ('auth_type', 'auth_key')),
        (_('Virtual IP Address'), ('ip_vrf', 'ip_address', 'ip_status'))
    )

    class Meta:
        model = FHRPGroup
        fields = (
            'protocol', 'group_id', 'auth_type', 'auth_key', 'name', 'ip_vrf', 'ip_address', 'ip_status', 'description',
            'comments', 'tags',
        )

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        user = getattr(instance, '_user', None)  # Set under FHRPGroupEditView.alter_object()

        # Check if we need to create a new IPAddress for the group
        if self.cleaned_data.get('ip_address'):
            ipaddress = IPAddress(
                vrf=self.cleaned_data['ip_vrf'],
                address=self.cleaned_data['ip_address'],
                status=self.cleaned_data['ip_status'],
                role=FHRP_PROTOCOL_ROLE_MAPPINGS.get(self.cleaned_data['protocol'], IPAddressRoleChoices.ROLE_VIP),
                assigned_object=instance
            )
            ipaddress.populate_custom_field_defaults()
            ipaddress.save()

            # Check that the new IPAddress conforms with any assigned object-level permissions
            if not IPAddress.objects.restrict(user, 'add').filter(pk=ipaddress.pk).first():
                raise PermissionsViolation()

        return instance

    def clean(self):
        super().clean()

        ip_vrf = self.cleaned_data.get('ip_vrf')
        ip_address = self.cleaned_data.get('ip_address')
        ip_status = self.cleaned_data.get('ip_status')

        if ip_address:
            ip_form = IPAddressForm({
                'address': ip_address,
                'vrf': ip_vrf,
                'status': ip_status,
            })
            if not ip_form.is_valid():
                self.errors.update({
                    f'ip_{field}': error for field, error in ip_form.errors.items()
                })


class FHRPGroupAssignmentForm(BootstrapMixin, forms.ModelForm):
    group = DynamicModelChoiceField(
        label=_('Group'),
        queryset=FHRPGroup.objects.all()
    )

    class Meta:
        model = FHRPGroupAssignment
        fields = ('group', 'priority')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ipaddresses = self.instance.interface.ip_addresses.all()
        for ipaddress in ipaddresses:
            self.fields['group'].widget.add_query_param('related_ip', ipaddress.pk)

    def clean_group(self):
        group = self.cleaned_data['group']

        conflicting_assignments = FHRPGroupAssignment.objects.filter(
            interface_type=self.instance.interface_type,
            interface_id=self.instance.interface_id,
            group=group
        )
        if self.instance.id:
            conflicting_assignments = conflicting_assignments.exclude(id=self.instance.id)

        if conflicting_assignments.exists():
            raise forms.ValidationError(
                _('Assignment already exists')
            )

        return group


class VLANGroupForm(NetBoxModelForm):
    scope_type = ContentTypeChoiceField(
        label=_('Scope type'),
        queryset=ContentType.objects.filter(model__in=VLANGROUP_SCOPE_TYPES),
        required=False
    )
    region = DynamicModelChoiceField(
        label=_('Region'),
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    sitegroup = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        },
        label=_('Site group')
    )
    site = DynamicModelChoiceField(
        label=_('Site'),
        queryset=Site.objects.all(),
        required=False,
        initial_params={
            'locations': '$location'
        },
        query_params={
            'region_id': '$region',
            'group_id': '$sitegroup',
        }
    )
    location = DynamicModelChoiceField(
        label=_('Location'),
        queryset=Location.objects.all(),
        required=False,
        initial_params={
            'racks': '$rack'
        },
        query_params={
            'site_id': '$site',
        }
    )
    rack = DynamicModelChoiceField(
        label=_('Rack'),
        queryset=Rack.objects.all(),
        required=False,
        query_params={
            'site_id': '$site',
            'location_id': '$location',
        }
    )
    clustergroup = DynamicModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        initial_params={
            'clusters': '$cluster'
        },
        label=_('Cluster group')
    )
    cluster = DynamicModelChoiceField(
        label=_('Cluster'),
        queryset=Cluster.objects.all(),
        required=False,
        query_params={
            'group_id': '$clustergroup',
        }
    )
    slug = SlugField()

    fieldsets = (
        (_('VLAN Group'), ('name', 'slug', 'description', 'tags')),
        (_('Child VLANs'), ('min_vid', 'max_vid')),
        (_('Scope'), ('scope_type', 'region', 'sitegroup', 'site', 'location', 'rack', 'clustergroup', 'cluster')),
    )

    class Meta:
        model = VLANGroup
        fields = [
            'name', 'slug', 'description', 'scope_type', 'region', 'sitegroup', 'site', 'location', 'rack',
            'clustergroup', 'cluster', 'min_vid', 'max_vid', 'tags',
        ]

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {})

        if instance is not None and instance.scope:
            initial[instance.scope_type.model] = instance.scope

            kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()

        # Assign scope based on scope_type
        if self.cleaned_data.get('scope_type'):
            scope_field = self.cleaned_data['scope_type'].model
            self.instance.scope = self.cleaned_data.get(scope_field)
        else:
            self.instance.scope_id = None


class VLANForm(TenancyForm, NetBoxModelForm):
    group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        selector=True,
        label=_('VLAN Group')
    )
    site = DynamicModelChoiceField(
        label=_('Site'),
        queryset=Site.objects.all(),
        required=False,
        null_option='None',
        selector=True
    )
    role = DynamicModelChoiceField(
        label=_('Role'),
        queryset=Role.objects.all(),
        required=False
    )
    comments = CommentField()

    class Meta:
        model = VLAN
        fields = [
            'site', 'group', 'vid', 'name', 'status', 'role', 'tenant_group', 'tenant', 'description', 'comments',
            'tags',
        ]


class ServiceTemplateForm(NetBoxModelForm):
    ports = NumericArrayField(
        label=_('Ports'),
        base_field=forms.IntegerField(
            min_value=SERVICE_PORT_MIN,
            max_value=SERVICE_PORT_MAX
        ),
        help_text=_("Comma-separated list of one or more port numbers. A range may be specified using a hyphen.")
    )
    comments = CommentField()

    fieldsets = (
        (_('Service Template'), (
            'name', 'protocol', 'ports', 'description', 'tags',
        )),
    )

    class Meta:
        model = ServiceTemplate
        fields = ('name', 'protocol', 'ports', 'description', 'comments', 'tags')


class ServiceForm(NetBoxModelForm):
    device = DynamicModelChoiceField(
        label=_('Device'),
        queryset=Device.objects.all(),
        required=False,
        selector=True
    )
    virtual_machine = DynamicModelChoiceField(
        label=_('Virtual machine'),
        queryset=VirtualMachine.objects.all(),
        required=False,
        selector=True
    )
    ports = NumericArrayField(
        label=_('Ports'),
        base_field=forms.IntegerField(
            min_value=SERVICE_PORT_MIN,
            max_value=SERVICE_PORT_MAX
        ),
        help_text=_("Comma-separated list of one or more port numbers. A range may be specified using a hyphen.")
    )
    ipaddresses = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label=_('IP Addresses'),
        query_params={
            'device_id': '$device',
            'virtual_machine_id': '$virtual_machine',
        }
    )
    comments = CommentField()

    class Meta:
        model = Service
        fields = [
            'device', 'virtual_machine', 'name', 'protocol', 'ports', 'ipaddresses', 'description', 'comments', 'tags',
        ]


class ServiceCreateForm(ServiceForm):
    service_template = DynamicModelChoiceField(
        label=_('Service template'),
        queryset=ServiceTemplate.objects.all(),
        required=False
    )

    class Meta(ServiceForm.Meta):
        fields = [
            'device', 'virtual_machine', 'service_template', 'name', 'protocol', 'ports', 'ipaddresses', 'description',
            'comments', 'tags',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fields which may be populated from a ServiceTemplate are not required
        for field in ('name', 'protocol', 'ports'):
            self.fields[field].required = False
            del self.fields[field].widget.attrs['required']

    def clean(self):
        super().clean()
        if self.cleaned_data['service_template']:
            # Create a new Service from the specified template
            service_template = self.cleaned_data['service_template']
            self.cleaned_data['name'] = service_template.name
            self.cleaned_data['protocol'] = service_template.protocol
            self.cleaned_data['ports'] = service_template.ports
            if not self.cleaned_data['description']:
                self.cleaned_data['description'] = service_template.description
        elif not all(self.cleaned_data[f] for f in ('name', 'protocol', 'ports')):
            raise forms.ValidationError(_("Must specify name, protocol, and port(s) if not using a service template."))
