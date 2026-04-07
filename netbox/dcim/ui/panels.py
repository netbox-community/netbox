from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from netbox.ui import actions, attrs, panels


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
    facility_id = attrs.TextAttr('facility_id', label=_('Facility ID'))
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')
    status = attrs.ChoiceAttr('status')
    rack_type = attrs.RelatedObjectAttr('rack_type', linkify=True, grouped_by='manufacturer')
    role = attrs.RelatedObjectAttr('role', linkify=True, colored=True)
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
    role = attrs.NestedObjectAttr('role', linkify=True, max_depth=3, colored=True)
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


class DeviceRolePanel(panels.NestedGroupObjectPanel):
    color = attrs.ColorAttr('color')
    vm_role = attrs.BooleanAttr('vm_role', label=_('VM role'))
    config_template = attrs.RelatedObjectAttr('config_template', linkify=True)


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


class ModulePanel(panels.ObjectAttributesPanel):
    device = attrs.RelatedObjectAttr('device', linkify=True)
    device_type = attrs.RelatedObjectAttr('device.device_type', linkify=True, grouped_by='manufacturer')
    module_bay = attrs.NestedObjectAttr('module_bay', linkify=True)
    status = attrs.ChoiceAttr('status')
    description = attrs.TextAttr('description')
    serial = attrs.TextAttr('serial', label=_('Serial number'), style='font-monospace', copy_button=True)
    asset_tag = attrs.TextAttr('asset_tag', style='font-monospace', copy_button=True)


class ModuleTypeProfilePanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name')
    description = attrs.TextAttr('description')


class ModuleTypePanel(panels.ObjectAttributesPanel):
    profile = attrs.RelatedObjectAttr('profile', linkify=True)
    manufacturer = attrs.RelatedObjectAttr('manufacturer', linkify=True)
    model = attrs.TextAttr('model', label=_('Model name'))
    part_number = attrs.TextAttr('part_number')
    description = attrs.TextAttr('description')
    airflow = attrs.ChoiceAttr('airflow')
    weight = attrs.NumericAttr('weight', unit_accessor='get_weight_unit_display')


class PlatformPanel(panels.NestedGroupObjectPanel):
    manufacturer = attrs.RelatedObjectAttr('manufacturer', linkify=True)
    config_template = attrs.RelatedObjectAttr('config_template', linkify=True)


class ConsolePortPanel(panels.ObjectAttributesPanel):
    device = attrs.RelatedObjectAttr('device', linkify=True)
    module = attrs.RelatedObjectAttr('module', linkify=True)
    name = attrs.TextAttr('name')
    label = attrs.TextAttr('label')
    type = attrs.ChoiceAttr('type')
    speed = attrs.ChoiceAttr('speed')
    description = attrs.TextAttr('description')


class ConsoleServerPortPanel(panels.ObjectAttributesPanel):
    device = attrs.RelatedObjectAttr('device', linkify=True)
    module = attrs.RelatedObjectAttr('module', linkify=True)
    name = attrs.TextAttr('name')
    label = attrs.TextAttr('label')
    type = attrs.ChoiceAttr('type')
    speed = attrs.ChoiceAttr('speed')
    description = attrs.TextAttr('description')


class PowerPortPanel(panels.ObjectAttributesPanel):
    device = attrs.RelatedObjectAttr('device', linkify=True)
    module = attrs.RelatedObjectAttr('module', linkify=True)
    name = attrs.TextAttr('name')
    label = attrs.TextAttr('label')
    type = attrs.ChoiceAttr('type')
    description = attrs.TextAttr('description')
    maximum_draw = attrs.TextAttr('maximum_draw')
    allocated_draw = attrs.TextAttr('allocated_draw')


class PowerOutletPanel(panels.ObjectAttributesPanel):
    device = attrs.RelatedObjectAttr('device', linkify=True)
    module = attrs.RelatedObjectAttr('module', linkify=True)
    name = attrs.TextAttr('name')
    label = attrs.TextAttr('label')
    type = attrs.ChoiceAttr('type')
    status = attrs.ChoiceAttr('status')
    description = attrs.TextAttr('description')
    color = attrs.ColorAttr('color')
    power_port = attrs.RelatedObjectAttr('power_port', linkify=True)
    feed_leg = attrs.ChoiceAttr('feed_leg')


