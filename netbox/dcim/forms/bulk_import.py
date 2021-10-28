from django import forms
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.forms.array import SimpleArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe

from dcim.choices import *
from dcim.constants import *
from dcim.models import *
from extras.forms import CustomFieldModelCSVForm
from tenancy.models import Tenant
from utilities.forms import CSVChoiceField, CSVContentTypeField, CSVModelChoiceField, CSVTypedChoiceField, SlugField
from virtualization.models import Cluster
from wireless.choices import WirelessRoleChoices

__all__ = (
    'CableCSVForm',
    'ChildDeviceCSVForm',
    'ConsolePortCSVForm',
    'ConsoleServerPortCSVForm',
    'DeviceBayCSVForm',
    'DeviceCSVForm',
    'DeviceRoleCSVForm',
    'FrontPortCSVForm',
    'InterfaceCSVForm',
    'InventoryItemCSVForm',
    'LocationCSVForm',
    'ManufacturerCSVForm',
    'PlatformCSVForm',
    'PowerFeedCSVForm',
    'PowerOutletCSVForm',
    'PowerPanelCSVForm',
    'PowerPortCSVForm',
    'RackCSVForm',
    'RackReservationCSVForm',
    'RackRoleCSVForm',
    'RearPortCSVForm',
    'RegionCSVForm',
    'SiteCSVForm',
    'SiteGroupCSVForm',
    'VirtualChassisCSVForm',
)


class RegionCSVForm(CustomFieldModelCSVForm):
    parent = CSVModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of parent region'
    )

    class Meta:
        model = Region
        fields = ('name', 'slug', 'parent', 'description')


class SiteGroupCSVForm(CustomFieldModelCSVForm):
    parent = CSVModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of parent site group'
    )

    class Meta:
        model = SiteGroup
        fields = ('name', 'slug', 'parent', 'description')


class SiteCSVForm(CustomFieldModelCSVForm):
    status = CSVChoiceField(
        choices=SiteStatusChoices,
        help_text='Operational status'
    )
    region = CSVModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned region'
    )
    group = CSVModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned group'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned tenant'
    )

    class Meta:
        model = Site
        fields = (
            'name', 'slug', 'status', 'region', 'group', 'tenant', 'facility', 'time_zone', 'description',
            'physical_address', 'shipping_address', 'latitude', 'longitude', 'contact_name', 'contact_phone',
            'contact_email', 'comments',
        )
        help_texts = {
            'time_zone': mark_safe(
                'Time zone (<a href="https://en.wikipedia.org/wiki/List_of_tz_database_time_zones">available options</a>)'
            )
        }


class LocationCSVForm(CustomFieldModelCSVForm):
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        help_text='Assigned site'
    )
    parent = CSVModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Parent location',
        error_messages={
            'invalid_choice': 'Location not found.',
        }
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned tenant'
    )

    class Meta:
        model = Location
        fields = ('site', 'parent', 'name', 'slug', 'tenant', 'description')


class RackRoleCSVForm(CustomFieldModelCSVForm):
    slug = SlugField()

    class Meta:
        model = RackRole
        fields = ('name', 'slug', 'color', 'description')
        help_texts = {
            'color': mark_safe('RGB color in hexadecimal (e.g. <code>00ff00</code>)'),
        }


class RackCSVForm(CustomFieldModelCSVForm):
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name'
    )
    location = CSVModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        to_field_name='name'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of assigned tenant'
    )
    status = CSVChoiceField(
        choices=RackStatusChoices,
        help_text='Operational status'
    )
    role = CSVModelChoiceField(
        queryset=RackRole.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of assigned role'
    )
    type = CSVChoiceField(
        choices=RackTypeChoices,
        required=False,
        help_text='Rack type'
    )
    width = forms.ChoiceField(
        choices=RackWidthChoices,
        help_text='Rail-to-rail width (in inches)'
    )
    outer_unit = CSVChoiceField(
        choices=RackDimensionUnitChoices,
        required=False,
        help_text='Unit for outer dimensions'
    )

    class Meta:
        model = Rack
        fields = (
            'site', 'location', 'name', 'facility_id', 'tenant', 'status', 'role', 'type', 'serial', 'asset_tag',
            'width', 'u_height', 'desc_units', 'outer_width', 'outer_depth', 'outer_unit', 'comments',
        )

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit location queryset by assigned site
            params = {f"site__{self.fields['site'].to_field_name}": data.get('site')}
            self.fields['location'].queryset = self.fields['location'].queryset.filter(**params)


