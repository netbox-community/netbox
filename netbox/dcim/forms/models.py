from django import forms
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from timezone_field import TimeZoneFormField

from dcim.choices import *
from dcim.constants import *
from dcim.models import *
from extras.models import Tag
from ipam.models import ASN, IPAddress, VLAN, VLANGroup, VRF
from netbox.forms import NetBoxModelForm
from tenancy.forms import TenancyForm
from utilities.forms import (
    APISelect, add_blank_choice, BootstrapMixin, ClearableFileInput, CommentField, ContentTypeChoiceField,
    DynamicModelChoiceField, DynamicModelMultipleChoiceField, JSONField, NumericArrayField, SelectWithPK, SmallTextarea,
    SlugField, StaticSelect, SelectSpeedWidget,
)
from virtualization.models import Cluster, ClusterGroup
from wireless.models import WirelessLAN, WirelessLANGroup
from .common import InterfaceCommonForm

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
)

INTERFACE_MODE_HELP_TEXT = """
Access: One untagged VLAN<br />
Tagged: One untagged VLAN and/or one or more tagged VLANs<br />
Tagged (All): Implies all VLANs are available (w/optional untagged VLAN)
"""


class RegionForm(NetBoxModelForm):
    parent = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False
    )
    slug = SlugField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Region
        fields = (
            'parent', 'name', 'slug', 'description', 'tags',
        )


class SiteGroupForm(NetBoxModelForm):
    parent = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False
    )
    slug = SlugField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = SiteGroup
        fields = (
            'parent', 'name', 'slug', 'description', 'tags',
        )