class FrontPortPanel(panels.ObjectAttributesPanel):
    device = attrs.RelatedObjectAttr('device', linkify=True)
    module = attrs.RelatedObjectAttr('module', linkify=True)
    name = attrs.TextAttr('name')
    label = attrs.TextAttr('label')
    type = attrs.ChoiceAttr('type')
    color = attrs.ColorAttr('color')
    positions = attrs.TextAttr('positions')
    description = attrs.TextAttr('description')


class RearPortPanel(panels.ObjectAttributesPanel):
    device = attrs.RelatedObjectAttr('device', linkify=True)
    module = attrs.RelatedObjectAttr('module', linkify=True)
    name = attrs.TextAttr('name')
    label = attrs.TextAttr('label')
    type = attrs.ChoiceAttr('type')
    color = attrs.ColorAttr('color')
    positions = attrs.TextAttr('positions')
    description = attrs.TextAttr('description')


class ModuleBayPanel(panels.ObjectAttributesPanel):
    device = attrs.RelatedObjectAttr('device', linkify=True)
    module = attrs.RelatedObjectAttr('module', linkify=True)
    name = attrs.TextAttr('name')
    label = attrs.TextAttr('label')
    position = attrs.TextAttr('position')
    description = attrs.TextAttr('description')


class DeviceBayPanel(panels.ObjectAttributesPanel):
    device = attrs.RelatedObjectAttr('device', linkify=True)
    name = attrs.TextAttr('name')
    label = attrs.TextAttr('label')
    description = attrs.TextAttr('description')


class InventoryItemPanel(panels.ObjectAttributesPanel):
    device = attrs.RelatedObjectAttr('device', linkify=True)
    parent = attrs.RelatedObjectAttr('parent', linkify=True, label=_('Parent item'))
    name = attrs.TextAttr('name')
    label = attrs.TextAttr('label')
    status = attrs.ChoiceAttr('status')
    role = attrs.RelatedObjectAttr('role', linkify=True, colored=True)
    component = attrs.GenericForeignKeyAttr('component', linkify=True)
    manufacturer = attrs.RelatedObjectAttr('manufacturer', linkify=True)
    part_id = attrs.TextAttr('part_id', label=_('Part ID'))
    serial = attrs.TextAttr('serial')
    asset_tag = attrs.TextAttr('asset_tag')
    description = attrs.TextAttr('description')


class InventoryItemRolePanel(panels.OrganizationalObjectPanel):
    color = attrs.ColorAttr('color')


class CablePanel(panels.ObjectAttributesPanel):
    type = attrs.ChoiceAttr('type')
    status = attrs.ChoiceAttr('status')
    profile = attrs.ChoiceAttr('profile')
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')
    label = attrs.TextAttr('label')
    description = attrs.TextAttr('description')
    color = attrs.ColorAttr('color')
    length = attrs.NumericAttr('length', unit_accessor='get_length_unit_display')


class VirtualChassisPanel(panels.ObjectAttributesPanel):
    domain = attrs.TextAttr('domain')
    master = attrs.RelatedObjectAttr('master', linkify=True)
    description = attrs.TextAttr('description')


class PowerPanelPanel(panels.ObjectAttributesPanel):
    site = attrs.RelatedObjectAttr('site', linkify=True)
    location = attrs.NestedObjectAttr('location', linkify=True)
    description = attrs.TextAttr('description')


class PowerFeedPanel(panels.ObjectAttributesPanel):
    power_panel = attrs.RelatedObjectAttr('power_panel', linkify=True)
    rack = attrs.RelatedObjectAttr('rack', linkify=True)
    type = attrs.ChoiceAttr('type')
    status = attrs.ChoiceAttr('status')
    description = attrs.TextAttr('description')
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')
    connected_device = attrs.TemplatedAttr(
        'connected_endpoints',
        label=_('Connected device'),
        template_name='dcim/powerfeed/attrs/connected_device.html',
    )
    utilization = attrs.TemplatedAttr(
        'connected_endpoints',
        label=_('Utilization (allocated)'),
        template_name='dcim/powerfeed/attrs/utilization.html',
    )


