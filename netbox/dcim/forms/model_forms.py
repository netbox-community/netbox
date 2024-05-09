from django import forms
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from timezone_field import TimeZoneFormField

from dcim.choices import *
from dcim.constants import *
from dcim.models import *
from extras.models import ConfigTemplate
from ipam.models import ASN, IPAddress, VLAN, VLANGroup, VRF
from netbox.forms import NetBoxModelForm
from tenancy.forms import TenancyForm
from utilities.forms import add_blank_choice
from utilities.forms.fields import (
    CommentField, DynamicModelChoiceField, DynamicModelMultipleChoiceField, JSONField, NumericArrayField, SlugField,
)
from utilities.forms.rendering import FieldSet, InlineFields, TabbedGroups
from utilities.forms.widgets import APISelect, ClearableFileInput, HTMXSelect, NumberWithOptions, SelectWithPK
from virtualization.models import Cluster
from wireless.models import WirelessLAN, WirelessLANGroup
from .common import InterfaceCommonForm, ModuleCommonForm

__all__ = (
    'CableForm',
    'ConsolePortForm',
    'ConsolePortTemplateForm',
    'ConsoleServerPortForm',
    'ConsoleServerPortTemplateForm',
    'DeviceBayForm',
    'DeviceBayTemplateForm',
    'DeviceForm',
    'DeviceRoleForm',
    'DeviceTypeForm',
    'DeviceVCMembershipForm',
    'FrontPortForm',
    'FrontPortTemplateForm',
    'InterfaceForm',
    'InterfaceTemplateForm',
    'InventoryItemForm',
    'InventoryItemRoleForm',
    'InventoryItemTemplateForm',
    'LocationForm',
    'ManufacturerForm',
    'ModuleForm',
    'ModuleBayForm',
    'ModuleBayTemplateForm',
    'ModuleTypeForm',
    'PlatformForm',
    'PopulateDeviceBayForm',
    'PowerFeedForm',
    'PowerOutletForm',
    'PowerOutletTemplateForm',
    'PowerPanelForm',
    'PowerPortForm',
    'PowerPortTemplateForm',
    'RackForm',
    'RackReservationForm',
    'RackRoleForm',
    'RearPortForm',
    'RearPortTemplateForm',
    'RegionForm',
    'SiteForm',
    'SiteGroupForm',
    'VCMemberSelectForm',
    'VirtualChassisForm',
    'VirtualDeviceContextForm'
)


class RegionForm(NetBoxModelForm):
    parent = DynamicModelChoiceField(
        label=_('Parent'),
        queryset=Region.objects.all(),
        required=False
    )
    slug = SlugField()

    fieldsets = (
        FieldSet('parent', 'name', 'slug', 'description', 'tags'),
    )

    class Meta:
        model = Region
        fields = (
            'parent', 'name', 'slug', 'description', 'tags',
        )


class SiteGroupForm(NetBoxModelForm):
    parent = DynamicModelChoiceField(
        label=_('Parent'),
        queryset=SiteGroup.objects.all(),
        required=False
    )
    slug = SlugField()

    fieldsets = (
        FieldSet('parent', 'name', 'slug', 'description', 'tags'),
    )

    class Meta:
        model = SiteGroup
        fields = (
            'parent', 'name', 'slug', 'description', 'tags',
        )


class SiteForm(TenancyForm, NetBoxModelForm):
    region = DynamicModelChoiceField(
        label=_('Region'),
        queryset=Region.objects.all(),
        required=False
    )
    group = DynamicModelChoiceField(
        label=_('Group'),
        queryset=SiteGroup.objects.all(),
        required=False
    )
    asns = DynamicModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        label=_('ASNs'),
        required=False
    )
    slug = SlugField()
    time_zone = TimeZoneFormField(
        label=_('Time zone'),
        choices=add_blank_choice(TimeZoneFormField().choices),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        FieldSet(
            'name', 'slug', 'status', 'region', 'group', 'facility', 'asns', 'time_zone', 'description', 'tags',
            name=_('Site')
        ),
        FieldSet('tenant_group', 'tenant', name=_('Tenancy')),
        FieldSet('physical_address', 'shipping_address', 'latitude', 'longitude', name=_('Contact Info')),
    )

    class Meta:
        model = Site
        fields = (
            'name', 'slug', 'status', 'region', 'group', 'tenant_group', 'tenant', 'facility', 'asns', 'time_zone',
            'description', 'physical_address', 'shipping_address', 'latitude', 'longitude', 'comments', 'tags',
        )
        widgets = {
            'physical_address': forms.Textarea(
                attrs={
                    'rows': 3,
                }
            ),
            'shipping_address': forms.Textarea(
                attrs={
                    'rows': 3,
                }
            ),
        }