class SiteForm(TenancyForm, NetBoxModelForm):
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False
    )
    group = DynamicModelChoiceField(
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
        choices=add_blank_choice(TimeZoneFormField().choices),
        required=False,
        widget=StaticSelect()
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    fieldsets = (
        ('Site', (
            'name', 'slug', 'status', 'region', 'group', 'facility', 'asns', 'time_zone', 'description', 'tags',
        )),
        ('Tenancy', ('tenant_group', 'tenant')),
        ('Contact Info', ('physical_address', 'shipping_address', 'latitude', 'longitude')),
    )

    class Meta:
        model = Site
        fields = (
            'name', 'slug', 'status', 'region', 'group', 'tenant_group', 'tenant', 'facility', 'asns', 'time_zone',
            'description', 'physical_address', 'shipping_address', 'latitude', 'longitude', 'comments', 'tags',
        )
        widgets = {
            'physical_address': SmallTextarea(
                attrs={
                    'rows': 3,
                }
            ),
            'shipping_address': SmallTextarea(
                attrs={
                    'rows': 3,
                }
            ),
            'status': StaticSelect(),
            'time_zone': StaticSelect(),
        }
        help_texts = {
            'name': "Full name of the site",
            'facility': "Data center provider and facility (e.g. Equinix NY7)",
            'time_zone': "Local time zone",
            'description': "Short description (will appear in sites list)",
            'physical_address': "Physical location of the building (e.g. for GPS)",
            'shipping_address': "If different from the physical address",
            'latitude': "Latitude in decimal format (xx.yyyyyy)",
            'longitude': "Longitude in decimal format (xx.yyyyyy)"
        }


class LocationForm(TenancyForm, NetBoxModelForm):
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    parent = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    slug = SlugField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    fieldsets = (
        ('Location', (
            'region', 'site_group', 'site', 'parent', 'name', 'slug', 'description', 'tags',
        )),
        ('Tenancy', ('tenant_group', 'tenant')),
    )

    class Meta:
        model = Location
        fields = (
            'region', 'site_group', 'site', 'parent', 'name', 'slug', 'description', 'tenant_group', 'tenant', 'tags',
        )


class RackRoleForm(NetBoxModelForm):
    slug = SlugField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = RackRole
        fields = [
            'name', 'slug', 'color', 'description', 'tags',
        ]


class RackForm(TenancyForm, NetBoxModelForm):
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    role = DynamicModelChoiceField(
        queryset=RackRole.objects.all(),
        required=False
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Rack
        fields = [
            'region', 'site_group', 'site', 'location', 'name', 'facility_id', 'tenant_group', 'tenant', 'status',
            'role', 'serial', 'asset_tag', 'type', 'width', 'u_height', 'desc_units', 'outer_width', 'outer_depth',
            'outer_unit', 'comments', 'tags',
        ]
        help_texts = {
            'site': "The site at which the rack exists",
            'name': "Organizational rack name",
            'facility_id': "The unique rack ID assigned by the facility",
            'u_height': "Height in rack units",
        }
        widgets = {
            'status': StaticSelect(),
            'type': StaticSelect(),
            'width': StaticSelect(),
            'outer_unit': StaticSelect(),
        }


class RackReservationForm(TenancyForm, NetBoxModelForm):
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        query_params={
            'site_id': '$site',
            'location_id': '$location',
        }
    )
    units = NumericArrayField(
        base_field=forms.IntegerField(),
        help_text="Comma-separated list of numeric unit IDs. A range may be specified using a hyphen."
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.order_by(
            'username'
        ),
        widget=StaticSelect()
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    fieldsets = (
        ('Reservation', ('region', 'site', 'location', 'rack', 'units', 'user', 'description', 'tags')),
        ('Tenancy', ('tenant_group', 'tenant')),
    )

    class Meta:
        model = RackReservation
        fields = [
            'region', 'site_group', 'site', 'location', 'rack', 'units', 'user', 'tenant_group', 'tenant',
            'description', 'tags',
        ]


class ManufacturerForm(NetBoxModelForm):
    slug = SlugField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Manufacturer
        fields = [
            'name', 'slug', 'description', 'tags',
        ]


class DeviceTypeForm(NetBoxModelForm):
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all()
    )
    slug = SlugField(
        slug_source='model'
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    fieldsets = (
        ('Device Type', (
            'manufacturer', 'model', 'slug', 'part_number', 'tags',
        )),
        ('Chassis', (
            'u_height', 'is_full_depth', 'subdevice_role', 'airflow',
        )),
        ('Images', ('front_image', 'rear_image')),
    )

    class Meta:
        model = DeviceType
        fields = [
            'manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'subdevice_role', 'airflow',
            'front_image', 'rear_image', 'comments', 'tags',
        ]
        widgets = {
            'subdevice_role': StaticSelect(),
            'front_image': ClearableFileInput(attrs={
                'accept': DEVICETYPE_IMAGE_FORMATS
            }),
            'rear_image': ClearableFileInput(attrs={
                'accept': DEVICETYPE_IMAGE_FORMATS
            })
        }


class ModuleTypeForm(NetBoxModelForm):
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all()
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = ModuleType
        fields = [
            'manufacturer', 'model', 'part_number', 'comments', 'tags',
        ]


class DeviceRoleForm(NetBoxModelForm):
    slug = SlugField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = DeviceRole
        fields = [
            'name', 'slug', 'color', 'vm_role', 'description', 'tags',
        ]


class PlatformForm(NetBoxModelForm):
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False
    )
    slug = SlugField(
        max_length=64
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Platform
        fields = [
            'name', 'slug', 'manufacturer', 'napalm_driver', 'napalm_args', 'description', 'tags',
        ]
        widgets = {
            'napalm_args': SmallTextarea(),
        }


class DeviceForm(TenancyForm, NetBoxModelForm):
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    location = DynamicModelChoiceField(
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
        queryset=Rack.objects.all(),
        required=False,
        query_params={
            'site_id': '$site',
            'location_id': '$location',
        }
    )
    position = forms.IntegerField(
        required=False,
        help_text="The lowest-numbered unit occupied by the device",
        widget=APISelect(
            api_url='/api/dcim/racks/{{rack}}/elevation/',
            attrs={
                'disabled-indicator': 'device',
                'data-dynamic-params': '[{"fieldName":"face","queryParam":"face"}]'
            }
        )
    )
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        initial_params={
            'device_types': '$device_type'
        }
    )
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        query_params={
            'manufacturer_id': '$manufacturer'
        }
    )
    device_role = DynamicModelChoiceField(
        queryset=DeviceRole.objects.all()
    )
    platform = DynamicModelChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': ['$manufacturer', 'null']
        }
    )
    cluster_group = DynamicModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        null_option='None',
        initial_params={
            'clusters': '$cluster'
        }
    )
    cluster = DynamicModelChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        query_params={
            'group_id': '$cluster_group'
        }
    )
    comments = CommentField()
    local_context_data = JSONField(
        required=False,
        label=''
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Device
        fields = [
            'name', 'device_role', 'device_type', 'serial', 'asset_tag', 'region', 'site_group', 'site', 'rack',
            'location', 'position', 'face', 'status', 'airflow', 'platform', 'primary_ip4', 'primary_ip6',
            'cluster_group', 'cluster', 'tenant_group', 'tenant', 'comments', 'tags', 'local_context_data'
        ]
        help_texts = {
            'device_role': "The function this device serves",
            'serial': "Chassis serial number",
            'local_context_data': "Local config context data overwrites all source contexts in the final rendered "
                                  "config context",
        }
        widgets = {
            'face': StaticSelect(),
            'status': StaticSelect(),
            'airflow': StaticSelect(),
            'primary_ip4': StaticSelect(),
            'primary_ip6': StaticSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:

            # Compile list of choices for primary IPv4 and IPv6 addresses
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

            # If editing an existing device, exclude it from the list of occupied rack units. This ensures that a device
            # can be flipped from one face to another.
            self.fields['position'].widget.add_query_param('exclude', self.instance.pk)

            # Limit platform by manufacturer
            self.fields['platform'].queryset = Platform.objects.filter(
                Q(manufacturer__isnull=True) | Q(manufacturer=self.instance.device_type.manufacturer)
            )

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

        # Rack position
        position = self.data.get('position') or self.initial.get('position')
        if position:
            self.fields['position'].widget.choices = [(position, f'U{position}')]


class ModuleForm(NetBoxModelForm):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        initial_params={
            'modulebays': '$module_bay'
        }
    )
    module_bay = DynamicModelChoiceField(
        queryset=ModuleBay.objects.all(),
        query_params={
            'device_id': '$device'
        }
    )
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        initial_params={
            'module_types': '$module_type'
        }
    )
    module_type = DynamicModelChoiceField(
        queryset=ModuleType.objects.all(),
        query_params={
            'manufacturer_id': '$manufacturer'
        }
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )
    replicate_components = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Automatically populate components associated with this module type"
    )

    class Meta:
        model = Module
        fields = [
            'device', 'module_bay', 'manufacturer', 'module_type', 'serial', 'asset_tag', 'tags',
            'replicate_components', 'comments',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['replicate_components'].initial = False
            self.fields['replicate_components'].disabled = True

    def save(self, *args, **kwargs):

        # If replicate_components is False, disable automatic component replication on the instance
        if self.instance.pk or not self.cleaned_data['replicate_components']:
            self.instance._disable_replication = True

        return super().save(*args, **kwargs)


class CableForm(TenancyForm, NetBoxModelForm):
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Cable
        fields = [
            'type', 'status', 'tenant_group', 'tenant', 'label', 'color', 'length', 'length_unit', 'tags',
        ]
        widgets = {
            'status': StaticSelect,
            'type': StaticSelect,
            'length_unit': StaticSelect,
        }
        error_messages = {
            'length': {
                'max_value': 'Maximum length is 32767 (any unit)'
            }
        }


class PowerPanelForm(NetBoxModelForm):
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    fieldsets = (
        ('Power Panel', ('region', 'site_group', 'site', 'location', 'name', 'tags')),
    )

    class Meta:
        model = PowerPanel
        fields = [
            'region', 'site_group', 'site', 'location', 'name', 'tags',
        ]


class PowerFeedForm(NetBoxModelForm):
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites__powerpanel': '$power_panel'
        }
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        initial_params={
            'powerpanel': '$power_panel'
        },
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    power_panel = DynamicModelChoiceField(
        queryset=PowerPanel.objects.all(),
        query_params={
            'site_id': '$site'
        }
    )
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    fieldsets = (
        ('Power Panel', ('region', 'site', 'power_panel')),
        ('Power Feed', ('rack', 'name', 'status', 'type', 'mark_connected', 'tags')),
        ('Characteristics', ('supply', 'voltage', 'amperage', 'phase', 'max_utilization')),
    )

    class Meta:
        model = PowerFeed
        fields = [
            'region', 'site_group', 'site', 'power_panel', 'rack', 'name', 'status', 'type', 'mark_connected', 'supply',
            'phase', 'voltage', 'amperage', 'max_utilization', 'comments', 'tags',
        ]
        widgets = {
            'status': StaticSelect(),
            'type': StaticSelect(),
            'supply': StaticSelect(),
            'phase': StaticSelect(),
        }


