from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels


class SitePanel(panels.ObjectAttributesPanel):
    region = attrs.NestedObjectAttr('region', linkify=True)
    group = attrs.NestedObjectAttr('group', linkify=True)
    name = attrs.TextAttr('name')
    status = attrs.ChoiceAttr('status')
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')
    facility = attrs.TextAttr('facility')
    description = attrs.TextAttr('description')
    timezone = attrs.TimezoneAttr('time_zone')
    physical_address = attrs.AddressAttr('physical_address', map_url=True)
    shipping_address = attrs.AddressAttr('shipping_address', map_url=True)
    gps_coordinates = attrs.GPSCoordinatesAttr()


class LocationPanel(panels.NestedGroupObjectPanel):
    site = attrs.RelatedObjectAttr('site', linkify=True, grouped_by='group')
    status = attrs.ChoiceAttr('status')
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')
    facility = attrs.TextAttr('facility')


class RackDimensionsPanel(panels.ObjectAttributesPanel):
    form_factor = attrs.ChoiceAttr('form_factor')
    width = attrs.ChoiceAttr('width')
    height = attrs.TextAttr('u_height', format_string='{}U', label=_('Height'))
    outer_width = attrs.NumericAttr('outer_width', unit_accessor='get_outer_unit_display')
    outer_height = attrs.NumericAttr('outer_height', unit_accessor='get_outer_unit_display')
    outer_depth = attrs.NumericAttr('outer_depth', unit_accessor='get_outer_unit_display')
    mounting_depth = attrs.TextAttr('mounting_depth', format_string=_('{} millimeters'))


class RackNumberingPanel(panels.ObjectAttributesPanel):
    starting_unit = attrs.TextAttr('starting_unit')
    desc_units = attrs.BooleanAttr('desc_units', label=_('Descending units'))


class RackPanel(panels.ObjectAttributesPanel):
    region = attrs.NestedObjectAttr('site.region', linkify=True)
    site = attrs.RelatedObjectAttr('site', linkify=True, grouped_by='group')
    location = attrs.NestedObjectAttr('location', linkify=True)
    name = attrs.TextAttr('name')
    facility = attrs.TextAttr('facility', label=_('Facility ID'))
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')
    status = attrs.ChoiceAttr('status')
    rack_type = attrs.RelatedObjectAttr('rack_type', linkify=True, grouped_by='manufacturer')
    role = attrs.RelatedObjectAttr('role', linkify=True)
    description = attrs.TextAttr('description')
    serial = attrs.TextAttr('serial', label=_('Serial number'), style='font-monospace', copy_button=True)
    asset_tag = attrs.TextAttr('asset_tag', style='font-monospace', copy_button=True)
    airflow = attrs.ChoiceAttr('airflow')
    space_utilization = attrs.UtilizationAttr('get_utilization')
    power_utilization = attrs.UtilizationAttr('get_power_utilization')


class RackWeightPanel(panels.ObjectAttributesPanel):
    weight = attrs.NumericAttr('weight', unit_accessor='get_weight_unit_display')
    max_weight = attrs.NumericAttr('max_weight', unit_accessor='get_weight_unit_display', label=_('Maximum weight'))
    total_weight = attrs.TemplatedAttr('total_weight', template_name='dcim/rack/attrs/total_weight.html')


class RackRolePanel(panels.OrganizationalObjectPanel):
    color = attrs.ColorAttr('color')


class RackReservationPanel(panels.ObjectAttributesPanel):
    units = attrs.TextAttr('unit_list')
    status = attrs.ChoiceAttr('status')
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')
    user = attrs.RelatedObjectAttr('user')
    description = attrs.TextAttr('description')


class RackTypePanel(panels.ObjectAttributesPanel):
    manufacturer = attrs.RelatedObjectAttr('manufacturer', linkify=True)
    model = attrs.TextAttr('model')
    description = attrs.TextAttr('description')