class LocationForm(TenancyForm, NetBoxModelForm):
    site = DynamicModelChoiceField(
        label=_('Site'),
        queryset=Site.objects.all(),
        selector=True
    )
    parent = DynamicModelChoiceField(
        label=_('Parent'),
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    slug = SlugField()

    fieldsets = (
        FieldSet('site', 'parent', 'name', 'slug', 'status', 'facility', 'description', 'tags', name=_('Location')),
        FieldSet('tenant_group', 'tenant', name=_('Tenancy')),
    )

    class Meta:
        model = Location
        fields = (
            'site', 'parent', 'name', 'slug', 'status', 'description', 'tenant_group', 'tenant', 'facility', 'tags',
        )


class RackRoleForm(NetBoxModelForm):
    slug = SlugField()

    fieldsets = (
        FieldSet('name', 'slug', 'color', 'description', 'tags', name=_('Rack Role')),
    )

    class Meta:
        model = RackRole
        fields = [
            'name', 'slug', 'color', 'description', 'tags',
        ]


class RackForm(TenancyForm, NetBoxModelForm):
    site = DynamicModelChoiceField(
        label=_('Site'),
        queryset=Site.objects.all(),
        selector=True
    )
    location = DynamicModelChoiceField(
        label=_('Location'),
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    role = DynamicModelChoiceField(
        label=_('Role'),
        queryset=RackRole.objects.all(),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        FieldSet('site', 'location', 'name', 'status', 'role', 'description', 'tags', name=_('Rack')),
        FieldSet('facility_id', 'serial', 'asset_tag', name=_('Inventory Control')),
        FieldSet('tenant_group', 'tenant', name=_('Tenancy')),
        FieldSet(
            'type', 'width', 'starting_unit', 'u_height',
            InlineFields('outer_width', 'outer_depth', 'outer_unit', label=_('Outer Dimensions')),
            InlineFields('weight', 'max_weight', 'weight_unit', label=_('Weight')),
            'mounting_depth', 'desc_units', name=_('Dimensions')
        ),
    )

    class Meta:
        model = Rack
        fields = [
            'site', 'location', 'name', 'facility_id', 'tenant_group', 'tenant', 'status', 'role', 'serial',
            'asset_tag', 'type', 'width', 'u_height', 'starting_unit', 'desc_units', 'outer_width', 'outer_depth',
            'outer_unit', 'mounting_depth', 'weight', 'max_weight', 'weight_unit', 'description', 'comments', 'tags',
        ]


class RackReservationForm(TenancyForm, NetBoxModelForm):
    rack = DynamicModelChoiceField(
        label=_('Rack'),
        queryset=Rack.objects.all(),
        selector=True
    )
    units = NumericArrayField(
        label=_('Units'),
        base_field=forms.IntegerField(),
        help_text=_("Comma-separated list of numeric unit IDs. A range may be specified using a hyphen.")
    )
    user = forms.ModelChoiceField(
        label=_('User'),
        queryset=get_user_model().objects.order_by(
            'username'
        )
    )
    comments = CommentField()

    fieldsets = (
        FieldSet('rack', 'units', 'user', 'description', 'tags', name=_('Reservation')),
        FieldSet('tenant_group', 'tenant', name=_('Tenancy')),
    )

    class Meta:
        model = RackReservation
        fields = [
            'rack', 'units', 'user', 'tenant_group', 'tenant', 'description', 'comments', 'tags',
        ]


class ManufacturerForm(NetBoxModelForm):
    slug = SlugField()

    fieldsets = (
        FieldSet('name', 'slug', 'description', 'tags', name=_('Manufacturer')),
    )

    class Meta:
        model = Manufacturer
        fields = [
            'name', 'slug', 'description', 'tags',
        ]


class DeviceTypeForm(NetBoxModelForm):
    manufacturer = DynamicModelChoiceField(
        label=_('Manufacturer'),
        queryset=Manufacturer.objects.all()
    )
    default_platform = DynamicModelChoiceField(
        label=_('Default platform'),
        queryset=Platform.objects.all(),
        required=False,
        selector=True,
        query_params={
            'manufacturer_id': ['$manufacturer', 'null'],
        }
    )
    slug = SlugField(
        label=_('Slug'),
        slug_source='model'
    )
    comments = CommentField()

    fieldsets = (
        FieldSet('manufacturer', 'model', 'slug', 'default_platform', 'description', 'tags', name=_('Device Type')),
        FieldSet(
            'u_height', 'exclude_from_utilization', 'is_full_depth', 'part_number', 'subdevice_role', 'airflow',
            'weight', 'weight_unit', name=_('Chassis')
        ),
        FieldSet('front_image', 'rear_image', name=_('Images')),
    )

    class Meta:
        model = DeviceType
        fields = [
            'manufacturer', 'model', 'slug', 'default_platform', 'part_number', 'u_height', 'exclude_from_utilization',
            'is_full_depth', 'subdevice_role', 'airflow', 'weight', 'weight_unit', 'front_image', 'rear_image',
            'description', 'comments', 'tags',
        ]
        widgets = {
            'front_image': ClearableFileInput(attrs={
                'accept': DEVICETYPE_IMAGE_FORMATS
            }),
            'rear_image': ClearableFileInput(attrs={
                'accept': DEVICETYPE_IMAGE_FORMATS
            }),
        }


class ModuleTypeForm(NetBoxModelForm):
    manufacturer = DynamicModelChoiceField(
        label=_('Manufacturer'),
        queryset=Manufacturer.objects.all()
    )
    comments = CommentField()

    fieldsets = (
        FieldSet('manufacturer', 'model', 'part_number', 'description', 'tags', name=_('Module Type')),
        FieldSet('weight', 'weight_unit', name=_('Weight'))
    )

    class Meta:
        model = ModuleType
        fields = [
            'manufacturer', 'model', 'part_number', 'weight', 'weight_unit', 'description', 'comments', 'tags',
        ]


class DeviceRoleForm(NetBoxModelForm):
    config_template = DynamicModelChoiceField(
        label=_('Config template'),
        queryset=ConfigTemplate.objects.all(),
        required=False
    )
    slug = SlugField()

    fieldsets = (
        FieldSet(
            'name', 'slug', 'color', 'vm_role', 'config_template', 'description', 'tags', name=_('Device Role')
        ),
    )

    class Meta:
        model = DeviceRole
        fields = [
            'name', 'slug', 'color', 'vm_role', 'config_template', 'description', 'tags',
        ]


class PlatformForm(NetBoxModelForm):
    manufacturer = DynamicModelChoiceField(
        label=_('Manufacturer'),
        queryset=Manufacturer.objects.all(),
        required=False
    )
    config_template = DynamicModelChoiceField(
        label=_('Config template'),
        queryset=ConfigTemplate.objects.all(),
        required=False
    )
    slug = SlugField(
        label=_('Slug'),
        max_length=64
    )

    fieldsets = (
        FieldSet('name', 'slug', 'manufacturer', 'config_template', 'description', 'tags', name=_('Platform')),
    )

    class Meta:
        model = Platform
        fields = [
            'name', 'slug', 'manufacturer', 'config_template', 'description', 'tags',
        ]


class DeviceForm(TenancyForm, NetBoxModelForm):
    site = DynamicModelChoiceField(
        label=_('Site'),
        queryset=Site.objects.all(),
        selector=True
    )
    location = DynamicModelChoiceField(
        label=_('Location'),
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        },
        initial_params={
            'racks': '$rack'
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
    position = forms.DecimalField(
        label=_('Position'),
        required=False,
        help_text=_("The lowest-numbered unit occupied by the device"),
        localize=True,
        widget=APISelect(
            api_url='/api/dcim/racks/{{rack}}/elevation/',
            attrs={
                'ts-disabled-field': 'device',
                'data-dynamic-params': '[{"fieldName":"face","queryParam":"face"}]'
            },
        )
    )
    device_type = DynamicModelChoiceField(
        label=_('Device type'),
        queryset=DeviceType.objects.all(),
        context={
            'parent': 'manufacturer',
        },
        selector=True
    )
    role = DynamicModelChoiceField(
        label=_('Device role'),
        queryset=DeviceRole.objects.all()
    )
    platform = DynamicModelChoiceField(
        label=_('Platform'),
        queryset=Platform.objects.all(),
        required=False,
        selector=True,
        query_params={
            'available_for_device_type': '$device_type',
        }
    )
    cluster = DynamicModelChoiceField(
        label=_('Cluster'),
        queryset=Cluster.objects.all(),
        required=False,
        selector=True
    )
    comments = CommentField()
    local_context_data = JSONField(
        required=False,
        label=''
    )
    virtual_chassis = DynamicModelChoiceField(
        label=_('Virtual chassis'),
        queryset=VirtualChassis.objects.all(),
        required=False,
        context={
            'parent': 'master',
        },
        selector=True
    )
    vc_position = forms.IntegerField(
        required=False,
        label=_('Position'),
        help_text=_("The position in the virtual chassis this device is identified by")
    )
    vc_priority = forms.IntegerField(
        required=False,
        label=_('Priority'),
        help_text=_("The priority of the device in the virtual chassis")
    )
    config_template = DynamicModelChoiceField(
        label=_('Config template'),
        queryset=ConfigTemplate.objects.all(),
        required=False
    )

    class Meta:
        model = Device
        fields = [
            'name', 'role', 'device_type', 'serial', 'asset_tag', 'site', 'rack', 'location', 'position', 'face',
            'latitude', 'longitude', 'status', 'airflow', 'platform', 'primary_ip4', 'primary_ip6', 'oob_ip', 'cluster',
            'tenant_group', 'tenant', 'virtual_chassis', 'vc_position', 'vc_priority', 'description', 'config_template',
            'comments', 'tags', 'local_context_data',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:

            # Compile list of choices for primary IPv4 and IPv6 addresses
            oob_ip_choices = [(None, '---------')]
            for family in [4, 6]:
                ip_choices = [(None, '---------')]

                # Gather PKs of all interfaces belonging to this Device or a peer VirtualChassis member
                interface_ids = self.instance.vc_interfaces(if_master=False).values_list('pk', flat=True)

                # Collect interface IPs
                interface_ips = IPAddress.objects.filter(
                    address__family=family,
                    assigned_object_type=ContentType.objects.get_for_model(Interface),
                    assigned_object_id__in=interface_ids
                ).prefetch_related('assigned_object')
                if interface_ips:
                    ip_list = [(ip.id, f'{ip.address} ({ip.assigned_object})') for ip in interface_ips]
                    ip_choices.append(('Interface IPs', ip_list))
                    oob_ip_choices.extend(ip_list)
                # Collect NAT IPs
                nat_ips = IPAddress.objects.prefetch_related('nat_inside').filter(
                    address__family=family,
                    nat_inside__assigned_object_type=ContentType.objects.get_for_model(Interface),
                    nat_inside__assigned_object_id__in=interface_ids
                ).prefetch_related('assigned_object')
                if nat_ips:
                    ip_list = [(ip.id, f'{ip.address} (NAT)') for ip in nat_ips]
                    ip_choices.append(('NAT IPs', ip_list))
                self.fields['primary_ip{}'.format(family)].choices = ip_choices
            self.fields['oob_ip'].choices = oob_ip_choices

            # If editing an existing device, exclude it from the list of occupied rack units. This ensures that a device
            # can be flipped from one face to another.
            self.fields['position'].widget.add_query_param('exclude', self.instance.pk)

            # Disable rack assignment if this is a child device installed in a parent device
            if self.instance.device_type.is_child_device and hasattr(self.instance, 'parent_bay'):
                self.fields['site'].disabled = True
                self.fields['rack'].disabled = True
                self.initial['site'] = self.instance.parent_bay.device.site_id
                self.initial['rack'] = self.instance.parent_bay.device.rack_id

        else:

            # An object that doesn't exist yet can't have any IPs assigned to it
            self.fields['primary_ip4'].choices = []
            self.fields['primary_ip4'].widget.attrs['readonly'] = True
            self.fields['primary_ip6'].choices = []
            self.fields['primary_ip6'].widget.attrs['readonly'] = True
            self.fields['oob_ip'].choices = []
            self.fields['oob_ip'].widget.attrs['readonly'] = True

        # Rack position
        position = self.data.get('position') or self.initial.get('position')
        if position:
            self.fields['position'].widget.choices = [(position, f'U{position}')]


class ModuleForm(ModuleCommonForm, NetBoxModelForm):
    device = DynamicModelChoiceField(
        label=_('Device'),
        queryset=Device.objects.all(),
        initial_params={
            'modulebays': '$module_bay'
        }
    )
    module_bay = DynamicModelChoiceField(
        label=_('Module bay'),
        queryset=ModuleBay.objects.all(),
        query_params={
            'device_id': '$device'
        }
    )
    module_type = DynamicModelChoiceField(
        label=_('Module type'),
        queryset=ModuleType.objects.all(),
        context={
            'parent': 'manufacturer',
        },
        selector=True
    )
    comments = CommentField()
    replicate_components = forms.BooleanField(
        label=_('Replicate components'),
        required=False,
        initial=True,
        help_text=_("Automatically populate components associated with this module type")
    )
    adopt_components = forms.BooleanField(
        label=_('Adopt components'),
        required=False,
        initial=False,
        help_text=_("Adopt already existing components")
    )

    fieldsets = (
        FieldSet('device', 'module_bay', 'module_type', 'status', 'description', 'tags', name=_('Module')),
        FieldSet('serial', 'asset_tag', 'replicate_components', 'adopt_components', name=_('Hardware')),
    )

    class Meta:
        model = Module
        fields = [
            'device', 'module_bay', 'module_type', 'status', 'serial', 'asset_tag', 'tags', 'replicate_components',
            'adopt_components', 'description', 'comments',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['device'].disabled = True
            self.fields['replicate_components'].initial = False
            self.fields['replicate_components'].disabled = True
            self.fields['adopt_components'].initial = False
            self.fields['adopt_components'].disabled = True


def get_termination_type_choices():
    return add_blank_choice([
        (f'{ct.app_label}.{ct.model}', ct.model_class()._meta.verbose_name.title())
        for ct in ContentType.objects.filter(CABLE_TERMINATION_MODELS)
    ])


class CableForm(TenancyForm, NetBoxModelForm):
    a_terminations_type = forms.ChoiceField(
        choices=get_termination_type_choices,
        required=False,
        widget=HTMXSelect(),
        label=_('Type')
    )
    b_terminations_type = forms.ChoiceField(
        choices=get_termination_type_choices,
        required=False,
        widget=HTMXSelect(),
        label=_('Type')
    )
    comments = CommentField()

    class Meta:
        model = Cable
        fields = [
            'a_terminations_type', 'b_terminations_type', 'type', 'status', 'tenant_group', 'tenant', 'label', 'color',
            'length', 'length_unit', 'description', 'comments', 'tags',
        ]
        error_messages = {
            'length': {
                'max_value': _('Maximum length is 32767 (any unit)')
            }
        }


class PowerPanelForm(NetBoxModelForm):
    site = DynamicModelChoiceField(
        label=_('Site'),
        queryset=Site.objects.all(),
        selector=True
    )
    location = DynamicModelChoiceField(
        label=_('Location'),
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    comments = CommentField()

    fieldsets = (
        FieldSet('site', 'location', 'name', 'description', 'tags', name=_('Power Panel')),
    )

    class Meta:
        model = PowerPanel
        fields = [
            'site', 'location', 'name', 'description', 'comments', 'tags',
        ]


class PowerFeedForm(TenancyForm, NetBoxModelForm):
    power_panel = DynamicModelChoiceField(
        label=_('Power panel'),
        queryset=PowerPanel.objects.all(),
        selector=True
    )
    rack = DynamicModelChoiceField(
        label=_('Rack'),
        queryset=Rack.objects.all(),
        required=False,
        selector=True
    )
    comments = CommentField()

    fieldsets = (
        FieldSet(
            'power_panel', 'rack', 'name', 'status', 'type', 'description', 'mark_connected', 'tags',
            name=_('Power Feed')
        ),
        FieldSet('supply', 'voltage', 'amperage', 'phase', 'max_utilization', name=_('Characteristics')),
        FieldSet('tenant_group', 'tenant', name=_('Tenancy')),
    )

    class Meta:
        model = PowerFeed
        fields = [
            'power_panel', 'rack', 'name', 'status', 'type', 'mark_connected', 'supply', 'phase', 'voltage', 'amperage',
            'max_utilization', 'tenant_group', 'tenant', 'description', 'comments', 'tags'
        ]


#
# Virtual chassis
#

class VirtualChassisForm(NetBoxModelForm):
    master = forms.ModelChoiceField(
        label=_('Master'),
        queryset=Device.objects.all(),
        required=False,
    )
    comments = CommentField()

    class Meta:
        model = VirtualChassis
        fields = [
            'name', 'domain', 'master', 'description', 'comments', 'tags',
        ]
        widgets = {
            'master': SelectWithPK(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['master'].queryset = Device.objects.filter(virtual_chassis=self.instance)


class DeviceVCMembershipForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = [
            'vc_position', 'vc_priority',
        ]
        labels = {
            'vc_position': 'Position',
            'vc_priority': 'Priority',
        }

    def __init__(self, validate_vc_position=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Require VC position (only required when the Device is a VirtualChassis member)
        self.fields['vc_position'].required = True

        # Add bootstrap classes to form elements.
        self.fields['vc_position'].widget.attrs = {'class': 'form-control'}
        self.fields['vc_priority'].widget.attrs = {'class': 'form-control'}

        # Validation of vc_position is optional. This is only required when adding a new member to an existing
        # VirtualChassis. Otherwise, vc_position validation is handled by BaseVCMemberFormSet.
        self.validate_vc_position = validate_vc_position

    def clean_vc_position(self):
        vc_position = self.cleaned_data['vc_position']

        if self.validate_vc_position:
            conflicting_members = Device.objects.filter(
                virtual_chassis=self.instance.virtual_chassis,
                vc_position=vc_position
            )
            if conflicting_members.exists():
                raise forms.ValidationError(
                    'A virtual chassis member already exists in position {}.'.format(vc_position)
                )

        return vc_position


class VCMemberSelectForm(forms.Form):
    device = DynamicModelChoiceField(
        label=_('Device'),
        queryset=Device.objects.all(),
        query_params={
            'virtual_chassis_id': 'null',
        },
        selector=True
    )

    def clean_device(self):
        device = self.cleaned_data['device']
        if device.virtual_chassis is not None:
            raise forms.ValidationError(
                f"Device {device} is already assigned to a virtual chassis."
            )
        return device


#
# Device component templates
#

class ComponentTemplateForm(forms.ModelForm):
    device_type = DynamicModelChoiceField(
        label=_('Device type'),
        queryset=DeviceType.objects.all(),
        context={
            'parent': 'manufacturer',
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Disable reassignment of DeviceType when editing an existing instance
        if self.instance.pk:
            self.fields['device_type'].disabled = True


class ModularComponentTemplateForm(ComponentTemplateForm):
    device_type = DynamicModelChoiceField(
        label=_('Device type'),
        queryset=DeviceType.objects.all().all(),
        required=False,
        context={
            'parent': 'manufacturer',
        }
    )
    module_type = DynamicModelChoiceField(
        label=_('Module type'),
        queryset=ModuleType.objects.all(),
        required=False,
        context={
            'parent': 'manufacturer',
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Disable reassignment of ModuleType when editing an existing instance
        if self.instance.pk:
            self.fields['module_type'].disabled = True


class ConsolePortTemplateForm(ModularComponentTemplateForm):
    fieldsets = (
        FieldSet('device_type', 'module_type', 'name', 'label', 'type', 'description'),
    )

    class Meta:
        model = ConsolePortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'description',
        ]


class ConsoleServerPortTemplateForm(ModularComponentTemplateForm):
    fieldsets = (
        FieldSet('device_type', 'module_type', 'name', 'label', 'type', 'description'),
    )

    class Meta:
        model = ConsoleServerPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'description',
        ]


class PowerPortTemplateForm(ModularComponentTemplateForm):
    fieldsets = (
        FieldSet(
            'device_type', 'module_type', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description',
        ),
    )

    class Meta:
        model = PowerPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description',
        ]


class PowerOutletTemplateForm(ModularComponentTemplateForm):
    power_port = DynamicModelChoiceField(
        label=_('Power port'),
        queryset=PowerPortTemplate.objects.all(),
        required=False,
        query_params={
            'devicetype_id': '$device_type',
        }
    )

    fieldsets = (
        FieldSet('device_type', 'module_type', 'name', 'label', 'type', 'power_port', 'feed_leg', 'description'),
    )

    class Meta:
        model = PowerOutletTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'power_port', 'feed_leg', 'description',
        ]


class InterfaceTemplateForm(ModularComponentTemplateForm):
    bridge = DynamicModelChoiceField(
        label=_('Bridge'),
        queryset=InterfaceTemplate.objects.all(),
        required=False,
        query_params={
            'devicetype_id': '$device_type',
            'moduletype_id': '$module_type',
        }
    )

    fieldsets = (
        FieldSet(
            'device_type', 'module_type', 'name', 'label', 'type', 'enabled', 'mgmt_only', 'description', 'bridge',
        ),
        FieldSet('poe_mode', 'poe_type', name=_('PoE')),
        FieldSet('rf_role', name=_('Wireless')),
    )

    class Meta:
        model = InterfaceTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'mgmt_only', 'enabled', 'description', 'poe_mode', 'poe_type', 'bridge', 'rf_role',
        ]


class FrontPortTemplateForm(ModularComponentTemplateForm):
    rear_port = DynamicModelChoiceField(
        label=_('Rear port'),
        queryset=RearPortTemplate.objects.all(),
        required=False,
        query_params={
            'devicetype_id': '$device_type',
            'moduletype_id': '$module_type',
        }
    )

    fieldsets = (
        FieldSet(
            'device_type', 'module_type', 'name', 'label', 'type', 'color', 'rear_port', 'rear_port_position',
            'description',
        ),
    )

    class Meta:
        model = FrontPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'color', 'rear_port', 'rear_port_position',
            'description',
        ]


class RearPortTemplateForm(ModularComponentTemplateForm):
    fieldsets = (
        FieldSet('device_type', 'module_type', 'name', 'label', 'type', 'color', 'positions', 'description'),
    )

    class Meta:
        model = RearPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'color', 'positions', 'description',
        ]


class ModuleBayTemplateForm(ComponentTemplateForm):
    fieldsets = (
        FieldSet('device_type', 'name', 'label', 'position', 'description'),
    )

    class Meta:
        model = ModuleBayTemplate
        fields = [
            'device_type', 'name', 'label', 'position', 'description',
        ]


class DeviceBayTemplateForm(ComponentTemplateForm):
    fieldsets = (
        FieldSet('device_type', 'name', 'label', 'description'),
    )

    class Meta:
        model = DeviceBayTemplate
        fields = [
            'device_type', 'name', 'label', 'description',
        ]


class InventoryItemTemplateForm(ComponentTemplateForm):
    parent = DynamicModelChoiceField(
        label=_('Parent'),
        queryset=InventoryItemTemplate.objects.all(),
        required=False,
        query_params={
            'devicetype_id': '$device_type'
        }
    )
    role = DynamicModelChoiceField(
        label=_('Role'),
        queryset=InventoryItemRole.objects.all(),
        required=False
    )
    manufacturer = DynamicModelChoiceField(
        label=_('Manufacturer'),
        queryset=Manufacturer.objects.all(),
        required=False
    )

    # Assigned component selectors
    consoleporttemplate = DynamicModelChoiceField(
        queryset=ConsolePortTemplate.objects.all(),
        required=False,
        query_params={
            'device_type_id': '$device_type'
        },
        label=_('Console port template')
    )
    consoleserverporttemplate = DynamicModelChoiceField(
        queryset=ConsoleServerPortTemplate.objects.all(),
        required=False,
        query_params={
            'device_type_id': '$device_type'
        },
        label=_('Console server port template')
    )
    frontporttemplate = DynamicModelChoiceField(
        queryset=FrontPortTemplate.objects.all(),
        required=False,
        query_params={
            'device_type_id': '$device_type'
        },
        label=_('Front port template')
    )
    interfacetemplate = DynamicModelChoiceField(
        queryset=InterfaceTemplate.objects.all(),
        required=False,
        query_params={
            'device_type_id': '$device_type'
        },
        label=_('Interface template')
    )
    poweroutlettemplate = DynamicModelChoiceField(
        queryset=PowerOutletTemplate.objects.all(),
        required=False,
        query_params={
            'device_type_id': '$device_type'
        },
        label=_('Power outlet template')
    )
    powerporttemplate = DynamicModelChoiceField(
        queryset=PowerPortTemplate.objects.all(),
        required=False,
        query_params={
            'device_type_id': '$device_type'
        },
        label=_('Power port template')
    )
    rearporttemplate = DynamicModelChoiceField(
        queryset=RearPortTemplate.objects.all(),
        required=False,
        query_params={
            'device_type_id': '$device_type'
        },
        label=_('Rear port template')
    )

    fieldsets = (
        FieldSet(
            'device_type', 'parent', 'name', 'label', 'role', 'manufacturer', 'part_id', 'description',
        ),
        FieldSet(
            TabbedGroups(
                FieldSet('interfacetemplate', name=_('Interface')),
                FieldSet('consoleporttemplate', name=_('Console Port')),
                FieldSet('consoleserverporttemplate', name=_('Console Server Port')),
                FieldSet('frontporttemplate', name=_('Front Port')),
                FieldSet('rearporttemplate', name=_('Rear Port')),
                FieldSet('powerporttemplate', name=_('Power Port')),
                FieldSet('poweroutlettemplate', name=_('Power Outlet')),
            ),
            name=_('Component Assignment')
        )
    )

    class Meta:
        model = InventoryItemTemplate
        fields = [
            'device_type', 'parent', 'name', 'label', 'role', 'manufacturer', 'part_id', 'description',
        ]

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {}).copy()
        component_type = initial.get('component_type')
        component_id = initial.get('component_id')

        if instance:
            # When editing set the initial value for component selection
            for component_model in ContentType.objects.filter(MODULAR_COMPONENT_TEMPLATE_MODELS):
                if type(instance.component) is component_model.model_class():
                    initial[component_model.model] = instance.component
                    break
        elif component_type and component_id:
            # When adding the InventoryItem from a component page
            if content_type := ContentType.objects.filter(MODULAR_COMPONENT_TEMPLATE_MODELS).filter(pk=component_type).first():
                if component := content_type.model_class().objects.filter(pk=component_id).first():
                    initial[content_type.model] = component

        kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()

        # Handle object assignment
        selected_objects = [
            field for field in (
                'consoleporttemplate', 'consoleserverporttemplate', 'frontporttemplate', 'interfacetemplate',
                'poweroutlettemplate', 'powerporttemplate', 'rearporttemplate'
            ) if self.cleaned_data[field]
        ]
        if len(selected_objects) > 1:
            raise forms.ValidationError(_("An InventoryItem can only be assigned to a single component."))
        elif selected_objects:
            self.instance.component = self.cleaned_data[selected_objects[0]]
        else:
            self.instance.component = None


#
# Device components
#

class DeviceComponentForm(NetBoxModelForm):
    device = DynamicModelChoiceField(
        label=_('Device'),
        queryset=Device.objects.all(),
        selector=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Disable reassignment of Device when editing an existing instance
        if self.instance.pk:
            self.fields['device'].disabled = True


class ModularDeviceComponentForm(DeviceComponentForm):
    module = DynamicModelChoiceField(
        label=_('Module'),
        queryset=Module.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )


class ConsolePortForm(ModularDeviceComponentForm):
    fieldsets = (
        FieldSet(
            'device', 'module', 'name', 'label', 'type', 'speed', 'mark_connected', 'description', 'tags',
        ),
    )

    class Meta:
        model = ConsolePort
        fields = [
            'device', 'module', 'name', 'label', 'type', 'speed', 'mark_connected', 'description', 'tags',
        ]


class ConsoleServerPortForm(ModularDeviceComponentForm):
    fieldsets = (
        FieldSet(
            'device', 'module', 'name', 'label', 'type', 'speed', 'mark_connected', 'description', 'tags',
        ),
    )

    class Meta:
        model = ConsoleServerPort
        fields = [
            'device', 'module', 'name', 'label', 'type', 'speed', 'mark_connected', 'description', 'tags',
        ]


class PowerPortForm(ModularDeviceComponentForm):
    fieldsets = (
        FieldSet(
            'device', 'module', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'mark_connected',
            'description', 'tags',
        ),
    )

    class Meta:
        model = PowerPort
        fields = [
            'device', 'module', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'mark_connected',
            'description', 'tags',
        ]


class PowerOutletForm(ModularDeviceComponentForm):
    power_port = DynamicModelChoiceField(
        label=_('Power port'),
        queryset=PowerPort.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )

    fieldsets = (
        FieldSet(
            'device', 'module', 'name', 'label', 'type', 'power_port', 'feed_leg', 'mark_connected', 'description',
            'tags',
        ),
    )

    class Meta:
        model = PowerOutlet
        fields = [
            'device', 'module', 'name', 'label', 'type', 'power_port', 'feed_leg', 'mark_connected', 'description',
            'tags',
        ]


class InterfaceForm(InterfaceCommonForm, ModularDeviceComponentForm):
    vdcs = DynamicModelMultipleChoiceField(
        queryset=VirtualDeviceContext.objects.all(),
        required=False,
        label=_('Virtual device contexts'),
        initial_params={
            'interfaces': '$parent',
        },
        query_params={
            'device_id': '$device',
        }
    )
    parent = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label=_('Parent interface'),
        query_params={
            'virtual_chassis_member_id': '$device',
        }
    )
    bridge = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label=_('Bridged interface'),
        query_params={
            'virtual_chassis_member_id': '$device',
        }
    )
    lag = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label=_('LAG interface'),
        query_params={
            'virtual_chassis_member_id': '$device',
            'type': 'lag',
        }
    )
    wireless_lan_group = DynamicModelChoiceField(
        queryset=WirelessLANGroup.objects.all(),
        required=False,
        label=_('Wireless LAN group')
    )
    wireless_lans = DynamicModelMultipleChoiceField(
        queryset=WirelessLAN.objects.all(),
        required=False,
        label=_('Wireless LANs'),
        query_params={
            'group_id': '$wireless_lan_group',
        }
    )
    vlan_group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        label=_('VLAN group')
    )
    untagged_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label=_('Untagged VLAN'),
        query_params={
            'group_id': '$vlan_group',
            'available_on_device': '$device',
        }
    )
    tagged_vlans = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label=_('Tagged VLANs'),
        query_params={
            'group_id': '$vlan_group',
            'available_on_device': '$device',
        }
    )
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('VRF')
    )
    wwn = forms.CharField(
        empty_value=None,
        required=False,
        label=_('WWN')
    )

    fieldsets = (
        FieldSet(
            'device', 'module', 'name', 'label', 'type', 'speed', 'duplex', 'description', 'tags', name=_('Interface')
        ),
        FieldSet('vrf', 'mac_address', 'wwn', name=_('Addressing')),
        FieldSet('vdcs', 'mtu', 'tx_power', 'enabled', 'mgmt_only', 'mark_connected', name=_('Operation')),
        FieldSet('parent', 'bridge', 'lag', name=_('Related Interfaces')),
        FieldSet('poe_mode', 'poe_type', name=_('PoE')),
        FieldSet('mode', 'vlan_group', 'untagged_vlan', 'tagged_vlans', name=_('802.1Q Switching')),
        FieldSet(
            'rf_role', 'rf_channel', 'rf_channel_frequency', 'rf_channel_width', 'wireless_lan_group', 'wireless_lans',
            name=_('Wireless')
        ),
    )

    class Meta:
        model = Interface
        fields = [
            'device', 'module', 'vdcs', 'name', 'label', 'type', 'speed', 'duplex', 'enabled', 'parent', 'bridge', 'lag',
            'mac_address', 'wwn', 'mtu', 'mgmt_only', 'mark_connected', 'description', 'poe_mode', 'poe_type', 'mode',
            'rf_role', 'rf_channel', 'rf_channel_frequency', 'rf_channel_width', 'tx_power', 'wireless_lans',
            'untagged_vlan', 'tagged_vlans', 'vrf', 'tags',
        ]
        widgets = {
            'speed': NumberWithOptions(
                options=InterfaceSpeedChoices
            ),
            'mode': HTMXSelect(),
        }
        labels = {
            'mode': '802.1Q Mode',
        }


