import django_tables2 as tables

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
        linkify=True
    )
    devicetype_count = columns.LinkedCountColumn(
        viewname='dcim:devicetype_list',
        url_params={'manufacturer_id': 'pk'},
        verbose_name='Device Types'
    )
    moduletype_count = columns.LinkedCountColumn(
        viewname='dcim:moduletype_list',
        url_params={'manufacturer_id': 'pk'},
        verbose_name='Module Types'
    )
    inventoryitem_count = columns.LinkedCountColumn(
        viewname='dcim:inventoryitem_list',
        url_params={'manufacturer_id': 'pk'},
        verbose_name='Inventory Items'
    )
    platform_count = columns.LinkedCountColumn(
        viewname='dcim:platform_list',
        url_params={'manufacturer_id': 'pk'},
        verbose_name='Platforms'
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
        verbose_name='Device Type'
    )
    manufacturer = tables.Column(
        linkify=True
    )
    default_platform = tables.Column(
        linkify=True
    )
    is_full_depth = columns.BooleanColumn(
        verbose_name='Full Depth'
    )
    instance_count = columns.LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'device_type_id': 'pk'},
        verbose_name='Instances'
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='dcim:devicetype_list'
    )
    u_height = columns.TemplateColumn(
        template_code='{{ value|floatformat }}'
    )
    weight = columns.TemplateColumn(
        template_code=WEIGHT,
        order_by=('_abs_weight', 'weight_unit')
    )

    class Meta(NetBoxTable.Meta):
        model = models.DeviceType
        fields = (
            'pk', 'id', 'model', 'manufacturer', 'default_platform', 'slug', 'part_number', 'u_height', 'is_full_depth', 'subdevice_role',
            'airflow', 'weight', 'description', 'comments', 'instance_count', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'model', 'manufacturer', 'part_number', 'u_height', 'is_full_depth', 'instance_count',
        )


#
# Device type components
#

class ComponentTemplateTable(NetBoxTable):
    id = tables.Column(
        verbose_name='ID'
    )
    name = tables.Column(
        order_by=('_name',)
    )

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
    enabled = columns.BooleanColumn()
    mgmt_only = columns.BooleanColumn(
        verbose_name='Management Only'
    )
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=MODULAR_COMPONENT_TEMPLATE_BUTTONS
    )

    class Meta(ComponentTemplateTable.Meta):
        model = models.InterfaceTemplate
        fields = ('pk', 'name', 'label', 'enabled', 'mgmt_only', 'type', 'description', 'bridge', 'poe_mode', 'poe_type', 'actions')
        empty_text = "None"


class FrontPortTemplateTable(ComponentTemplateTable):
    rear_port_position = tables.Column(
        verbose_name='Position'
    )
    color = columns.ColorColumn()
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=MODULAR_COMPONENT_TEMPLATE_BUTTONS
    )

    class Meta(ComponentTemplateTable.Meta):
        model = models.FrontPortTemplate
        fields = ('pk', 'name', 'label', 'type', 'color', 'rear_port', 'rear_port_position', 'description', 'actions')
        empty_text = "None"


class RearPortTemplateTable(ComponentTemplateTable):
    color = columns.ColorColumn()
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
        linkify=True
    )
    manufacturer = tables.Column(
        linkify=True
    )
    component = tables.Column(
        orderable=False
    )

    class Meta(ComponentTemplateTable.Meta):
        model = models.InventoryItemTemplate
        fields = (
            'pk', 'name', 'label', 'parent', 'role', 'manufacturer', 'part_id', 'component', 'description', 'actions',
        )
        empty_text = "None"