class RackReservationCSVForm(CustomFieldModelCSVForm):
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        help_text='Parent site'
    )
    location = CSVModelChoiceField(
        queryset=Location.objects.all(),
        to_field_name='name',
        required=False,
        help_text="Rack's location (if any)"
    )
    rack = CSVModelChoiceField(
        queryset=Rack.objects.all(),
        to_field_name='name',
        help_text='Rack'
    )
    units = SimpleArrayField(
        base_field=forms.IntegerField(),
        required=True,
        help_text='Comma-separated list of individual unit numbers'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned tenant'
    )

    class Meta:
        model = RackReservation
        fields = ('site', 'location', 'rack', 'units', 'tenant', 'description')

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit location queryset by assigned site
            params = {f"site__{self.fields['site'].to_field_name}": data.get('site')}
            self.fields['location'].queryset = self.fields['location'].queryset.filter(**params)

            # Limit rack queryset by assigned site and group
            params = {
                f"site__{self.fields['site'].to_field_name}": data.get('site'),
                f"location__{self.fields['location'].to_field_name}": data.get('location'),
            }
            self.fields['rack'].queryset = self.fields['rack'].queryset.filter(**params)


class ManufacturerCSVForm(CustomFieldModelCSVForm):

    class Meta:
        model = Manufacturer
        fields = ('name', 'slug', 'description')


class DeviceRoleCSVForm(CustomFieldModelCSVForm):
    slug = SlugField()

    class Meta:
        model = DeviceRole
        fields = ('name', 'slug', 'color', 'vm_role', 'description')
        help_texts = {
            'color': mark_safe('RGB color in hexadecimal (e.g. <code>00ff00</code>)'),
        }


class PlatformCSVForm(CustomFieldModelCSVForm):
    slug = SlugField()
    manufacturer = CSVModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Limit platform assignments to this manufacturer'
    )

    class Meta:
        model = Platform
        fields = ('name', 'slug', 'manufacturer', 'napalm_driver', 'napalm_args', 'description')


class BaseDeviceCSVForm(CustomFieldModelCSVForm):
    device_role = CSVModelChoiceField(
        queryset=DeviceRole.objects.all(),
        to_field_name='name',
        help_text='Assigned role'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned tenant'
    )
    manufacturer = CSVModelChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name='name',
        help_text='Device type manufacturer'
    )
    device_type = CSVModelChoiceField(
        queryset=DeviceType.objects.all(),
        to_field_name='model',
        help_text='Device type model'
    )
    platform = CSVModelChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned platform'
    )
    status = CSVChoiceField(
        choices=DeviceStatusChoices,
        help_text='Operational status'
    )
    virtual_chassis = CSVModelChoiceField(
        queryset=VirtualChassis.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Virtual chassis'
    )
    cluster = CSVModelChoiceField(
        queryset=Cluster.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Virtualization cluster'
    )

    class Meta:
        fields = []
        model = Device
        help_texts = {
            'vc_position': 'Virtual chassis position',
            'vc_priority': 'Virtual chassis priority',
        }

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit device type queryset by manufacturer
            params = {f"manufacturer__{self.fields['manufacturer'].to_field_name}": data.get('manufacturer')}
            self.fields['device_type'].queryset = self.fields['device_type'].queryset.filter(**params)


class DeviceCSVForm(BaseDeviceCSVForm):
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        help_text='Assigned site'
    )
    location = CSVModelChoiceField(
        queryset=Location.objects.all(),
        to_field_name='name',
        required=False,
        help_text="Assigned location (if any)"
    )
    rack = CSVModelChoiceField(
        queryset=Rack.objects.all(),
        to_field_name='name',
        required=False,
        help_text="Assigned rack (if any)"
    )
    face = CSVChoiceField(
        choices=DeviceFaceChoices,
        required=False,
        help_text='Mounted rack face'
    )
    airflow = CSVChoiceField(
        choices=DeviceAirflowChoices,
        required=False,
        help_text='Airflow direction'
    )

    class Meta(BaseDeviceCSVForm.Meta):
        fields = [
            'name', 'device_role', 'tenant', 'manufacturer', 'device_type', 'platform', 'serial', 'asset_tag', 'status',
            'site', 'location', 'rack', 'position', 'face', 'airflow', 'virtual_chassis', 'vc_position', 'vc_priority',
            'cluster', 'comments',
        ]

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit location queryset by assigned site
            params = {f"site__{self.fields['site'].to_field_name}": data.get('site')}
            self.fields['location'].queryset = self.fields['location'].queryset.filter(**params)

            # Limit rack queryset by assigned site and group
            params = {
                f"site__{self.fields['site'].to_field_name}": data.get('site'),
                f"location__{self.fields['location'].to_field_name}": data.get('location'),
            }
            self.fields['rack'].queryset = self.fields['rack'].queryset.filter(**params)