class FrontPortForm(ModularDeviceComponentForm):
    rear_port = DynamicModelChoiceField(
        queryset=RearPort.objects.all(),
        query_params={
            'device_id': '$device',
        }
    )

    fieldsets = (
        FieldSet(
            'device', 'module', 'name', 'label', 'type', 'color', 'rear_port', 'rear_port_position', 'mark_connected',
            'description', 'tags',
        ),
    )

    class Meta:
        model = FrontPort
        fields = [
            'device', 'module', 'name', 'label', 'type', 'color', 'rear_port', 'rear_port_position', 'mark_connected',
            'description', 'tags',
        ]


class RearPortForm(ModularDeviceComponentForm):
    fieldsets = (
        FieldSet(
            'device', 'module', 'name', 'label', 'type', 'color', 'positions', 'mark_connected', 'description', 'tags',
        ),
    )

    class Meta:
        model = RearPort
        fields = [
            'device', 'module', 'name', 'label', 'type', 'color', 'positions', 'mark_connected', 'description', 'tags',
        ]


class ModuleBayForm(DeviceComponentForm):
    fieldsets = (
        FieldSet('device', 'name', 'label', 'position', 'description', 'tags',),
    )

    class Meta:
        model = ModuleBay
        fields = [
            'device', 'name', 'label', 'position', 'description', 'tags',
        ]


