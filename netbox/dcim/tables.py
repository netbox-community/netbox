import django_tables2 as tables
from django_tables2.utils import Accessor

from tenancy.tables import COL_TENANT
from utilities.tables import (
    BaseTable, BooleanColumn, ButtonsColumn, ChoiceFieldColumn, ColorColumn, ColoredLabelColumn, LinkedCountColumn,
    TagColumn, ToggleColumn,
)
from .models import (
    Cable, ConsolePort, ConsolePortTemplate, ConsoleServerPort, ConsoleServerPortTemplate, Device, DeviceBay,
    DeviceBayTemplate, DeviceRole, DeviceType, FrontPort, FrontPortTemplate, Interface, InterfaceTemplate,
    InventoryItem, Manufacturer, Platform, PowerFeed, PowerOutlet, PowerOutletTemplate, PowerPanel, PowerPort,
    PowerPortTemplate, Rack, RackGroup, RackReservation, RackRole, RearPort, RearPortTemplate, Region, Site,
    VirtualChassis,
)

MPTT_LINK = """
{% if record.get_children %}
    <span style="padding-left: {{ record.get_ancestors|length }}0px "><i class="fa fa-caret-right"></i>
{% else %}
    <span style="padding-left: {{ record.get_ancestors|length }}9px">
{% endif %}
    <a href="{{ record.get_absolute_url }}">{{ record.name }}</a>
</span>
"""

DEVICE_LINK = """
<a href="{% url 'dcim:device' pk=record.pk %}">
    {{ record.name|default:'<span class="label label-info">Unnamed device</span>' }}
</a>
"""

RACKGROUP_ELEVATIONS = """
<a href="{% url 'dcim:rack_elevation_list' %}?site={{ record.site.slug }}&group_id={{ record.pk }}" class="btn btn-xs btn-primary" title="View elevations">
    <i class="fa fa-eye"></i>
</a>
"""

UTILIZATION_GRAPH = """
{% load helpers %}
{% utilization_graph value %}
"""

CABLE_TERMINATION_PARENT = """
{% if value.device %}
    <a href="{{ value.device.get_absolute_url }}">{{ value.device }}</a>
{% elif value.circuit %}
    <a href="{{ value.circuit.get_absolute_url }}">{{ value.circuit }}</a>
{% elif value.power_panel %}
    <a href="{{ value.power_panel.get_absolute_url }}">{{ value.power_panel }}</a>
{% endif %}
"""

CABLE_LENGTH = """
{% if record.length %}{{ record.length }} {{ record.get_length_unit_display }}{% else %}&mdash;{% endif %}
"""

INTERFACE_IPADDRESSES = """
{% for ip in record.ip_addresses.unrestricted %}
    <a href="{{ ip.get_absolute_url }}">{{ ip }}</a><br />
{% endfor %}
"""

INTERFACE_TAGGED_VLANS = """
{% for vlan in record.tagged_vlans.unrestricted %}
    <a href="{{ vlan.get_absolute_url }}">{{ vlan }}</a><br />
{% endfor %}
"""

PATH_STATUS = """
<span class="label label-{% if value %}success{% else %}danger{% endif %}">{% if value %}Connected{% else %}Not Connected{% endif %}</span>
"""


#
# Regions
#

class RegionTable(BaseTable):
    pk = ToggleColumn()
    name = tables.TemplateColumn(
        template_code=MPTT_LINK,
        orderable=False
    )
    site_count = tables.Column(
        verbose_name='Sites'
    )
    actions = ButtonsColumn(Region)

    class Meta(BaseTable.Meta):
        model = Region
        fields = ('pk', 'name', 'slug', 'site_count', 'description', 'actions')
        default_columns = ('pk', 'name', 'site_count', 'description', 'actions')


#
# Sites
#

class SiteTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn(
        order_by=('_name',)
    )
    status = ChoiceFieldColumn()
    region = tables.Column(
        linkify=True
    )
    tenant = tables.TemplateColumn(
        template_code=COL_TENANT
    )
    tags = TagColumn(
        url_name='dcim:site_list'
    )

    class Meta(BaseTable.Meta):
        model = Site
        fields = (
            'pk', 'name', 'slug', 'status', 'facility', 'region', 'tenant', 'asn', 'time_zone', 'description',
            'physical_address', 'shipping_address', 'latitude', 'longitude', 'contact_name', 'contact_phone',
            'contact_email', 'tags',
        )
        default_columns = ('pk', 'name', 'status', 'facility', 'region', 'tenant', 'asn', 'description')


#
# Rack groups
#

class RackGroupTable(BaseTable):
    pk = ToggleColumn()
    name = tables.TemplateColumn(
        template_code=MPTT_LINK,
        orderable=False
    )
    site = tables.LinkColumn(
        viewname='dcim:site',
        args=[Accessor('site__slug')],
        verbose_name='Site'
    )
    rack_count = tables.Column(
        verbose_name='Racks'
    )
    actions = ButtonsColumn(
        model=RackGroup,
        prepend_template=RACKGROUP_ELEVATIONS
    )

    class Meta(BaseTable.Meta):
        model = RackGroup
        fields = ('pk', 'name', 'site', 'rack_count', 'description', 'slug', 'actions')
        default_columns = ('pk', 'name', 'site', 'rack_count', 'description', 'actions')


#
# Rack roles
#

class RackRoleTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    rack_count = tables.Column(verbose_name='Racks')
    color = ColorColumn()
    actions = ButtonsColumn(RackRole)

    class Meta(BaseTable.Meta):
        model = RackRole
        fields = ('pk', 'name', 'rack_count', 'color', 'description', 'slug', 'actions')
        default_columns = ('pk', 'name', 'rack_count', 'color', 'description', 'actions')


#
# Racks
#

class RackTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn(
        order_by=('_name',)
    )
    site = tables.LinkColumn(
        viewname='dcim:site',
        args=[Accessor('site__slug')]
    )
    tenant = tables.TemplateColumn(
        template_code=COL_TENANT
    )
    status = ChoiceFieldColumn()
    role = ColoredLabelColumn()
    u_height = tables.TemplateColumn(
        template_code="{{ record.u_height }}U",
        verbose_name='Height'
    )

    class Meta(BaseTable.Meta):
        model = Rack
        fields = (
            'pk', 'name', 'site', 'group', 'status', 'facility_id', 'tenant', 'role', 'serial', 'asset_tag', 'type',
            'width', 'u_height',
        )
        default_columns = ('pk', 'name', 'site', 'group', 'status', 'facility_id', 'tenant', 'role', 'u_height')


class RackDetailTable(RackTable):
    device_count = LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'rack_id': 'pk'},
        verbose_name='Devices'
    )
    get_utilization = tables.TemplateColumn(
        template_code=UTILIZATION_GRAPH,
        orderable=False,
        verbose_name='Space'
    )
    get_power_utilization = tables.TemplateColumn(
        template_code=UTILIZATION_GRAPH,
        orderable=False,
        verbose_name='Power'
    )
    tags = TagColumn(
        url_name='dcim:rack_list'
    )

    class Meta(RackTable.Meta):
        fields = (
            'pk', 'name', 'site', 'group', 'status', 'facility_id', 'tenant', 'role', 'serial', 'asset_tag', 'type',
            'width', 'u_height', 'device_count', 'get_utilization', 'get_power_utilization', 'tags',
        )
        default_columns = (
            'pk', 'name', 'site', 'group', 'status', 'facility_id', 'tenant', 'role', 'u_height', 'device_count',
            'get_utilization', 'get_power_utilization',
        )


#
# Rack reservations
#

class RackReservationTable(BaseTable):
    pk = ToggleColumn()
    reservation = tables.Column(
        accessor='pk',
        linkify=True
    )
    site = tables.Column(
        accessor=Accessor('rack__site'),
        linkify=True
    )
    tenant = tables.TemplateColumn(
        template_code=COL_TENANT
    )
    rack = tables.Column(
        linkify=True
    )
    unit_list = tables.Column(
        orderable=False,
        verbose_name='Units'
    )
    tags = TagColumn(
        url_name='dcim:rackreservation_list'
    )
    actions = ButtonsColumn(RackReservation)

    class Meta(BaseTable.Meta):
        model = RackReservation
        fields = (
            'pk', 'reservation', 'site', 'rack', 'unit_list', 'user', 'created', 'tenant', 'description', 'tags',
            'actions',
        )
        default_columns = (
            'pk', 'reservation', 'site', 'rack', 'unit_list', 'user', 'description', 'actions',
        )


