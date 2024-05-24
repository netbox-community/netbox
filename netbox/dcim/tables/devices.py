import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from django_tables2.utils import Accessor

from dcim import models
from netbox.tables import NetBoxTable, columns
from tenancy.tables import ContactsColumnMixin, TenancyColumnsMixin
from .template_code import *

__all__ = (
    'BaseInterfaceTable',
    'CableTerminationTable',
    'ConsolePortTable',
    'ConsoleServerPortTable',
    'DeviceBayTable',
    'DeviceConsolePortTable',
    'DeviceConsoleServerPortTable',
    'DeviceDeviceBayTable',
    'DeviceFrontPortTable',
    'DeviceInterfaceTable',
    'DeviceInventoryItemTable',
    'DeviceModuleBayTable',
    'DevicePowerPortTable',
    'DevicePowerOutletTable',
    'DeviceRearPortTable',
    'DeviceRoleTable',
    'DeviceTable',
    'FrontPortTable',
    'InterfaceTable',
    'InventoryItemRoleTable',
    'InventoryItemTable',
    'ModuleBayTable',
    'PlatformTable',
    'PowerOutletTable',
    'PowerPortTable',
    'RearPortTable',
    'VirtualChassisTable',
    'VirtualDeviceContextTable'
)

MODULEBAY_STATUS = """
{% badge record.installed_module.get_status_display bg_color=record.installed_module.get_status_color %}
"""


def get_cabletermination_row_class(record):
    if record.mark_connected:
        return 'success'
    elif record.cable:
        return record.cable.get_status_color()
    return ''


#
# Device roles
#

class DeviceRoleTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    device_count = columns.LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'role_id': 'pk'},
        verbose_name=_('Devices')
    )
    vm_count = columns.LinkedCountColumn(
        viewname='virtualization:virtualmachine_list',
        url_params={'role_id': 'pk'},
        verbose_name=_('VMs')
    )
    color = columns.ColorColumn()
    vm_role = columns.BooleanColumn()
    config_template = tables.Column(
        linkify=True
    )
    tags = columns.TagColumn(
        url_name='dcim:devicerole_list'
    )

    class Meta(NetBoxTable.Meta):
        model = models.DeviceRole
        fields = (
            'pk', 'id', 'name', 'device_count', 'vm_count', 'color', 'vm_role', 'config_template', 'description',
            'slug', 'tags', 'actions', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'device_count', 'vm_count', 'color', 'vm_role', 'description')


#
# Platforms
#

class PlatformTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    manufacturer = tables.Column(
        verbose_name=_('Manufacturer'),
        linkify=True
    )
    config_template = tables.Column(
        verbose_name=_('Config Template'),
        linkify=True
    )
    device_count = columns.LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'platform_id': 'pk'},
        verbose_name=_('Devices')
    )
    vm_count = columns.LinkedCountColumn(
        viewname='virtualization:virtualmachine_list',
        url_params={'platform_id': 'pk'},
        verbose_name=_('VMs')
    )
    tags = columns.TagColumn(
        url_name='dcim:platform_list'
    )

    class Meta(NetBoxTable.Meta):
        model = models.Platform
        fields = (
            'pk', 'id', 'name', 'manufacturer', 'device_count', 'vm_count', 'slug', 'config_template', 'description',
            'tags', 'actions', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'manufacturer', 'device_count', 'vm_count', 'description',
        )


#
# Devices
#