#
# Virtual chassis
#

class VirtualChassisForm(NetBoxModelForm):
    master = forms.ModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = VirtualChassis
        fields = [
            'name', 'domain', 'master', 'tags',
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


class VCMemberSelectForm(BootstrapMixin, forms.Form):
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site'
        }
    )
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        query_params={
            'site_id': '$site',
            'rack_id': '$rack',
            'virtual_chassis_id': 'null',
        }
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


class ConsolePortTemplateForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = ConsolePortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
            'module_type': forms.HiddenInput(),
            'type': StaticSelect,
        }


class ConsoleServerPortTemplateForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = ConsoleServerPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
            'module_type': forms.HiddenInput(),
            'type': StaticSelect,
        }


class PowerPortTemplateForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = PowerPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
            'module_type': forms.HiddenInput(),
            'type': StaticSelect(),
        }


class PowerOutletTemplateForm(BootstrapMixin, forms.ModelForm):
    power_port = DynamicModelChoiceField(
        queryset=PowerPortTemplate.objects.all(),
        required=False,
        query_params={
            'devicetype_id': '$device_type',
        }
    )

    class Meta:
        model = PowerOutletTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'power_port', 'feed_leg', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
            'module_type': forms.HiddenInput(),
            'type': StaticSelect(),
            'feed_leg': StaticSelect(),
        }


class InterfaceTemplateForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = InterfaceTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'mgmt_only', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
            'module_type': forms.HiddenInput(),
            'type': StaticSelect(),
        }


class FrontPortTemplateForm(BootstrapMixin, forms.ModelForm):
    rear_port = DynamicModelChoiceField(
        queryset=RearPortTemplate.objects.all(),
        required=False,
        query_params={
            'devicetype_id': '$device_type',
        }
    )

    class Meta:
        model = FrontPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'color', 'rear_port', 'rear_port_position',
            'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
            'module_type': forms.HiddenInput(),
            'type': StaticSelect(),
        }


class RearPortTemplateForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = RearPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'color', 'positions', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
            'module_type': forms.HiddenInput(),
            'type': StaticSelect(),
        }


class ModuleBayTemplateForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = ModuleBayTemplate
        fields = [
            'device_type', 'name', 'label', 'position', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
        }


class DeviceBayTemplateForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = DeviceBayTemplate
        fields = [
            'device_type', 'name', 'label', 'description',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
        }


class InventoryItemTemplateForm(BootstrapMixin, forms.ModelForm):
    parent = DynamicModelChoiceField(
        queryset=InventoryItem.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        }
    )
    role = DynamicModelChoiceField(
        queryset=InventoryItemRole.objects.all(),
        required=False
    )
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False
    )
    component_type = ContentTypeChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=MODULAR_COMPONENT_TEMPLATE_MODELS,
        required=False,
        widget=forms.HiddenInput
    )
    component_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput
    )

    fieldsets = (
        ('Inventory Item', ('device_type', 'parent', 'name', 'label', 'role', 'description')),
        ('Hardware', ('manufacturer', 'part_id')),
    )

    class Meta:
        model = InventoryItemTemplate
        fields = [
            'device_type', 'parent', 'name', 'label', 'role', 'manufacturer', 'part_id', 'description',
            'component_type', 'component_id',
        ]
        widgets = {
            'device_type': forms.HiddenInput(),
        }


