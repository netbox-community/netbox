import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from dcim import models
from netbox.tables import NetBoxTable, columns
from tenancy.tables import ContactsColumnMixin
from .template_code import MODULAR_COMPONENT_TEMPLATE_BUTTONS, WEIGHT

__all__ = (
    'ConsolePortTemplateTable',
    'ConsoleServerPortTemplateTable',
    'DeviceBayTemplateTable',
    'DeviceTypeTable',
    'FrontPortTemplateTable',
    'InterfaceTemplateTable',
    'InventoryItemTemplateTable',
    'ManufacturerTable',
    'ModuleBayTemplateTable',
    'PowerOutletTemplateTable',
    'PowerPortTemplateTable',
    'RearPortTemplateTable',
)


#
# Manufacturers
#

class ManufacturerTable(ContactsColumnMixin, NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    devicetype_count = columns.LinkedCountColumn(
        viewname='dcim:devicetype_list',
        url_params={'manufacturer_id': 'pk'},
        verbose_name=_('Device Types')
    )
    moduletype_count = columns.LinkedCountColumn(
        viewname='dcim:moduletype_list',
        url_params={'manufacturer_id': 'pk'},
        verbose_name=_('Module Types')
    )
    inventoryitem_count = columns.LinkedCountColumn(
        viewname='dcim:inventoryitem_list',
        url_params={'manufacturer_id': 'pk'},
        verbose_name=_('Inventory Items')
    )
    platform_count = columns.LinkedCountColumn(
        viewname='dcim:platform_list',
        url_params={'manufacturer_id': 'pk'},
        verbose_name=_('Platforms')
    )
    tags = columns.TagColumn(
        url_name='dcim:manufacturer_list'
    )

    class Meta(NetBoxTable.Meta):
        model = models.Manufacturer
        fields = (
            'pk', 'id', 'name', 'devicetype_count', 'moduletype_count', 'inventoryitem_count', 'platform_count',
            'description', 'slug', 'tags', 'contacts', 'actions', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'devicetype_count', 'moduletype_count', 'inventoryitem_count', 'platform_count',
            'description', 'slug',
        )


#
# Device types
#

class DeviceTypeTable(NetBoxTable):
    model = tables.Column(
        linkify=True,
        verbose_name=_('Device Type')
    )
    manufacturer = tables.Column(
        verbose_name=_('Manufacturer'),
        linkify=True
    )
    default_platform = tables.Column(
        verbose_name=_('Default Platform'),
        linkify=True
    )
    is_full_depth = columns.BooleanColumn(
        verbose_name=_('Full Depth'),
        false_mark=None
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
    tags = columns.TagColumn(
        url_name='dcim:devicetype_list'
    )
    u_height = columns.TemplateColumn(
        verbose_name=_('U Height'),
        template_code='{{ value|floatformat }}'
    )
    exclude_from_utilization = columns.BooleanColumn(
        verbose_name=_('Exclude from utilization'),
        false_mark=None
    )
    weight = columns.TemplateColumn(
        verbose_name=_('Weight'),
        template_code=WEIGHT,
        order_by=('_abs_weight', 'weight_unit')
    )
    instance_count = columns.LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'device_type_id': 'pk'},
        verbose_name=_('Instances')
    )
    console_port_template_count = tables.Column(
        verbose_name=_('Console Ports')
    )
    console_server_port_template_count = tables.Column(
        verbose_name=_('Console Server Ports')
    )
    power_port_template_count = tables.Column(
        verbose_name=_('Power Ports')
    )
    power_outlet_template_count = tables.Column(
        verbose_name=_('Power Outlets')
    )
    interface_template_count = tables.Column(
        verbose_name=_('Interfaces')
    )
    front_port_template_count = tables.Column(
        verbose_name=_('Front Ports')
    )
    rear_port_template_count = tables.Column(
        verbose_name=_('Rear Ports')
    )
    device_bay_template_count = tables.Column(
        verbose_name=_('Device Bays')
    )
    module_bay_template_count = tables.Column(
        verbose_name=_('Module Bays')
    )
    inventory_item_template_count = tables.Column(
        verbose_name=_('Inventory Items')
    )

    class Meta(NetBoxTable.Meta):
        model = models.DeviceType
        fields = (
            'pk', 'id', 'model', 'manufacturer', 'default_platform', 'slug', 'part_number', 'u_height',
            'exclude_from_utilization', 'is_full_depth', 'subdevice_role', 'airflow', 'weight',
            'description', 'comments', 'instance_count', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'model', 'manufacturer', 'part_number', 'u_height', 'is_full_depth', 'instance_count',
        )


#
# Device type components
#