#
# Manufacturers
#

class ManufacturerTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    devicetype_count = tables.Column(
        verbose_name='Device Types'
    )
    inventoryitem_count = tables.Column(
        verbose_name='Inventory Items'
    )
    platform_count = tables.Column(
        verbose_name='Platforms'
    )
    slug = tables.Column()
    actions = ButtonsColumn(Manufacturer, pk_field='slug')

    class Meta(BaseTable.Meta):
        model = Manufacturer
        fields = (
            'pk', 'name', 'devicetype_count', 'inventoryitem_count', 'platform_count', 'description', 'slug', 'actions',
        )


#
# Device types
#

class DeviceTypeTable(BaseTable):
    pk = ToggleColumn()
    model = tables.Column(
        linkify=True,
        verbose_name='Device Type'
    )
    is_full_depth = BooleanColumn(
        verbose_name='Full Depth'
    )
    instance_count = LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'device_type_id': 'pk'},
        verbose_name='Instances'
    )
    tags = TagColumn(
        url_name='dcim:devicetype_list'
    )

    class Meta(BaseTable.Meta):
        model = DeviceType
        fields = (
            'pk', 'model', 'manufacturer', 'slug', 'part_number', 'u_height', 'is_full_depth', 'subdevice_role',
            'instance_count', 'tags',
        )
        default_columns = (
            'pk', 'model', 'manufacturer', 'part_number', 'u_height', 'is_full_depth', 'instance_count',
        )


#
# Device type components
#

class ComponentTemplateTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        order_by=('_name',)
    )


class ConsolePortTemplateTable(ComponentTemplateTable):
    actions = ButtonsColumn(
        model=ConsolePortTemplate,
        buttons=('edit', 'delete')
    )

    class Meta(BaseTable.Meta):
        model = ConsolePortTemplate
        fields = ('pk', 'name', 'label', 'type', 'description', 'actions')
        empty_text = "None"


class ConsoleServerPortTemplateTable(ComponentTemplateTable):
    actions = ButtonsColumn(
        model=ConsoleServerPortTemplate,
        buttons=('edit', 'delete')
    )

    class Meta(BaseTable.Meta):
        model = ConsoleServerPortTemplate
        fields = ('pk', 'name', 'label', 'type', 'description', 'actions')
        empty_text = "None"