class ChildDeviceCSVForm(BaseDeviceCSVForm):
    parent = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        help_text='Parent device'
    )
    device_bay = CSVModelChoiceField(
        queryset=DeviceBay.objects.all(),
        to_field_name='name',
        help_text='Device bay in which this device is installed'
    )

    class Meta(BaseDeviceCSVForm.Meta):
        fields = [
            'name', 'device_role', 'tenant', 'manufacturer', 'device_type', 'platform', 'serial', 'asset_tag', 'status',
            'parent', 'device_bay', 'virtual_chassis', 'vc_position', 'vc_priority', 'cluster', 'comments',
        ]

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit device bay queryset by parent device
            params = {f"device__{self.fields['parent'].to_field_name}": data.get('parent')}
            self.fields['device_bay'].queryset = self.fields['device_bay'].queryset.filter(**params)

    def clean(self):
        super().clean()

        # Set parent_bay reverse relationship
        device_bay = self.cleaned_data.get('device_bay')
        if device_bay:
            self.instance.parent_bay = device_bay

        # Inherit site and rack from parent device
        parent = self.cleaned_data.get('parent')
        if parent:
            self.instance.site = parent.site
            self.instance.rack = parent.rack


#
# Device components
#

class ConsolePortCSVForm(CustomFieldModelCSVForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name'
    )
    type = CSVChoiceField(
        choices=ConsolePortTypeChoices,
        required=False,
        help_text='Port type'
    )
    speed = CSVTypedChoiceField(
        choices=ConsolePortSpeedChoices,
        coerce=int,
        empty_value=None,
        required=False,
        help_text='Port speed in bps'
    )

    class Meta:
        model = ConsolePort
        fields = ('device', 'name', 'label', 'type', 'speed', 'mark_connected', 'description')


class ConsoleServerPortCSVForm(CustomFieldModelCSVForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name'
    )
    type = CSVChoiceField(
        choices=ConsolePortTypeChoices,
        required=False,
        help_text='Port type'
    )
    speed = CSVTypedChoiceField(
        choices=ConsolePortSpeedChoices,
        coerce=int,
        empty_value=None,
        required=False,
        help_text='Port speed in bps'
    )

    class Meta:
        model = ConsoleServerPort
        fields = ('device', 'name', 'label', 'type', 'speed', 'mark_connected', 'description')


class PowerPortCSVForm(CustomFieldModelCSVForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name'
    )
    type = CSVChoiceField(
        choices=PowerPortTypeChoices,
        required=False,
        help_text='Port type'
    )

    class Meta:
        model = PowerPort
        fields = (
            'device', 'name', 'label', 'type', 'mark_connected', 'maximum_draw', 'allocated_draw', 'description',
        )


class PowerOutletCSVForm(CustomFieldModelCSVForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name'
    )
    type = CSVChoiceField(
        choices=PowerOutletTypeChoices,
        required=False,
        help_text='Outlet type'
    )
    power_port = CSVModelChoiceField(
        queryset=PowerPort.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Local power port which feeds this outlet'
    )
    feed_leg = CSVChoiceField(
        choices=PowerOutletFeedLegChoices,
        required=False,
        help_text='Electrical phase (for three-phase circuits)'
    )

    class Meta:
        model = PowerOutlet
        fields = ('device', 'name', 'label', 'type', 'mark_connected', 'power_port', 'feed_leg', 'description')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit PowerPort choices to those belonging to this device (or VC master)
        if self.is_bound:
            try:
                device = self.fields['device'].to_python(self.data['device'])
            except forms.ValidationError:
                device = None
        else:
            try:
                device = self.instance.device
            except Device.DoesNotExist:
                device = None

        if device:
            self.fields['power_port'].queryset = PowerPort.objects.filter(
                device__in=[device, device.get_vc_master()]
            )
        else:
            self.fields['power_port'].queryset = PowerPort.objects.none()