#
# Device components
#

class ConsolePortForm(NetBoxModelForm):
    module = DynamicModelChoiceField(
        queryset=Module.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = ConsolePort
        fields = [
            'device', 'module', 'name', 'label', 'type', 'speed', 'mark_connected', 'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
            'type': StaticSelect(),
            'speed': StaticSelect(),
        }


class ConsoleServerPortForm(NetBoxModelForm):
    module = DynamicModelChoiceField(
        queryset=Module.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = ConsoleServerPort
        fields = [
            'device', 'module', 'name', 'label', 'type', 'speed', 'mark_connected', 'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
            'type': StaticSelect(),
            'speed': StaticSelect(),
        }


class PowerPortForm(NetBoxModelForm):
    module = DynamicModelChoiceField(
        queryset=Module.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = PowerPort
        fields = [
            'device', 'module', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'mark_connected',
            'description',
            'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
            'type': StaticSelect(),
        }


class PowerOutletForm(NetBoxModelForm):
    module = DynamicModelChoiceField(
        queryset=Module.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )
    power_port = DynamicModelChoiceField(
        queryset=PowerPort.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = PowerOutlet
        fields = [
            'device', 'module', 'name', 'label', 'type', 'power_port', 'feed_leg', 'mark_connected', 'description',
            'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
            'type': StaticSelect(),
            'feed_leg': StaticSelect(),
        }


class InterfaceForm(InterfaceCommonForm, NetBoxModelForm):
    module = DynamicModelChoiceField(
        queryset=Module.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )
    parent = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label='Parent interface',
        query_params={
            'device_id': '$device',
        }
    )
    bridge = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label='Bridged interface',
        query_params={
            'device_id': '$device',
        }
    )
    lag = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label='LAG interface',
        query_params={
            'device_id': '$device',
            'type': 'lag',
        }
    )
    wireless_lan_group = DynamicModelChoiceField(
        queryset=WirelessLANGroup.objects.all(),
        required=False,
        label='Wireless LAN group'
    )
    wireless_lans = DynamicModelMultipleChoiceField(
        queryset=WirelessLAN.objects.all(),
        required=False,
        label='Wireless LANs',
        query_params={
            'group_id': '$wireless_lan_group',
        }
    )
    vlan_group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        label='VLAN group'
    )
    untagged_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label='Untagged VLAN',
        query_params={
            'group_id': '$vlan_group',
            'available_on_device': '$device',
        }
    )
    tagged_vlans = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label='Tagged VLANs',
        query_params={
            'group_id': '$vlan_group',
            'available_on_device': '$device',
        }
    )
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF'
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    fieldsets = (
        ('Interface', ('device', 'module', 'name', 'type', 'speed', 'duplex', 'label', 'description', 'tags')),
        ('Addressing', ('vrf', 'mac_address', 'wwn')),
        ('Operation', ('mtu', 'tx_power', 'enabled', 'mgmt_only', 'mark_connected')),
        ('Related Interfaces', ('parent', 'bridge', 'lag')),
        ('802.1Q Switching', ('mode', 'vlan_group', 'untagged_vlan', 'tagged_vlans')),
        ('Wireless', (
            'rf_role', 'rf_channel', 'rf_channel_frequency', 'rf_channel_width', 'wireless_lan_group', 'wireless_lans',
        )),
    )

    class Meta:
        model = Interface
        fields = [
            'device', 'module', 'name', 'label', 'type', 'speed', 'duplex', 'enabled', 'parent', 'bridge', 'lag',
            'mac_address', 'wwn', 'mtu', 'mgmt_only', 'mark_connected', 'description', 'mode', 'rf_role', 'rf_channel',
            'rf_channel_frequency', 'rf_channel_width', 'tx_power', 'wireless_lans', 'untagged_vlan', 'tagged_vlans',
            'vrf', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
            'type': StaticSelect(),
            'speed': SelectSpeedWidget(),
            'duplex': StaticSelect(),
            'mode': StaticSelect(),
            'rf_role': StaticSelect(),
            'rf_channel': StaticSelect(),
        }
        labels = {
            'mode': '802.1Q Mode',
        }
        help_texts = {
            'mode': INTERFACE_MODE_HELP_TEXT,
            'rf_channel_frequency': "Populated by selected channel (if set)",
            'rf_channel_width': "Populated by selected channel (if set)",
        }