class DevicePanel(panels.ObjectAttributesPanel):
    region = attrs.NestedObjectAttr('site.region', linkify=True)
    site = attrs.RelatedObjectAttr('site', linkify=True, grouped_by='group')
    location = attrs.NestedObjectAttr('location', linkify=True)
    rack = attrs.TemplatedAttr('rack', template_name='dcim/device/attrs/rack.html')
    virtual_chassis = attrs.RelatedObjectAttr('virtual_chassis', linkify=True)
    parent_device = attrs.TemplatedAttr('parent_bay', template_name='dcim/device/attrs/parent_device.html')
    gps_coordinates = attrs.GPSCoordinatesAttr()
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')
    description = attrs.TextAttr('description')
    airflow = attrs.ChoiceAttr('airflow')
    serial = attrs.TextAttr('serial', label=_('Serial number'), style='font-monospace', copy_button=True)
    asset_tag = attrs.TextAttr('asset_tag', style='font-monospace', copy_button=True)
    config_template = attrs.RelatedObjectAttr('config_template', linkify=True)


class DeviceManagementPanel(panels.ObjectAttributesPanel):
    title = _('Management')

    status = attrs.ChoiceAttr('status')
    role = attrs.NestedObjectAttr('role', linkify=True, max_depth=3)
    platform = attrs.NestedObjectAttr('platform', linkify=True, max_depth=3)
    primary_ip4 = attrs.TemplatedAttr(
        'primary_ip4',
        label=_('Primary IPv4'),
        template_name='dcim/device/attrs/ipaddress.html',
    )
    primary_ip6 = attrs.TemplatedAttr(
        'primary_ip6',
        label=_('Primary IPv6'),
        template_name='dcim/device/attrs/ipaddress.html',
    )
    oob_ip = attrs.TemplatedAttr(
        'oob_ip',
        label=_('Out-of-band IP'),
        template_name='dcim/device/attrs/ipaddress.html',
    )
    cluster = attrs.RelatedObjectAttr('cluster', linkify=True)


class DeviceDeviceTypePanel(panels.ObjectAttributesPanel):
    title = _('Device Type')

    manufacturer = attrs.RelatedObjectAttr('device_type.manufacturer', linkify=True)
    model = attrs.RelatedObjectAttr('device_type', linkify=True)
    height = attrs.TemplatedAttr('device_type.u_height', template_name='dcim/devicetype/attrs/height.html')
    front_image = attrs.ImageAttr('device_type.front_image')
    rear_image = attrs.ImageAttr('device_type.rear_image')


class DeviceDimensionsPanel(panels.ObjectAttributesPanel):
    title = _('Dimensions')

    total_weight = attrs.TemplatedAttr('total_weight', template_name='dcim/device/attrs/total_weight.html')


class DeviceTypePanel(panels.ObjectAttributesPanel):
    manufacturer = attrs.RelatedObjectAttr('manufacturer', linkify=True)
    model = attrs.TextAttr('model')
    part_number = attrs.TextAttr('part_number')
    default_platform = attrs.RelatedObjectAttr('default_platform', linkify=True)
    description = attrs.TextAttr('description')
    height = attrs.TemplatedAttr('u_height', template_name='dcim/devicetype/attrs/height.html')
    exclude_from_utilization = attrs.BooleanAttr('exclude_from_utilization')
    full_depth = attrs.BooleanAttr('is_full_depth')
    weight = attrs.NumericAttr('weight', unit_accessor='get_weight_unit_display')
    subdevice_role = attrs.ChoiceAttr('subdevice_role', label=_('Parent/child'))
    airflow = attrs.ChoiceAttr('airflow')
    front_image = attrs.ImageAttr('front_image')
    rear_image = attrs.ImageAttr('rear_image')


class ModuleTypeProfilePanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name')
    description = attrs.TextAttr('description')


class VirtualChassisMembersPanel(panels.ObjectPanel):
    """
    A panel which lists all members of a virtual chassis.
    """
    template_name = 'dcim/panels/virtual_chassis_members.html'
    title = _('Virtual Chassis Members')

    def get_context(self, context):
        return {
            **super().get_context(context),
            'vc_members': context.get('vc_members'),
        }

    def render(self, context):
        if not context.get('vc_members'):
            return ''
        return super().render(context)


class PowerUtilizationPanel(panels.ObjectPanel):
    """
    A panel which displays the power utilization statistics for a device.
    """
    template_name = 'dcim/panels/power_utilization.html'
    title = _('Power Utilization')

    def get_context(self, context):
        return {
            **super().get_context(context),
            'vc_members': context.get('vc_members'),
        }

    def render(self, context):
        obj = context['object']
        if not obj.powerports.exists() or not obj.poweroutlets.exists():
            return ''
        return super().render(context)