class DeviceTable(TenancyColumnsMixin, ContactsColumnMixin, NetBoxTable):
    name = tables.TemplateColumn(
        verbose_name=_('Name'),
        order_by=('_name',),
        template_code=DEVICE_LINK,
        linkify=True
    )
    status = columns.ChoiceFieldColumn(
        verbose_name=_('Status'),
    )
    region = tables.Column(
        verbose_name=_('Region'),
        accessor=Accessor('site__region'),
        linkify=True
    )
    site_group = tables.Column(
        accessor=Accessor('site__group'),
        linkify=True,
        verbose_name=_('Site Group')
    )
    site = tables.Column(
        verbose_name=_('Site'),
        linkify=True
    )
    location = tables.Column(
        verbose_name=_('Location'),
        linkify=True
    )
    rack = tables.Column(
        verbose_name=_('Rack'),
        linkify=True
    )
    position = columns.TemplateColumn(
        verbose_name=_('Position'),
        template_code='{{ value|floatformat }}'
    )
    role = columns.ColoredLabelColumn(
        verbose_name=_('Role')
    )
    manufacturer = tables.Column(
        verbose_name=_('Manufacturer'),
        accessor=Accessor('device_type__manufacturer'),
        linkify=True
    )
    device_type = tables.Column(
        linkify=True,
        verbose_name=_('Type')
    )
    platform = tables.Column(
        linkify=True,
        verbose_name=_('Platform')
    )
    primary_ip = tables.Column(
        linkify=True,
        order_by=('primary_ip4', 'primary_ip6'),
        verbose_name=_('IP Address')
    )
    primary_ip4 = tables.Column(
        linkify=True,
        verbose_name=_('IPv4 Address')
    )
    primary_ip6 = tables.Column(
        linkify=True,
        verbose_name=_('IPv6 Address')
    )
    oob_ip = tables.Column(
        linkify=True,
        verbose_name='OOB IP'
    )
    cluster = tables.Column(
        verbose_name=_('Cluster'),
        linkify=True
    )
    virtual_chassis = tables.Column(
        verbose_name=_('Virtual Chassis'),
        linkify=True
    )
    vc_position = tables.Column(
        verbose_name=_('VC Position')
    )
    vc_priority = tables.Column(
        verbose_name=_('VC Priority')
    )
    config_template = tables.Column(
        verbose_name=_('Config Template'),
        linkify=True
    )
    parent_device = tables.Column(
        verbose_name=_('Parent Device'),
        linkify=True,
        accessor='parent_bay__device'
    )
    device_bay_position = tables.Column(
        verbose_name=_('Position (Device Bay)'),
        accessor='parent_bay',
        linkify=True
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='dcim:device_list'
    )
    console_port_count = tables.Column(
        verbose_name=_('Console ports')
    )
    console_server_port_count = tables.Column(
        verbose_name=_('Console server ports')
    )
    power_port_count = tables.Column(
        verbose_name=_('Power ports')
    )
    power_outlet_count = tables.Column(
        verbose_name=_('Power outlets')
    )
    interface_count = tables.Column(
        verbose_name=_('Interfaces')
    )
    front_port_count = tables.Column(
        verbose_name=_('Front ports')
    )
    rear_port_count = tables.Column(
        verbose_name=_('Rear ports')
    )
    device_bay_count = tables.Column(
        verbose_name=_('Device bays')
    )
    module_bay_count = tables.Column(
        verbose_name=_('Module bays')
    )
    inventory_item_count = tables.Column(
        verbose_name=_('Inventory items')
    )

    class Meta(NetBoxTable.Meta):
        model = models.Device
        fields = (
            'pk', 'id', 'name', 'status', 'tenant', 'tenant_group', 'role', 'manufacturer', 'device_type',
            'serial', 'asset_tag', 'region', 'site_group', 'site', 'location', 'rack', 'parent_device',
            'device_bay_position', 'position', 'face', 'latitude', 'longitude', 'airflow', 'primary_ip', 'primary_ip4',
            'primary_ip6', 'oob_ip', 'cluster', 'virtual_chassis', 'vc_position', 'vc_priority', 'description',
            'config_template', 'comments', 'contacts', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'status', 'tenant', 'site', 'location', 'rack', 'role', 'manufacturer', 'device_type',
            'primary_ip',
        )


#
# Device components
#

class DeviceComponentTable(NetBoxTable):
    device = tables.Column(
        verbose_name=_('Device'),
        linkify=True
    )
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True,
        order_by=('_name',)
    )

    class Meta(NetBoxTable.Meta):
        order_by = ('device', 'name')


class ModularDeviceComponentTable(DeviceComponentTable):
    module_bay = tables.Column(
        verbose_name=_('Module Bay'),
        accessor=Accessor('module__module_bay'),
        linkify={
            'viewname': 'dcim:device_modulebays',
            'args': [Accessor('device_id')],
        }
    )
    module = tables.Column(
        verbose_name=_('Module'),
        linkify=True
    )
    inventory_items = columns.ManyToManyColumn(
        linkify_item=True,
        verbose_name=_('Inventory Items'),
    )