class InterfaceCSVForm(CustomFieldModelCSVForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name'
    )
    parent = CSVModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Parent interface'
    )
    bridge = CSVModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Bridged interface'
    )
    lag = CSVModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Parent LAG interface'
    )
    type = CSVChoiceField(
        choices=InterfaceTypeChoices,
        help_text='Physical medium'
    )
    mode = CSVChoiceField(
        choices=InterfaceModeChoices,
        required=False,
        help_text='IEEE 802.1Q operational mode (for L2 interfaces)'
    )
    rf_role = CSVChoiceField(
        choices=WirelessRoleChoices,
        required=False,
        help_text='Wireless role (AP/station)'
    )

    class Meta:
        model = Interface
        fields = (
            'device', 'name', 'label', 'parent', 'bridge', 'lag', 'type', 'enabled', 'mark_connected', 'mac_address',
            'wwn', 'mtu', 'mgmt_only', 'description', 'mode', 'rf_role', 'rf_channel', 'rf_channel_frequency',
            'rf_channel_width', 'tx_power',
        )

    def clean_enabled(self):
        # Make sure enabled is True when it's not included in the uploaded data
        if 'enabled' not in self.data:
            return True
        else:
            return self.cleaned_data['enabled']


class FrontPortCSVForm(CustomFieldModelCSVForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name'
    )
    rear_port = CSVModelChoiceField(
        queryset=RearPort.objects.all(),
        to_field_name='name',
        help_text='Corresponding rear port'
    )
    type = CSVChoiceField(
        choices=PortTypeChoices,
        help_text='Physical medium classification'
    )

    class Meta:
        model = FrontPort
        fields = (
            'device', 'name', 'label', 'type', 'color', 'mark_connected', 'rear_port', 'rear_port_position',
            'description',
        )
        help_texts = {
            'rear_port_position': 'Mapped position on corresponding rear port',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit RearPort choices to those belonging to this device (or VC master)
        if self.is_bound:
            try:
                device = self.fields['device'].to_python(self.data['device'])
            except forms.ValidationError:
                device = None
        else:
            try:
                device = self.instance.device
            except Device.DoesNotExist:
                device = None

        if device:
            self.fields['rear_port'].queryset = RearPort.objects.filter(
                device__in=[device, device.get_vc_master()]
            )
        else:
            self.fields['rear_port'].queryset = RearPort.objects.none()


class RearPortCSVForm(CustomFieldModelCSVForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name'
    )
    type = CSVChoiceField(
        help_text='Physical medium classification',
        choices=PortTypeChoices,
    )

    class Meta:
        model = RearPort
        fields = ('device', 'name', 'label', 'type', 'color', 'mark_connected', 'positions', 'description')
        help_texts = {
            'positions': 'Number of front ports which may be mapped'
        }


class DeviceBayCSVForm(CustomFieldModelCSVForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name'
    )
    installed_device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Child device installed within this bay',
        error_messages={
            'invalid_choice': 'Child device not found.',
        }
    )

    class Meta:
        model = DeviceBay
        fields = ('device', 'name', 'label', 'installed_device', 'description')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit installed device choices to devices of the correct type and location
        if self.is_bound:
            try:
                device = self.fields['device'].to_python(self.data['device'])
            except forms.ValidationError:
                device = None
        else:
            try:
                device = self.instance.device
            except Device.DoesNotExist:
                device = None

        if device:
            self.fields['installed_device'].queryset = Device.objects.filter(
                site=device.site,
                rack=device.rack,
                parent_bay__isnull=True,
                device_type__u_height=0,
                device_type__subdevice_role=SubdeviceRoleChoices.ROLE_CHILD
            ).exclude(pk=device.pk)
        else:
            self.fields['installed_device'].queryset = Interface.objects.none()