class DeviceBayForm(DeviceComponentForm):
    fieldsets = (
        FieldSet('device', 'name', 'label', 'description', 'tags',),
    )

    class Meta:
        model = DeviceBay
        fields = [
            'device', 'name', 'label', 'description', 'tags',
        ]


class PopulateDeviceBayForm(forms.Form):
    installed_device = forms.ModelChoiceField(
        queryset=Device.objects.all(),
        label=_('Child Device'),
        help_text=_("Child devices must first be created and assigned to the site and rack of the parent device.")
    )

    def __init__(self, device_bay, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['installed_device'].queryset = Device.objects.filter(
            site=device_bay.device.site,
            rack=device_bay.device.rack,
            parent_bay__isnull=True,
            device_type__u_height=0,
            device_type__subdevice_role=SubdeviceRoleChoices.ROLE_CHILD
        ).exclude(pk=device_bay.device.pk)


class InventoryItemForm(DeviceComponentForm):
    parent = DynamicModelChoiceField(
        label=_('Parent'),
        queryset=InventoryItem.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        }
    )
    role = DynamicModelChoiceField(
        label=_('Role'),
        queryset=InventoryItemRole.objects.all(),
        required=False
    )
    manufacturer = DynamicModelChoiceField(
        label=_('Manufacturer'),
        queryset=Manufacturer.objects.all(),
        required=False
    )

    # Assigned component selectors
    consoleport = DynamicModelChoiceField(
        queryset=ConsolePort.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        },
        label=_('Console port')
    )
    consoleserverport = DynamicModelChoiceField(
        queryset=ConsoleServerPort.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        },
        label=_('Console server port')
    )
    frontport = DynamicModelChoiceField(
        queryset=FrontPort.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        },
        label=_('Front port')
    )
    interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        },
        label=_('Interface')
    )
    poweroutlet = DynamicModelChoiceField(
        queryset=PowerOutlet.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        },
        label=_('Power outlet')
    )
    powerport = DynamicModelChoiceField(
        queryset=PowerPort.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        },
        label=_('Power port')
    )
    rearport = DynamicModelChoiceField(
        queryset=RearPort.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        },
        label=_('Rear port')
    )

    fieldsets = (
        FieldSet('device', 'parent', 'name', 'label', 'role', 'description', 'tags', name=_('Inventory Item')),
        FieldSet('manufacturer', 'part_id', 'serial', 'asset_tag', name=_('Hardware')),
        FieldSet(
            TabbedGroups(
                FieldSet('interface', name=_('Interface')),
                FieldSet('consoleport', name=_('Console Port')),
                FieldSet('consoleserverport', name=_('Console Server Port')),
                FieldSet('frontport', name=_('Front Port')),
                FieldSet('rearport', name=_('Rear Port')),
                FieldSet('powerport', name=_('Power Port')),
                FieldSet('poweroutlet', name=_('Power Outlet')),
            ),
            name=_('Component Assignment')
        )
    )

    class Meta:
        model = InventoryItem
        fields = [
            'device', 'parent', 'name', 'label', 'role', 'manufacturer', 'part_id', 'serial', 'asset_tag',
            'description', 'tags',
        ]

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {}).copy()
        component_type = initial.get('component_type')
        component_id = initial.get('component_id')

        if instance:
            # When editing set the initial value for component selection
            for component_model in ContentType.objects.filter(MODULAR_COMPONENT_MODELS):
                if type(instance.component) is component_model.model_class():
                    initial[component_model.model] = instance.component
                    break
        elif component_type and component_id:
            # When adding the InventoryItem from a component page
            if content_type := ContentType.objects.filter(MODULAR_COMPONENT_MODELS).filter(pk=component_type).first():
                if component := content_type.model_class().objects.filter(pk=component_id).first():
                    initial[content_type.model] = component

        kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

        # Specifically allow editing the device of IntentoryItems
        if self.instance.pk:
            self.fields['device'].disabled = False

    def clean(self):
        super().clean()

        # Handle object assignment
        selected_objects = [
            field for field in (
                'consoleport', 'consoleserverport', 'frontport', 'interface', 'poweroutlet', 'powerport', 'rearport'
            ) if self.cleaned_data[field]
        ]
        if len(selected_objects) > 1:
            raise forms.ValidationError(_("An InventoryItem can only be assigned to a single component."))
        elif selected_objects:
            self.instance.component = self.cleaned_data[selected_objects[0]]
        else:
            self.instance.component = None