class PowerFeedElectricalPanel(panels.ObjectAttributesPanel):
    title = _('Electrical Characteristics')

    supply = attrs.ChoiceAttr('supply')
    voltage = attrs.TextAttr('voltage', format_string=_('{}V'))
    amperage = attrs.TextAttr('amperage', format_string=_('{}A'))
    phase = attrs.ChoiceAttr('phase')
    max_utilization = attrs.TextAttr('max_utilization', format_string='{}%')


class VirtualDeviceContextPanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name')
    device = attrs.RelatedObjectAttr('device', linkify=True)
    identifier = attrs.TextAttr('identifier')
    status = attrs.ChoiceAttr('status')
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
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')


class MACAddressPanel(panels.ObjectAttributesPanel):
    mac_address = attrs.TextAttr('mac_address', label=_('MAC address'), style='font-monospace', copy_button=True)
    description = attrs.TextAttr('description')
    assignment = attrs.RelatedObjectAttr('assigned_object', linkify=True, grouped_by='parent_object')
    is_primary = attrs.BooleanAttr('is_primary', label=_('Primary for interface'))


class ConnectionPanel(panels.ObjectPanel):
    """
    A panel which displays connection information for a cabled object.
    """
    template_name = 'dcim/panels/connection.html'
    title = _('Connection')

    def __init__(self, trace_url_name, connect_options=None, show_endpoints=True, **kwargs):
        super().__init__(**kwargs)
        self.trace_url_name = trace_url_name
        self.connect_options = connect_options or []
        self.show_endpoints = show_endpoints

    def get_context(self, context):
        return {
            **super().get_context(context),
            'trace_url_name': self.trace_url_name,
            'connect_options': self.connect_options,
            'show_endpoints': self.show_endpoints,
        }

    def render(self, context):
        ctx = self.get_context(context)
        return render_to_string(self.template_name, ctx, request=ctx.get('request'))


class InventoryItemsPanel(panels.ObjectPanel):
    """
    A panel which displays inventory items associated with a component.
    """
    template_name = 'dcim/panels/component_inventory_items.html'
    title = _('Inventory Items')
    actions = [
        actions.AddObject(
            'dcim.inventoryitem',
            url_params={
                'component_type': lambda ctx: ContentType.objects.get_for_model(ctx['object']).pk,
                'component_id': lambda ctx: ctx['object'].pk,
            },
        ),
    ]

    def render(self, context):
        ctx = self.get_context(context)
        return render_to_string(self.template_name, ctx, request=ctx.get('request'))