class PowerPortTemplateTable(ComponentTemplateTable):
    actions = ButtonsColumn(
        model=PowerPortTemplate,
        buttons=('edit', 'delete')
    )

    class Meta(BaseTable.Meta):
        model = PowerPortTemplate
        fields = ('pk', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description', 'actions')
        empty_text = "None"


class PowerOutletTemplateTable(ComponentTemplateTable):
    actions = ButtonsColumn(
        model=PowerOutletTemplate,
        buttons=('edit', 'delete')
    )

    class Meta(BaseTable.Meta):
        model = PowerOutletTemplate
        fields = ('pk', 'name', 'label', 'type', 'power_port', 'feed_leg', 'description', 'actions')
        empty_text = "None"


class InterfaceTemplateTable(ComponentTemplateTable):
    mgmt_only = BooleanColumn(
        verbose_name='Management Only'
    )
    actions = ButtonsColumn(
        model=InterfaceTemplate,
        buttons=('edit', 'delete')
    )

    class Meta(BaseTable.Meta):
        model = InterfaceTemplate
        fields = ('pk', 'name', 'label', 'mgmt_only', 'type', 'description', 'actions')
        empty_text = "None"


class FrontPortTemplateTable(ComponentTemplateTable):
    rear_port_position = tables.Column(
        verbose_name='Position'
    )
    actions = ButtonsColumn(
        model=FrontPortTemplate,
        buttons=('edit', 'delete')
    )

    class Meta(BaseTable.Meta):
        model = FrontPortTemplate
        fields = ('pk', 'name', 'label', 'type', 'rear_port', 'rear_port_position', 'description', 'actions')
        empty_text = "None"


class RearPortTemplateTable(ComponentTemplateTable):
    actions = ButtonsColumn(
        model=RearPortTemplate,
        buttons=('edit', 'delete')
    )

    class Meta(BaseTable.Meta):
        model = RearPortTemplate
        fields = ('pk', 'name', 'label', 'type', 'positions', 'description', 'actions')
        empty_text = "None"


class DeviceBayTemplateTable(ComponentTemplateTable):
    actions = ButtonsColumn(
        model=DeviceBayTemplate,
        buttons=('edit', 'delete')
    )

    class Meta(BaseTable.Meta):
        model = DeviceBayTemplate
        fields = ('pk', 'name', 'label', 'description', 'actions')
        empty_text = "None"


#
# Device roles
#

class DeviceRoleTable(BaseTable):
    pk = ToggleColumn()
    device_count = LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'role': 'slug'},
        verbose_name='Devices'
    )
    vm_count = LinkedCountColumn(
        viewname='virtualization:virtualmachine_list',
        url_params={'role': 'slug'},
        verbose_name='VMs'
    )
    color = ColorColumn()
    vm_role = BooleanColumn()
    actions = ButtonsColumn(DeviceRole, pk_field='slug')

    class Meta(BaseTable.Meta):
        model = DeviceRole
        fields = ('pk', 'name', 'device_count', 'vm_count', 'color', 'vm_role', 'description', 'slug', 'actions')
        default_columns = ('pk', 'name', 'device_count', 'vm_count', 'color', 'vm_role', 'description', 'actions')


#
# Platforms
#

class PlatformTable(BaseTable):
    pk = ToggleColumn()
    device_count = LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'platform': 'slug'},
        verbose_name='Devices'
    )
    vm_count = LinkedCountColumn(
        viewname='virtualization:virtualmachine_list',
        url_params={'platform': 'slug'},
        verbose_name='VMs'
    )
    actions = ButtonsColumn(Platform, pk_field='slug')

    class Meta(BaseTable.Meta):
        model = Platform
        fields = (
            'pk', 'name', 'manufacturer', 'device_count', 'vm_count', 'slug', 'napalm_driver', 'napalm_args',
            'description', 'actions',
        )
        default_columns = (
            'pk', 'name', 'manufacturer', 'device_count', 'vm_count', 'napalm_driver', 'description', 'actions',
        )


#
# Devices
#

class DeviceTable(BaseTable):
    pk = ToggleColumn()
    name = tables.TemplateColumn(
        order_by=('_name',),
        template_code=DEVICE_LINK
    )
    status = ChoiceFieldColumn()
    tenant = tables.TemplateColumn(
        template_code=COL_TENANT
    )
    site = tables.Column(
        linkify=True
    )
    rack = tables.Column(
        linkify=True
    )
    device_role = ColoredLabelColumn(
        verbose_name='Role'
    )
    device_type = tables.LinkColumn(
        viewname='dcim:devicetype',
        args=[Accessor('device_type__pk')],
        verbose_name='Type',
        text=lambda record: record.device_type.display_name
    )
    primary_ip = tables.Column(
        linkify=True,
        verbose_name='IP Address'
    )
    primary_ip4 = tables.Column(
        linkify=True,
        verbose_name='IPv4 Address'
    )
    primary_ip6 = tables.Column(
        linkify=True,
        verbose_name='IPv6 Address'
    )
    cluster = tables.LinkColumn(
        viewname='virtualization:cluster',
        args=[Accessor('cluster__pk')]
    )
    virtual_chassis = tables.LinkColumn(
        viewname='dcim:virtualchassis',
        args=[Accessor('virtual_chassis__pk')]
    )
    vc_position = tables.Column(
        verbose_name='VC Position'
    )
    vc_priority = tables.Column(
        verbose_name='VC Priority'
    )
    tags = TagColumn(
        url_name='dcim:device_list'
    )

    class Meta(BaseTable.Meta):
        model = Device
        fields = (
            'pk', 'name', 'status', 'tenant', 'device_role', 'device_type', 'platform', 'serial', 'asset_tag', 'site',
            'rack', 'position', 'face', 'primary_ip', 'primary_ip4', 'primary_ip6', 'cluster', 'virtual_chassis',
            'vc_position', 'vc_priority', 'tags',
        )
        default_columns = (
            'pk', 'name', 'status', 'tenant', 'site', 'rack', 'device_role', 'device_type', 'primary_ip',
        )