class InventoryItemCSVForm(CustomFieldModelCSVForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name'
    )
    manufacturer = CSVModelChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name='name',
        required=False
    )
    parent = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Parent inventory item'
    )

    class Meta:
        model = InventoryItem
        fields = (
            'device', 'name', 'label', 'manufacturer', 'part_id', 'serial', 'asset_tag', 'discovered', 'description',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit parent choices to inventory items belonging to this device
        device = None
        if self.is_bound and 'device' in self.data:
            try:
                device = self.fields['device'].to_python(self.data['device'])
            except forms.ValidationError:
                pass
        if device:
            self.fields['parent'].queryset = InventoryItem.objects.filter(device=device)
        else:
            self.fields['parent'].queryset = InventoryItem.objects.none()


class CableCSVForm(CustomFieldModelCSVForm):
    # Termination A
    side_a_device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        help_text='Side A device'
    )
    side_a_type = CSVContentTypeField(
        queryset=ContentType.objects.all(),
        limit_choices_to=CABLE_TERMINATION_MODELS,
        help_text='Side A type'
    )
    side_a_name = forms.CharField(
        help_text='Side A component name'
    )

    # Termination B
    side_b_device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        help_text='Side B device'
    )
    side_b_type = CSVContentTypeField(
        queryset=ContentType.objects.all(),
        limit_choices_to=CABLE_TERMINATION_MODELS,
        help_text='Side B type'
    )
    side_b_name = forms.CharField(
        help_text='Side B component name'
    )

    # Cable attributes
    status = CSVChoiceField(
        choices=LinkStatusChoices,
        required=False,
        help_text='Connection status'
    )
    type = CSVChoiceField(
        choices=CableTypeChoices,
        required=False,
        help_text='Physical medium classification'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned tenant'
    )
    length_unit = CSVChoiceField(
        choices=CableLengthUnitChoices,
        required=False,
        help_text='Length unit'
    )

    class Meta:
        model = Cable
        fields = [
            'side_a_device', 'side_a_type', 'side_a_name', 'side_b_device', 'side_b_type', 'side_b_name', 'type',
            'status', 'tenant', 'label', 'color', 'length', 'length_unit',
        ]
        help_texts = {
            'color': mark_safe('RGB color in hexadecimal (e.g. <code>00ff00</code>)'),
        }

    def _clean_side(self, side):
        """
        Derive a Cable's A/B termination objects.

        :param side: 'a' or 'b'
        """
        assert side in 'ab', f"Invalid side designation: {side}"

        device = self.cleaned_data.get(f'side_{side}_device')
        content_type = self.cleaned_data.get(f'side_{side}_type')
        name = self.cleaned_data.get(f'side_{side}_name')
        if not device or not content_type or not name:
            return None

        model = content_type.model_class()
        try:
            termination_object = model.objects.get(device=device, name=name)
            if termination_object.cable is not None:
                raise forms.ValidationError(f"Side {side.upper()}: {device} {termination_object} is already connected")
        except ObjectDoesNotExist:
            raise forms.ValidationError(f"{side.upper()} side termination not found: {device} {name}")

        setattr(self.instance, f'termination_{side}', termination_object)
        return termination_object

    def clean_side_a_name(self):
        return self._clean_side('a')

    def clean_side_b_name(self):
        return self._clean_side('b')

    def clean_length_unit(self):
        # Avoid trying to save as NULL
        length_unit = self.cleaned_data.get('length_unit', None)
        return length_unit if length_unit is not None else ''


class VirtualChassisCSVForm(CustomFieldModelCSVForm):
    master = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Master device'
    )

    class Meta:
        model = VirtualChassis
        fields = ('name', 'domain', 'master')


class PowerPanelCSVForm(CustomFieldModelCSVForm):
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        help_text='Name of parent site'
    )
    location = CSVModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        to_field_name='name'
    )

    class Meta:
        model = PowerPanel
        fields = ('site', 'location', 'name')

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit group queryset by assigned site
            params = {f"site__{self.fields['site'].to_field_name}": data.get('site')}
            self.fields['location'].queryset = self.fields['location'].queryset.filter(**params)


class PowerFeedCSVForm(CustomFieldModelCSVForm):
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        help_text='Assigned site'
    )
    power_panel = CSVModelChoiceField(
        queryset=PowerPanel.objects.all(),
        to_field_name='name',
        help_text='Upstream power panel'
    )
    location = CSVModelChoiceField(
        queryset=Location.objects.all(),
        to_field_name='name',
        required=False,
        help_text="Rack's location (if any)"
    )
    rack = CSVModelChoiceField(
        queryset=Rack.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Rack'
    )
    status = CSVChoiceField(
        choices=PowerFeedStatusChoices,
        help_text='Operational status'
    )
    type = CSVChoiceField(
        choices=PowerFeedTypeChoices,
        help_text='Primary or redundant'
    )
    supply = CSVChoiceField(
        choices=PowerFeedSupplyChoices,
        help_text='Supply type (AC/DC)'
    )
    phase = CSVChoiceField(
        choices=PowerFeedPhaseChoices,
        help_text='Single or three-phase'
    )

    class Meta:
        model = PowerFeed
        fields = (
            'site', 'power_panel', 'location', 'rack', 'name', 'status', 'type', 'mark_connected', 'supply', 'phase',
            'voltage', 'amperage', 'max_utilization', 'comments',
        )

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit power_panel queryset by site
            params = {f"site__{self.fields['site'].to_field_name}": data.get('site')}
            self.fields['power_panel'].queryset = self.fields['power_panel'].queryset.filter(**params)

            # Limit location queryset by site
            params = {f"site__{self.fields['site'].to_field_name}": data.get('site')}
            self.fields['location'].queryset = self.fields['location'].queryset.filter(**params)

            # Limit rack queryset by site and group
            params = {
                f"site__{self.fields['site'].to_field_name}": data.get('site'),
                f"location__{self.fields['location'].to_field_name}": data.get('location'),
            }
            self.fields['rack'].queryset = self.fields['rack'].queryset.filter(**params)