class ComponentTemplateTable(NetBoxTable):
    id = tables.Column(
        verbose_name=_('ID')
    )
    name = tables.Column()

    class Meta(NetBoxTable.Meta):
        exclude = ('id', )


class ConsolePortTemplateTable(ComponentTemplateTable):
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=MODULAR_COMPONENT_TEMPLATE_BUTTONS
    )

    class Meta(ComponentTemplateTable.Meta):
        model = models.ConsolePortTemplate
        fields = ('pk', 'name', 'label', 'type', 'description', 'actions')
        empty_text = "None"


class ConsoleServerPortTemplateTable(ComponentTemplateTable):
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=MODULAR_COMPONENT_TEMPLATE_BUTTONS
    )

    class Meta(ComponentTemplateTable.Meta):
        model = models.ConsoleServerPortTemplate
        fields = ('pk', 'name', 'label', 'type', 'description', 'actions')
        empty_text = "None"


class PowerPortTemplateTable(ComponentTemplateTable):
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=MODULAR_COMPONENT_TEMPLATE_BUTTONS
    )

    class Meta(ComponentTemplateTable.Meta):
        model = models.PowerPortTemplate
        fields = ('pk', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description', 'actions')
        empty_text = "None"


class PowerOutletTemplateTable(ComponentTemplateTable):
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=MODULAR_COMPONENT_TEMPLATE_BUTTONS
    )

    class Meta(ComponentTemplateTable.Meta):
        model = models.PowerOutletTemplate
        fields = ('pk', 'name', 'label', 'type', 'power_port', 'feed_leg', 'description', 'actions')
        empty_text = "None"


class InterfaceTemplateTable(ComponentTemplateTable):
    name = tables.Column(
        verbose_name=_('Name'),
        order_by=('_name',)
    )
    enabled = columns.BooleanColumn(
        verbose_name=_('Enabled'),
    )
    mgmt_only = columns.BooleanColumn(
        verbose_name=_('Management Only'),
        false_mark=None
    )
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=MODULAR_COMPONENT_TEMPLATE_BUTTONS
    )

    class Meta(ComponentTemplateTable.Meta):
        model = models.InterfaceTemplate
        fields = (
            'pk', 'name', 'label', 'enabled', 'mgmt_only', 'type', 'description', 'bridge', 'poe_mode', 'poe_type',
            'rf_role', 'actions',
        )
        empty_text = "None"


class FrontPortTemplateTable(ComponentTemplateTable):
    rear_port_position = tables.Column(
        verbose_name=_('Position')
    )
    color = columns.ColorColumn(
        verbose_name=_('Color'),
    )
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=MODULAR_COMPONENT_TEMPLATE_BUTTONS
    )

    class Meta(ComponentTemplateTable.Meta):
        model = models.FrontPortTemplate
        fields = ('pk', 'name', 'label', 'type', 'color', 'rear_port', 'rear_port_position', 'description', 'actions')
        empty_text = "None"


class RearPortTemplateTable(ComponentTemplateTable):
    color = columns.ColorColumn(
        verbose_name=_('Color'),
    )
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=MODULAR_COMPONENT_TEMPLATE_BUTTONS
    )

    class Meta(ComponentTemplateTable.Meta):
        model = models.RearPortTemplate
        fields = ('pk', 'name', 'label', 'type', 'color', 'positions', 'description', 'actions')
        empty_text = "None"


class ModuleBayTemplateTable(ComponentTemplateTable):
    actions = columns.ActionsColumn(
        actions=('edit', 'delete')
    )

    class Meta(ComponentTemplateTable.Meta):
        model = models.ModuleBayTemplate
        fields = ('pk', 'name', 'label', 'position', 'description', 'actions')
        empty_text = "None"


class DeviceBayTemplateTable(ComponentTemplateTable):
    actions = columns.ActionsColumn(
        actions=('edit', 'delete')
    )

    class Meta(ComponentTemplateTable.Meta):
        model = models.DeviceBayTemplate
        fields = ('pk', 'name', 'label', 'description', 'actions')
        empty_text = "None"


class InventoryItemTemplateTable(ComponentTemplateTable):
    actions = columns.ActionsColumn(
        actions=('edit', 'delete')
    )
    role = tables.Column(
        verbose_name=_('Role'),
        linkify=True
    )
    manufacturer = tables.Column(
        verbose_name=_('Manufacturer'),
        linkify=True
    )
    component = tables.Column(
        verbose_name=_('Component'),
        orderable=False
    )

    class Meta(ComponentTemplateTable.Meta):
        model = models.InventoryItemTemplate
        fields = (
            'pk', 'name', 'label', 'parent', 'role', 'manufacturer', 'part_id', 'component', 'description', 'actions',
        )
        empty_text = "None"