class DeviceImportTable(BaseTable):
    name = tables.TemplateColumn(
        template_code=DEVICE_LINK
    )
    status = ChoiceFieldColumn()
    tenant = tables.TemplateColumn(
        template_code=COL_TENANT
    )
    site = tables.Column(
        linkify=True
    )
    rack = tables.Column(
        linkify=True
    )
    device_role = tables.Column(
        verbose_name='Role'
    )
    device_type = tables.Column(
        verbose_name='Type'
    )

    class Meta(BaseTable.Meta):
        model = Device
        fields = ('name', 'status', 'tenant', 'site', 'rack', 'position', 'device_role', 'device_type')
        empty_text = False


#
# Device components
#

class DeviceComponentTable(BaseTable):
    pk = ToggleColumn()
    device = tables.Column(
        linkify=True
    )
    name = tables.Column(
        linkify=True,
        order_by=('_name',)
    )
    cable = tables.Column(
        linkify=True
    )

    class Meta(BaseTable.Meta):
        order_by = ('device', 'name')


class ConsolePortTable(DeviceComponentTable):
    tags = TagColumn(
        url_name='dcim:consoleport_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = ConsolePort
        fields = ('pk', 'device', 'name', 'label', 'type', 'description', 'cable', 'tags')
        default_columns = ('pk', 'device', 'name', 'label', 'type', 'description')


class ConsoleServerPortTable(DeviceComponentTable):
    tags = TagColumn(
        url_name='dcim:consoleserverport_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = ConsoleServerPort
        fields = ('pk', 'device', 'name', 'label', 'type', 'description', 'cable', 'tags')
        default_columns = ('pk', 'device', 'name', 'label', 'type', 'description')


class PowerPortTable(DeviceComponentTable):
    tags = TagColumn(
        url_name='dcim:powerport_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = PowerPort
        fields = (
            'pk', 'device', 'name', 'label', 'type', 'description', 'maximum_draw', 'allocated_draw', 'cable', 'tags',
        )
        default_columns = ('pk', 'device', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description')


class PowerOutletTable(DeviceComponentTable):
    tags = TagColumn(
        url_name='dcim:poweroutlet_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = PowerOutlet
        fields = ('pk', 'device', 'name', 'label', 'type', 'description', 'power_port', 'feed_leg', 'cable', 'tags')
        default_columns = ('pk', 'device', 'name', 'label', 'type', 'power_port', 'feed_leg', 'description')


class BaseInterfaceTable(BaseTable):
    enabled = BooleanColumn()
    ip_addresses = tables.TemplateColumn(
        template_code=INTERFACE_IPADDRESSES,
        orderable=False,
        verbose_name='IP Addresses'
    )
    untagged_vlan = tables.Column(linkify=True)
    tagged_vlans = tables.TemplateColumn(
        template_code=INTERFACE_TAGGED_VLANS,
        orderable=False,
        verbose_name='Tagged VLANs'
    )


class InterfaceTable(DeviceComponentTable, BaseInterfaceTable):
    tags = TagColumn(
        url_name='dcim:interface_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = Interface
        fields = (
            'pk', 'device', 'name', 'label', 'enabled', 'type', 'mgmt_only', 'mtu', 'mode', 'mac_address',
            'description', 'cable', 'tags', 'ip_addresses', 'untagged_vlan', 'tagged_vlans',
        )
        default_columns = ('pk', 'device', 'name', 'label', 'enabled', 'type', 'description')


class FrontPortTable(DeviceComponentTable):
    rear_port_position = tables.Column(
        verbose_name='Position'
    )
    tags = TagColumn(
        url_name='dcim:frontport_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = FrontPort
        fields = (
            'pk', 'device', 'name', 'label', 'type', 'rear_port', 'rear_port_position', 'description', 'cable', 'tags',
        )
        default_columns = ('pk', 'device', 'name', 'label', 'type', 'rear_port', 'rear_port_position', 'description')


class RearPortTable(DeviceComponentTable):
    tags = TagColumn(
        url_name='dcim:rearport_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = RearPort
        fields = ('pk', 'device', 'name', 'label', 'type', 'positions', 'description', 'cable', 'tags')
        default_columns = ('pk', 'device', 'name', 'label', 'type', 'description')


class DeviceBayTable(DeviceComponentTable):
    installed_device = tables.Column(
        linkify=True
    )
    tags = TagColumn(
        url_name='dcim:devicebay_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = DeviceBay
        fields = ('pk', 'device', 'name', 'label', 'installed_device', 'description', 'tags')
        default_columns = ('pk', 'device', 'name', 'label', 'installed_device', 'description')


class InventoryItemTable(DeviceComponentTable):
    manufacturer = tables.Column(
        linkify=True
    )
    discovered = BooleanColumn()
    tags = TagColumn(
        url_name='dcim:inventoryitem_list'
    )
    cable = None  # Override DeviceComponentTable

    class Meta(DeviceComponentTable.Meta):
        model = InventoryItem
        fields = (
            'pk', 'device', 'name', 'label', 'manufacturer', 'part_id', 'serial', 'asset_tag', 'description',
            'discovered', 'tags',
        )
        default_columns = ('pk', 'device', 'name', 'label', 'manufacturer', 'part_id', 'serial', 'asset_tag')


#
# Cables
#

class CableTable(BaseTable):
    pk = ToggleColumn()
    id = tables.Column(
        linkify=True,
        verbose_name='ID'
    )
    termination_a_parent = tables.TemplateColumn(
        template_code=CABLE_TERMINATION_PARENT,
        accessor=Accessor('termination_a'),
        orderable=False,
        verbose_name='Side A'
    )
    termination_a = tables.LinkColumn(
        accessor=Accessor('termination_a'),
        orderable=False,
        verbose_name='Termination A'
    )
    termination_b_parent = tables.TemplateColumn(
        template_code=CABLE_TERMINATION_PARENT,
        accessor=Accessor('termination_b'),
        orderable=False,
        verbose_name='Side B'
    )
    termination_b = tables.LinkColumn(
        accessor=Accessor('termination_b'),
        orderable=False,
        verbose_name='Termination B'
    )
    status = ChoiceFieldColumn()
    length = tables.TemplateColumn(
        template_code=CABLE_LENGTH,
        order_by='_abs_length'
    )
    color = ColorColumn()
    tags = TagColumn(
        url_name='dcim:cable_list'
    )

    class Meta(BaseTable.Meta):
        model = Cable
        fields = (
            'pk', 'id', 'label', 'termination_a_parent', 'termination_a', 'termination_b_parent', 'termination_b',
            'status', 'type', 'color', 'length', 'tags',
        )
        default_columns = (
            'pk', 'id', 'label', 'termination_a_parent', 'termination_a', 'termination_b_parent', 'termination_b',
            'status', 'type',
        )


#
# Device connections
#

class ConsoleConnectionTable(BaseTable):
    console_server = tables.Column(
        accessor=Accessor('_path__destination__device'),
        orderable=False,
        linkify=True,
        verbose_name='Console Server'
    )
    console_server_port = tables.Column(
        accessor=Accessor('_path__destination'),
        orderable=False,
        linkify=True,
        verbose_name='Port'
    )
    device = tables.Column(
        linkify=True
    )
    name = tables.Column(
        linkify=True,
        verbose_name='Console Port'
    )
    path_status = tables.TemplateColumn(
        accessor=Accessor('_path__is_connected'),
        template_code=PATH_STATUS,
        verbose_name='Path Status'
    )

    add_prefetch = False

    class Meta(BaseTable.Meta):
        model = ConsolePort
        fields = ('console_server', 'console_server_port', 'device', 'name', 'path_status')


class PowerConnectionTable(BaseTable):
    pdu = tables.Column(
        accessor=Accessor('_path__destination__device'),
        orderable=False,
        linkify=True,
        verbose_name='PDU'
    )
    outlet = tables.Column(
        accessor=Accessor('_path__destination'),
        orderable=False,
        linkify=True,
        verbose_name='Outlet'
    )
    device = tables.Column(
        linkify=True
    )
    name = tables.Column(
        linkify=True,
        verbose_name='Power Port'
    )
    path_status = tables.TemplateColumn(
        accessor=Accessor('_path__is_connected'),
        template_code=PATH_STATUS,
        verbose_name='Path Status'
    )

    add_prefetch = False

    class Meta(BaseTable.Meta):
        model = PowerPort
        fields = ('pdu', 'outlet', 'device', 'name', 'path_status')


class InterfaceConnectionTable(BaseTable):
    device_a = tables.Column(
        accessor=Accessor('device'),
        linkify=True,
        verbose_name='Device A'
    )
    interface_a = tables.Column(
        accessor=Accessor('name'),
        linkify=True,
        verbose_name='Interface A'
    )
    device_b = tables.Column(
        accessor=Accessor('_path__destination__device'),
        orderable=False,
        linkify=True,
        verbose_name='Device B'
    )
    interface_b = tables.Column(
        accessor=Accessor('_path__destination'),
        orderable=False,
        linkify=True,
        verbose_name='Interface B'
    )
    path_status = tables.TemplateColumn(
        accessor=Accessor('_path__is_connected'),
        template_code=PATH_STATUS,
        verbose_name='Path Status'
    )

    add_prefetch = False

    class Meta(BaseTable.Meta):
        model = Interface
        fields = ('device_a', 'interface_a', 'device_b', 'interface_b', 'path_status')


#
# Virtual chassis
#

class VirtualChassisTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    master = tables.Column(
        linkify=True
    )
    member_count = LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'virtual_chassis_id': 'pk'},
        verbose_name='Members'
    )
    tags = TagColumn(
        url_name='dcim:virtualchassis_list'
    )

    class Meta(BaseTable.Meta):
        model = VirtualChassis
        fields = ('pk', 'name', 'domain', 'master', 'member_count', 'tags')
        default_columns = ('pk', 'name', 'domain', 'master', 'member_count')


#
# Power panels
#

class PowerPanelTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    site = tables.LinkColumn(
        viewname='dcim:site',
        args=[Accessor('site__slug')]
    )
    powerfeed_count = LinkedCountColumn(
        viewname='dcim:powerfeed_list',
        url_params={'power_panel_id': 'pk'},
        verbose_name='Feeds'
    )
    tags = TagColumn(
        url_name='dcim:powerpanel_list'
    )

    class Meta(BaseTable.Meta):
        model = PowerPanel
        fields = ('pk', 'name', 'site', 'rack_group', 'powerfeed_count', 'tags')
        default_columns = ('pk', 'name', 'site', 'rack_group', 'powerfeed_count')


#
# Power feeds
#

class PowerFeedTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    power_panel = tables.Column(
        linkify=True
    )
    rack = tables.Column(
        linkify=True
    )
    status = ChoiceFieldColumn()
    type = ChoiceFieldColumn()
    max_utilization = tables.TemplateColumn(
        template_code="{{ value }}%"
    )
    available_power = tables.Column(
        verbose_name='Available power (VA)'
    )
    tags = TagColumn(
        url_name='dcim:powerfeed_list'
    )

    class Meta(BaseTable.Meta):
        model = PowerFeed
        fields = (
            'pk', 'name', 'power_panel', 'rack', 'status', 'type', 'supply', 'voltage', 'amperage', 'phase',
            'max_utilization', 'available_power', 'tags',
        )
        default_columns = (
            'pk', 'name', 'power_panel', 'rack', 'status', 'type', 'supply', 'voltage', 'amperage', 'phase',
        )