class FrontPortForm(NetBoxModelForm):
    module = DynamicModelChoiceField(
        queryset=Module.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )
    rear_port = DynamicModelChoiceField(
        queryset=RearPort.objects.all(),
        query_params={
            'device_id': '$device',
        }
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = FrontPort
        fields = [
            'device', 'module', 'name', 'label', 'type', 'color', 'rear_port', 'rear_port_position', 'mark_connected',
            'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
            'type': StaticSelect(),
        }


class RearPortForm(NetBoxModelForm):
    module = DynamicModelChoiceField(
        queryset=Module.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = RearPort
        fields = [
            'device', 'module', 'name', 'label', 'type', 'color', 'positions', 'mark_connected', 'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
            'type': StaticSelect(),
        }


class ModuleBayForm(NetBoxModelForm):
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = ModuleBay
        fields = [
            'device', 'name', 'label', 'position', 'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
        }


class DeviceBayForm(NetBoxModelForm):
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = DeviceBay
        fields = [
            'device', 'name', 'label', 'description', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
        }


class PopulateDeviceBayForm(BootstrapMixin, forms.Form):
    installed_device = forms.ModelChoiceField(
        queryset=Device.objects.all(),
        label='Child Device',
        help_text="Child devices must first be created and assigned to the site/rack of the parent device.",
        widget=StaticSelect(),
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


class InventoryItemForm(NetBoxModelForm):
    parent = DynamicModelChoiceField(
        queryset=InventoryItem.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        }
    )
    role = DynamicModelChoiceField(
        queryset=InventoryItemRole.objects.all(),
        required=False
    )
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False
    )
    component_type = ContentTypeChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=MODULAR_COMPONENT_MODELS,
        required=False,
        widget=forms.HiddenInput
    )
    component_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    fieldsets = (
        ('Inventory Item', ('device', 'parent', 'name', 'label', 'role', 'description', 'tags')),
        ('Hardware', ('manufacturer', 'part_id', 'serial', 'asset_tag')),
    )

    class Meta:
        model = InventoryItem
        fields = [
            'device', 'parent', 'name', 'label', 'role', 'manufacturer', 'part_id', 'serial', 'asset_tag',
            'description', 'component_type', 'component_id', 'tags',
        ]
        widgets = {
            'device': forms.HiddenInput(),
        }


#
# Device component roles
#

class InventoryItemRoleForm(NetBoxModelForm):
    slug = SlugField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = InventoryItemRole
        fields = [
            'name', 'slug', 'color', 'description', 'tags',
        ]