# Device component roles
#

class InventoryItemRoleForm(NetBoxModelForm):
    slug = SlugField()

    fieldsets = (
        FieldSet('name', 'slug', 'color', 'description', 'tags', name=_('Inventory Item Role')),
    )

    class Meta:
        model = InventoryItemRole
        fields = [
            'name', 'slug', 'color', 'description', 'tags',
        ]


class VirtualDeviceContextForm(TenancyForm, NetBoxModelForm):
    device = DynamicModelChoiceField(
        label=_('Device'),
        queryset=Device.objects.all(),
        selector=True
    )
    primary_ip4 = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        label=_('Primary IPv4'),
        required=False,
        query_params={
            'device_id': '$device',
            'family': '4',
        }
    )
    primary_ip6 = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        label=_('Primary IPv6'),
        required=False,
        query_params={
            'device_id': '$device',
            'family': '6',
        }
    )

    fieldsets = (
        FieldSet(
            'device', 'name', 'status', 'identifier', 'primary_ip4', 'primary_ip6', 'tags',
            name=_('Virtual Device Context')
        ),
        FieldSet('tenant_group', 'tenant', name=_('Tenancy'))
    )

    class Meta:
        model = VirtualDeviceContext
        fields = [
            'device', 'name', 'status', 'identifier', 'primary_ip4', 'primary_ip6', 'tenant_group', 'tenant',
            'comments', 'tags'
        ]