class VirtualChassisMembersPanel(panels.ObjectPanel):
    """
    A panel which lists all members of a virtual chassis.
    """

    template_name = 'dcim/panels/virtual_chassis_members.html'
    title = _('Virtual Chassis Members')
    actions = [
        actions.AddObject(
            'dcim.device',
            url_params={
                'site': lambda ctx: (
                    ctx['virtual_chassis'].master.site_id
                    if ctx['virtual_chassis'] and ctx['virtual_chassis'].master_id
                    else ''
                ),
                'rack': lambda ctx: (
                    ctx['virtual_chassis'].master.rack_id
                    if ctx['virtual_chassis'] and ctx['virtual_chassis'].master_id
                    else ''
                ),
            },
        ),
    ]

    def get_context(self, context):
        return {
            **super().get_context(context),
            'virtual_chassis': context.get('virtual_chassis'),
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


class InterfacePanel(panels.ObjectAttributesPanel):
    device = attrs.RelatedObjectAttr('device', linkify=True)
    module = attrs.RelatedObjectAttr('module', linkify=True)
    name = attrs.TextAttr('name')
    label = attrs.TextAttr('label')
    type = attrs.ChoiceAttr('type')
    speed = attrs.TemplatedAttr('speed', template_name='dcim/interface/attrs/speed.html', label=_('Speed'))
    duplex = attrs.ChoiceAttr('duplex')
    mtu = attrs.TextAttr('mtu', label=_('MTU'))
    enabled = attrs.BooleanAttr('enabled')
    mgmt_only = attrs.BooleanAttr('mgmt_only', label=_('Management only'))
    description = attrs.TextAttr('description')
    poe_mode = attrs.ChoiceAttr('poe_mode', label=_('PoE mode'))
    poe_type = attrs.ChoiceAttr('poe_type', label=_('PoE type'))
    mode = attrs.ChoiceAttr('mode', label=_('802.1Q mode'))
    qinq_svlan = attrs.RelatedObjectAttr('qinq_svlan', linkify=True, label=_('Q-in-Q SVLAN'))
    untagged_vlan = attrs.RelatedObjectAttr('untagged_vlan', linkify=True, label=_('Untagged VLAN'))
    tx_power = attrs.TextAttr('tx_power', label=_('Transmit power (dBm)'))
    tunnel = attrs.RelatedObjectAttr('tunnel_termination.tunnel', linkify=True, label=_('Tunnel'))
    l2vpn = attrs.RelatedObjectAttr('l2vpn_termination.l2vpn', linkify=True, label=_('L2VPN'))


class RelatedInterfacesPanel(panels.ObjectAttributesPanel):
    title = _('Related Interfaces')

    parent = attrs.RelatedObjectAttr('parent', linkify=True)
    bridge = attrs.RelatedObjectAttr('bridge', linkify=True)
    lag = attrs.RelatedObjectAttr('lag', linkify=True, label=_('LAG'))


class InterfaceAddressingPanel(panels.ObjectAttributesPanel):
    title = _('Addressing')

    mac_address = attrs.TemplatedAttr(
        'primary_mac_address',
        template_name='dcim/interface/attrs/mac_address.html',
        label=_('MAC address'),
    )
    wwn = attrs.TextAttr('wwn', style='font-monospace', label=_('WWN'))
    vrf = attrs.RelatedObjectAttr('vrf', linkify=True, label=_('VRF'))
    vlan_translation = attrs.RelatedObjectAttr('vlan_translation_policy', linkify=True, label=_('VLAN translation'))


class InterfaceConnectionPanel(panels.ObjectPanel):
    """
    A connection panel for interfaces, which handles cable, wireless link, and virtual circuit cases.
    """
    template_name = 'dcim/panels/interface_connection.html'
    title = _('Connection')

    def render(self, context):
        obj = context.get('object')
        if obj and obj.is_virtual:
            return ''
        ctx = self.get_context(context)
        return render_to_string(self.template_name, ctx, request=ctx.get('request'))


class VirtualCircuitPanel(panels.ObjectPanel):
    """
    A panel which displays virtual circuit information for a virtual interface.
    """
    template_name = 'dcim/panels/interface_virtual_circuit.html'
    title = _('Virtual Circuit')

    def render(self, context):
        obj = context.get('object')
        if not obj or not obj.is_virtual or not hasattr(obj, 'virtual_circuit_termination'):
            return ''
        ctx = self.get_context(context)
        return render_to_string(self.template_name, ctx, request=ctx.get('request'))


class InterfaceWirelessPanel(panels.ObjectPanel):
    """
    A panel which displays wireless RF attributes for an interface, comparing local and peer values.
    """
    template_name = 'dcim/panels/interface_wireless.html'
    title = _('Wireless')

    def render(self, context):
        obj = context.get('object')
        if not obj or not obj.is_wireless:
            return ''
        ctx = self.get_context(context)
        return render_to_string(self.template_name, ctx, request=ctx.get('request'))


class WirelessLANsPanel(panels.ObjectPanel):
    """
    A panel which lists the wireless LANs associated with an interface.
    """
    template_name = 'dcim/panels/interface_wireless_lans.html'
    title = _('Wireless LANs')

    def render(self, context):
        obj = context.get('object')
        if not obj or not obj.is_wireless:
            return ''
        ctx = self.get_context(context)
        return render_to_string(self.template_name, ctx, request=ctx.get('request'))