class CableTerminationTable(NetBoxTable):
    cable = tables.Column(
        verbose_name=_('Cable'),
        linkify=True
    )
    cable_color = columns.ColorColumn(
        accessor='cable__color',
        orderable=False,
        verbose_name=_('Cable Color')
    )
    link_peer = columns.TemplateColumn(
        accessor='link_peers',
        template_code=LINKTERMINATION,
        orderable=False,
        verbose_name=_('Link Peers')
    )
    mark_connected = columns.BooleanColumn(
        verbose_name=_('Mark Connected'),
    )

    def value_link_peer(self, value):
        return ', '.join([
            f"{termination.parent_object} > {termination}" for termination in value
        ])


class PathEndpointTable(CableTerminationTable):
    connection = columns.TemplateColumn(
        accessor='_path__destinations',
        template_code=LINKTERMINATION,
        verbose_name=_('Connection'),
        orderable=False
    )


class ConsolePortTable(ModularDeviceComponentTable, PathEndpointTable):
    device = tables.Column(
        verbose_name=_('Device'),
        linkify={
            'viewname': 'dcim:device_consoleports',
            'args': [Accessor('device_id')],
        }
    )
    tags = columns.TagColumn(
        url_name='dcim:consoleport_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.ConsolePort
        fields = (
            'pk', 'id', 'name', 'device', 'module_bay', 'module', 'label', 'type', 'speed', 'description',
            'mark_connected', 'cable', 'cable_color', 'link_peer', 'connection', 'inventory_items', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'device', 'label', 'type', 'speed', 'description')


class DeviceConsolePortTable(ConsolePortTable):
    name = tables.TemplateColumn(
        verbose_name=_('Name'),
        template_code='<i class="mdi mdi-console"></i> <a href="{{ record.get_absolute_url }}">{{ value }}</a>',
        order_by=Accessor('_name'),
        attrs={'td': {'class': 'text-nowrap'}}
    )
    actions = columns.ActionsColumn(
        extra_buttons=CONSOLEPORT_BUTTONS
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.ConsolePort
        fields = (
            'pk', 'id', 'name', 'module_bay', 'module', 'label', 'type', 'speed', 'description', 'mark_connected',
            'cable', 'cable_color', 'link_peer', 'connection', 'tags', 'actions'
        )
        default_columns = ('pk', 'name', 'label', 'type', 'speed', 'description', 'cable', 'connection')
        row_attrs = {
            'class': get_cabletermination_row_class
        }


class ConsoleServerPortTable(ModularDeviceComponentTable, PathEndpointTable):
    device = tables.Column(
        verbose_name=_('Device'),
        linkify={
            'viewname': 'dcim:device_consoleserverports',
            'args': [Accessor('device_id')],
        }
    )
    tags = columns.TagColumn(
        url_name='dcim:consoleserverport_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.ConsoleServerPort
        fields = (
            'pk', 'id', 'name', 'device', 'module_bay', 'module', 'label', 'type', 'speed', 'description',
            'mark_connected', 'cable', 'cable_color', 'link_peer', 'connection', 'inventory_items', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'device', 'label', 'type', 'speed', 'description')


class DeviceConsoleServerPortTable(ConsoleServerPortTable):
    name = tables.TemplateColumn(
        verbose_name=_('Name'),
        template_code='<i class="mdi mdi-console-network-outline"></i> '
                      '<a href="{{ record.get_absolute_url }}">{{ value }}</a>',
        order_by=Accessor('_name'),
        attrs={'td': {'class': 'text-nowrap'}}
    )
    actions = columns.ActionsColumn(
        extra_buttons=CONSOLESERVERPORT_BUTTONS
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.ConsoleServerPort
        fields = (
            'pk', 'id', 'name', 'module_bay', 'module', 'label', 'type', 'speed', 'description', 'mark_connected',
            'cable', 'cable_color', 'link_peer', 'connection', 'tags', 'actions',
        )
        default_columns = ('pk', 'name', 'label', 'type', 'speed', 'description', 'cable', 'connection')
        row_attrs = {
            'class': get_cabletermination_row_class
        }


class PowerPortTable(ModularDeviceComponentTable, PathEndpointTable):
    device = tables.Column(
        verbose_name=_('Device'),
        linkify={
            'viewname': 'dcim:device_powerports',
            'args': [Accessor('device_id')],
        }
    )
    maximum_draw = tables.Column(
        verbose_name=_('Maximum draw (W)')
    )
    allocated_draw = tables.Column(
        verbose_name=_('Allocated draw (W)')
    )
    tags = columns.TagColumn(
        url_name='dcim:powerport_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.PowerPort
        fields = (
            'pk', 'id', 'name', 'device', 'module_bay', 'module', 'label', 'type', 'description', 'mark_connected',
            'maximum_draw', 'allocated_draw', 'cable', 'cable_color', 'link_peer', 'connection', 'inventory_items',
            'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'device', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description')


class DevicePowerPortTable(PowerPortTable):
    name = tables.TemplateColumn(
        verbose_name=_('Name'),
        template_code='<i class="mdi mdi-power-plug-outline"></i> <a href="{{ record.get_absolute_url }}">'
                      '{{ value }}</a>',
        order_by=Accessor('_name'),
        attrs={'td': {'class': 'text-nowrap'}}
    )
    actions = columns.ActionsColumn(
        extra_buttons=POWERPORT_BUTTONS
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.PowerPort
        fields = (
            'pk', 'id', 'name', 'module_bay', 'module', 'label', 'type', 'maximum_draw', 'allocated_draw',
            'description', 'mark_connected', 'cable', 'cable_color', 'link_peer', 'connection', 'tags', 'actions',
        )
        default_columns = (
            'pk', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description', 'cable', 'connection',
        )
        row_attrs = {
            'class': get_cabletermination_row_class
        }


class PowerOutletTable(ModularDeviceComponentTable, PathEndpointTable):
    device = tables.Column(
        verbose_name=_('Device'),
        linkify={
            'viewname': 'dcim:device_poweroutlets',
            'args': [Accessor('device_id')],
        }
    )
    power_port = tables.Column(
        verbose_name=_('Power Port'),
        linkify=True
    )
    tags = columns.TagColumn(
        url_name='dcim:poweroutlet_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.PowerOutlet
        fields = (
            'pk', 'id', 'name', 'device', 'module_bay', 'module', 'label', 'type', 'description', 'power_port',
            'feed_leg', 'mark_connected', 'cable', 'cable_color', 'link_peer', 'connection', 'inventory_items',
            'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'device', 'label', 'type', 'power_port', 'feed_leg', 'description')


class DevicePowerOutletTable(PowerOutletTable):
    name = tables.TemplateColumn(
        verbose_name=_('Name'),
        template_code='<i class="mdi mdi-power-socket"></i> <a href="{{ record.get_absolute_url }}">{{ value }}</a>',
        order_by=Accessor('_name'),
        attrs={'td': {'class': 'text-nowrap'}}
    )
    actions = columns.ActionsColumn(
        extra_buttons=POWEROUTLET_BUTTONS
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.PowerOutlet
        fields = (
            'pk', 'id', 'name', 'module_bay', 'module', 'label', 'type', 'power_port', 'feed_leg', 'description',
            'mark_connected', 'cable', 'cable_color', 'link_peer', 'connection', 'tags', 'actions',
        )
        default_columns = (
            'pk', 'name', 'label', 'type', 'power_port', 'feed_leg', 'description', 'cable', 'connection',
        )
        row_attrs = {
            'class': get_cabletermination_row_class
        }


class BaseInterfaceTable(NetBoxTable):
    enabled = columns.BooleanColumn(
        verbose_name=_('Enabled'),
    )
    ip_addresses = tables.TemplateColumn(
        template_code=INTERFACE_IPADDRESSES,
        orderable=False,
        verbose_name=_('IP Addresses')
    )
    fhrp_groups = tables.TemplateColumn(
        accessor=Accessor('fhrp_group_assignments'),
        template_code=INTERFACE_FHRPGROUPS,
        orderable=False,
        verbose_name=_('FHRP Groups')
    )
    l2vpn = tables.Column(
        accessor=tables.A('l2vpn_termination__l2vpn'),
        linkify=True,
        orderable=False,
        verbose_name=_('L2VPN')
    )
    tunnel = tables.Column(
        accessor=tables.A('tunnel_termination__tunnel'),
        linkify=True,
        orderable=False,
        verbose_name=_('Tunnel')
    )
    untagged_vlan = tables.Column(
        verbose_name=_('Untagged VLAN'),
        linkify=True
    )
    tagged_vlans = columns.TemplateColumn(
        template_code=INTERFACE_TAGGED_VLANS,
        orderable=False,
        verbose_name=_('Tagged VLANs')
    )

    def value_ip_addresses(self, value):
        return ",".join([str(obj.address) for obj in value.all()])


class InterfaceTable(ModularDeviceComponentTable, BaseInterfaceTable, PathEndpointTable):
    device = tables.Column(
        verbose_name=_('Device'),
        linkify={
            'viewname': 'dcim:device_interfaces',
            'args': [Accessor('device_id')],
        }
    )
    mgmt_only = columns.BooleanColumn(
        verbose_name=_('Management Only')
    )
    speed_formatted = columns.TemplateColumn(
        template_code='{% load helpers %}{{ value|humanize_speed }}',
        accessor=Accessor('speed'),
        verbose_name=_('Speed')
    )
    wireless_link = tables.Column(
        verbose_name=_('Wireless link'),
        linkify=True
    )
    wireless_lans = columns.TemplateColumn(
        template_code=INTERFACE_WIRELESS_LANS,
        orderable=False,
        verbose_name=_('Wireless LANs')
    )
    vdcs = columns.ManyToManyColumn(
        linkify_item=True,
        verbose_name=_('VDCs')
    )
    vrf = tables.Column(
        verbose_name=_('VRF'),
        linkify=True
    )
    tags = columns.TagColumn(
        url_name='dcim:interface_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.Interface
        fields = (
            'pk', 'id', 'name', 'device', 'module_bay', 'module', 'label', 'enabled', 'type', 'mgmt_only', 'mtu',
            'speed', 'speed_formatted', 'duplex', 'mode', 'mac_address', 'wwn', 'poe_mode', 'poe_type', 'rf_role', 'rf_channel',
            'rf_channel_frequency', 'rf_channel_width', 'tx_power', 'description', 'mark_connected', 'cable',
            'cable_color', 'wireless_link', 'wireless_lans', 'link_peer', 'connection', 'tags', 'vdcs', 'vrf', 'l2vpn',
            'tunnel', 'ip_addresses', 'fhrp_groups', 'untagged_vlan', 'tagged_vlans', 'inventory_items', 'created',
            'last_updated',
        )
        default_columns = ('pk', 'name', 'device', 'label', 'enabled', 'type', 'description')


class DeviceInterfaceTable(InterfaceTable):
    name = tables.TemplateColumn(
        verbose_name=_('Name'),
        template_code='<i class="mdi mdi-{% if record.mgmt_only %}wrench{% elif record.is_lag %}reorder-horizontal'
                      '{% elif record.is_virtual %}circle{% elif record.is_wireless %}wifi{% else %}ethernet'
                      '{% endif %}"></i> <a href="{{ record.get_absolute_url }}">{{ value }}</a>',
        order_by=Accessor('_name'),
        attrs={'td': {'class': 'text-nowrap'}}
    )
    parent = tables.Column(
        verbose_name=_('Parent'),
        linkify=True
    )
    bridge = tables.Column(
        verbose_name=_('Bridge'),
        linkify=True
    )
    lag = tables.Column(
        linkify=True,
        verbose_name=_('LAG')
    )
    actions = columns.ActionsColumn(
        extra_buttons=INTERFACE_BUTTONS
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.Interface
        fields = (
            'pk', 'id', 'name', 'module_bay', 'module', 'label', 'enabled', 'type', 'parent', 'bridge', 'lag',
            'mgmt_only', 'mtu', 'mode', 'mac_address', 'wwn', 'rf_role', 'rf_channel', 'rf_channel_frequency',
            'rf_channel_width', 'tx_power', 'description', 'mark_connected', 'cable', 'cable_color', 'wireless_link',
            'wireless_lans', 'link_peer', 'connection', 'tags', 'vdcs', 'vrf', 'l2vpn', 'tunnel', 'ip_addresses',
            'fhrp_groups', 'untagged_vlan', 'tagged_vlans', 'actions',
        )
        default_columns = (
            'pk', 'name', 'label', 'enabled', 'type', 'parent', 'lag', 'mtu', 'mode', 'description', 'ip_addresses',
            'cable', 'connection',
        )
        row_attrs = {
            'data-name': lambda record: record.name,
            'data-enabled': lambda record: "enabled" if record.enabled else "disabled",
            'data-virtual': lambda record: "true" if record.is_virtual else "false",
            'data-mark-connected': lambda record: "true" if record.mark_connected else "false",
            'data-cable-status': lambda record: record.cable.status if record.cable else "",
            'data-type': lambda record: record.type
        }


class FrontPortTable(ModularDeviceComponentTable, CableTerminationTable):
    device = tables.Column(
        verbose_name=_('Device'),
        linkify={
            'viewname': 'dcim:device_frontports',
            'args': [Accessor('device_id')],
        }
    )
    color = columns.ColorColumn(
        verbose_name=_('Color'),
    )
    rear_port_position = tables.Column(
        verbose_name=_('Position')
    )
    rear_port = tables.Column(
        verbose_name=_('Rear Port'),
        linkify=True
    )
    tags = columns.TagColumn(
        url_name='dcim:frontport_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.FrontPort
        fields = (
            'pk', 'id', 'name', 'device', 'module_bay', 'module', 'label', 'type', 'color', 'rear_port',
            'rear_port_position', 'description', 'mark_connected', 'cable', 'cable_color', 'link_peer',
            'inventory_items', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'device', 'label', 'type', 'color', 'rear_port', 'rear_port_position', 'description',
        )


class DeviceFrontPortTable(FrontPortTable):
    name = tables.TemplateColumn(
        verbose_name=_('Name'),
        template_code='<i class="mdi mdi-square-rounded{% if not record.cable %}-outline{% endif %}"></i> '
                      '<a href="{{ record.get_absolute_url }}">{{ value }}</a>',
        order_by=Accessor('_name'),
        attrs={'td': {'class': 'text-nowrap'}}
    )
    actions = columns.ActionsColumn(
        extra_buttons=FRONTPORT_BUTTONS
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.FrontPort
        fields = (
            'pk', 'id', 'name', 'module_bay', 'module', 'label', 'type', 'rear_port', 'rear_port_position',
            'description', 'mark_connected', 'cable', 'cable_color', 'link_peer', 'tags', 'actions',
        )
        default_columns = (
            'pk', 'name', 'label', 'type', 'rear_port', 'rear_port_position', 'description', 'cable', 'link_peer',
        )
        row_attrs = {
            'class': get_cabletermination_row_class
        }


class RearPortTable(ModularDeviceComponentTable, CableTerminationTable):
    device = tables.Column(
        verbose_name=_('Device'),
        linkify={
            'viewname': 'dcim:device_rearports',
            'args': [Accessor('device_id')],
        }
    )
    color = columns.ColorColumn(
        verbose_name=_('Color'),
    )
    tags = columns.TagColumn(
        url_name='dcim:rearport_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.RearPort
        fields = (
            'pk', 'id', 'name', 'device', 'module_bay', 'module', 'label', 'type', 'color', 'positions', 'description',
            'mark_connected', 'cable', 'cable_color', 'link_peer', 'inventory_items', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'device', 'label', 'type', 'color', 'description')


class DeviceRearPortTable(RearPortTable):
    name = tables.TemplateColumn(
        verbose_name=_('Name'),
        template_code='<i class="mdi mdi-square-rounded{% if not record.cable %}-outline{% endif %}"></i> '
                      '<a href="{{ record.get_absolute_url }}">{{ value }}</a>',
        order_by=Accessor('_name'),
        attrs={'td': {'class': 'text-nowrap'}}
    )
    actions = columns.ActionsColumn(
        extra_buttons=REARPORT_BUTTONS
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.RearPort
        fields = (
            'pk', 'id', 'name', 'module_bay', 'module', 'label', 'type', 'positions', 'description', 'mark_connected',
            'cable', 'cable_color', 'link_peer', 'tags', 'actions',
        )
        default_columns = (
            'pk', 'name', 'label', 'type', 'positions', 'description', 'cable', 'link_peer',
        )
        row_attrs = {
            'class': get_cabletermination_row_class
        }


class DeviceBayTable(DeviceComponentTable):
    device = tables.Column(
        verbose_name=_('Device'),
        linkify={
            'viewname': 'dcim:device_devicebays',
            'args': [Accessor('device_id')],
        }
    )
    role = columns.ColoredLabelColumn(
        accessor=Accessor('installed_device__role'),
        verbose_name=_('Role')
    )
    device_type = tables.Column(
        accessor=Accessor('installed_device__device_type'),
        linkify=True,
        verbose_name=_('Type')
    )
    status = tables.TemplateColumn(
        verbose_name=_('Status'),
        template_code=DEVICEBAY_STATUS,
        order_by=Accessor('installed_device__status')
    )
    installed_device = tables.Column(
        verbose_name=_('Installed device'),
        linkify=True
    )
    tags = columns.TagColumn(
        url_name='dcim:devicebay_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.DeviceBay
        fields = (
            'pk', 'id', 'name', 'device', 'label', 'status', 'role', 'device_type', 'installed_device', 'description',
            'tags', 'created', 'last_updated',
        )

        default_columns = ('pk', 'name', 'device', 'label', 'status', 'installed_device', 'description')


class DeviceDeviceBayTable(DeviceBayTable):
    name = tables.TemplateColumn(
        verbose_name=_('Name'),
        template_code='<i class="mdi mdi-circle{% if record.installed_device %}slice-8{% else %}outline{% endif %}'
                      '"></i> <a href="{{ record.get_absolute_url }}">{{ value }}</a>',
        order_by=Accessor('_name'),
        attrs={'td': {'class': 'text-nowrap'}}
    )
    actions = columns.ActionsColumn(
        extra_buttons=DEVICEBAY_BUTTONS
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.DeviceBay
        fields = (
            'pk', 'id', 'name', 'label', 'status', 'installed_device', 'description', 'tags', 'actions',
        )
        default_columns = ('pk', 'name', 'label', 'status', 'installed_device', 'description')


class ModuleBayTable(DeviceComponentTable):
    device = tables.Column(
        verbose_name=_('Device'),
        linkify={
            'viewname': 'dcim:device_modulebays',
            'args': [Accessor('device_id')],
        }
    )
    installed_module = tables.Column(
        linkify=True,
        verbose_name=_('Installed Module')
    )
    module_serial = tables.Column(
        verbose_name=_('Module Serial'),
        accessor=tables.A('installed_module__serial')
    )
    module_asset_tag = tables.Column(
        verbose_name=_('Module Asset Tag'),
        accessor=tables.A('installed_module__asset_tag')
    )
    tags = columns.TagColumn(
        url_name='dcim:modulebay_list'
    )
    module_status = columns.TemplateColumn(
        accessor=tables.A('installed_module__status'),
        template_code=MODULEBAY_STATUS,
        verbose_name=_('Module Status')
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.ModuleBay
        fields = (
            'pk', 'id', 'name', 'device', 'label', 'position', 'installed_module', 'module_status', 'module_serial',
            'module_asset_tag', 'description', 'tags',
        )
        default_columns = ('pk', 'name', 'device', 'label', 'installed_module', 'module_status', 'description')


class DeviceModuleBayTable(ModuleBayTable):
    actions = columns.ActionsColumn(
        extra_buttons=MODULEBAY_BUTTONS
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.ModuleBay
        fields = (
            'pk', 'id', 'name', 'label', 'position', 'installed_module', 'module_status', 'module_serial', 'module_asset_tag',
            'description', 'tags', 'actions',
        )
        default_columns = ('pk', 'name', 'label', 'installed_module', 'module_status', 'description')


class InventoryItemTable(DeviceComponentTable):
    device = tables.Column(
        verbose_name=_('Device'),
        linkify={
            'viewname': 'dcim:device_inventory',
            'args': [Accessor('device_id')],
        }
    )
    role = columns.ColoredLabelColumn(
        verbose_name=_('Role'),
    )
    manufacturer = tables.Column(
        verbose_name=_('Manufacturer'),
        linkify=True
    )
    component = tables.Column(
        verbose_name=_('Component'),
        orderable=False,
        linkify=True
    )
    discovered = columns.BooleanColumn(
        verbose_name=_('Discovered'),
    )
    parent = tables.Column(
        linkify=True,
        verbose_name=_('Parent'),
    )
    tags = columns.TagColumn(
        url_name='dcim:inventoryitem_list'
    )
    cable = None  # Override DeviceComponentTable

    class Meta(NetBoxTable.Meta):
        model = models.InventoryItem
        fields = (
            'pk', 'id', 'name', 'device', 'parent', 'component', 'label', 'role', 'manufacturer', 'part_id', 'serial',
            'asset_tag', 'description', 'discovered', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'device', 'label', 'role', 'manufacturer', 'part_id', 'serial', 'asset_tag',
        )


class DeviceInventoryItemTable(InventoryItemTable):
    name = tables.TemplateColumn(
        verbose_name=_('Name'),
        template_code='<a href="{{ record.get_absolute_url }}" style="padding-left: {{ record.level }}0px">'
                      '{{ value }}</a>',
        order_by=Accessor('_name'),
        attrs={'td': {'class': 'text-nowrap'}}
    )

    class Meta(NetBoxTable.Meta):
        model = models.InventoryItem
        fields = (
            'pk', 'id', 'name', 'label', 'role', 'manufacturer', 'part_id', 'serial', 'asset_tag', 'component',
            'description', 'discovered', 'tags', 'actions',
        )
        default_columns = (
            'pk', 'name', 'label', 'role', 'manufacturer', 'part_id', 'serial', 'asset_tag', 'component',
        )


class InventoryItemRoleTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    inventoryitem_count = columns.LinkedCountColumn(
        viewname='dcim:inventoryitem_list',
        url_params={'role_id': 'pk'},
        verbose_name=_('Items')
    )
    color = columns.ColorColumn(
        verbose_name=_('Color'),
    )
    tags = columns.TagColumn(
        url_name='dcim:inventoryitemrole_list'
    )

    class Meta(NetBoxTable.Meta):
        model = models.InventoryItemRole
        fields = (
            'pk', 'id', 'name', 'inventoryitem_count', 'color', 'description', 'slug', 'tags', 'actions',
        )
        default_columns = ('pk', 'name', 'inventoryitem_count', 'color', 'description')


#
# Virtual chassis
#

class VirtualChassisTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    master = tables.Column(
        verbose_name=_('Master'),
        linkify=True
    )
    member_count = columns.LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'virtual_chassis_id': 'pk'},
        verbose_name=_('Members')
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
    tags = columns.TagColumn(
        url_name='dcim:virtualchassis_list'
    )

    class Meta(NetBoxTable.Meta):
        model = models.VirtualChassis
        fields = (
            'pk', 'id', 'name', 'domain', 'master', 'member_count', 'description', 'comments', 'tags', 'created',
            'last_updated',
        )
        default_columns = ('pk', 'name', 'domain', 'master', 'member_count')


class VirtualDeviceContextTable(TenancyColumnsMixin, NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    device = tables.TemplateColumn(
        verbose_name=_('Device'),
        order_by=('_name',),
        template_code=DEVICE_LINK,
        linkify=True
    )
    status = columns.ChoiceFieldColumn(
        verbose_name=_('Status'),
    )
    primary_ip = tables.Column(
        linkify=True,
        order_by=('primary_ip4', 'primary_ip6'),
        verbose_name=_('IP Address')
    )
    primary_ip4 = tables.Column(
        linkify=True,
        verbose_name=_('IPv4 Address')
    )
    primary_ip6 = tables.Column(
        linkify=True,
        verbose_name=_('IPv6 Address')
    )
    interface_count = columns.LinkedCountColumn(
        viewname='dcim:interface_list',
        url_params={'vdc_id': 'pk'},
        verbose_name=_('Interfaces')
    )

    comments = columns.MarkdownColumn()

    tags = columns.TagColumn(
        url_name='dcim:virtualdevicecontext_list'
    )

    class Meta(NetBoxTable.Meta):
        model = models.VirtualDeviceContext
        fields = (
            'pk', 'id', 'name', 'status', 'identifier', 'tenant', 'tenant_group', 'primary_ip', 'primary_ip4',
            'primary_ip6', 'comments', 'tags', 'interface_count', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'identifier', 'status', 'tenant', 'primary_ip',
        )
