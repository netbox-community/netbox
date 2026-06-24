import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from django_tables2.utils import Accessor

from dcim import models
from dcim.models import CoolingFeed, CoolingSource
from netbox.tables import PrimaryModelTable, columns
from tenancy.tables import ContactsColumnMixin, TenancyColumnsMixin

from .devices import CableTerminationTable, DeviceComponentTable, ModularDeviceComponentTable, PathEndpointTable
from .devicetypes import ComponentTemplateTable
from .template_code import (
    COOLINGOUTLET_BUTTONS,
    COOLINGPORT_BUTTONS,
    DIAMETER,
    MODULAR_COMPONENT_TEMPLATE_BUTTONS,
)

__all__ = (
    'CoolingFeedTable',
    'CoolingOutletTable',
    'CoolingOutletTemplateTable',
    'CoolingPortTable',
    'CoolingPortTemplateTable',
    'CoolingSourceTable',
    'DeviceCoolingOutletTable',
    'DeviceCoolingPortTable',
)


#
# Cooling sources
#

class CoolingSourceTable(ContactsColumnMixin, PrimaryModelTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    site = tables.Column(
        verbose_name=_('Site'),
        linkify=True
    )
    location = tables.Column(
        verbose_name=_('Location'),
        linkify=True
    )
    status = columns.ChoiceFieldColumn(
        verbose_name=_('Status'),
    )
    type = columns.ChoiceFieldColumn(
        verbose_name=_('Type'),
    )
    cooling_capacity = tables.Column(
        verbose_name=_('Cooling Capacity (kW)')
    )
    supply_temperature = tables.Column(
        verbose_name=_('Supply Temperature'),
        order_by=('_abs_supply_temperature',)
    )
    return_temperature = tables.Column(
        verbose_name=_('Return Temperature'),
        order_by=('_abs_return_temperature',)
    )
    temperature_unit = columns.ChoiceFieldColumn(
        verbose_name=_('Temperature Unit'),
    )
    cooling_feed_count = columns.LinkedCountColumn(
        viewname='dcim:coolingfeed_list',
        url_params={'cooling_source_id': 'pk'},
        verbose_name=_('Cooling Feeds')
    )
    tags = columns.TagColumn(
        url_name='dcim:coolingsource_list'
    )

    class Meta(PrimaryModelTable.Meta):
        model = CoolingSource
        fields = (
            'pk', 'id', 'name', 'site', 'location', 'type', 'status', 'cooling_capacity', 'supply_temperature',
            'return_temperature', 'temperature_unit', 'cooling_feed_count', 'contacts', 'description', 'comments',
            'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'site', 'location', 'type', 'status', 'cooling_capacity', 'cooling_feed_count',
        )


#
# Cooling feeds
#

# We're not using PathEndpointTable for CoolingFeed because cooling connections
# cannot traverse pass-through ports.
class CoolingFeedTable(TenancyColumnsMixin, CableTerminationTable, PrimaryModelTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    cooling_source = tables.Column(
        verbose_name=_('Cooling Source'),
        linkify=True
    )
    rack = tables.Column(
        verbose_name=_('Rack'),
        linkify=True
    )
    status = columns.ChoiceFieldColumn(
        verbose_name=_('Status'),
    )
    type = columns.ChoiceFieldColumn(
        verbose_name=_('Type'),
    )
    fluid_type = columns.ChoiceFieldColumn(
        verbose_name=_('Fluid Type'),
    )
    cooling_capacity = tables.Column(
        verbose_name=_('Cooling Capacity (kW)')
    )
    flow_rate = tables.Column(
        verbose_name=_('Flow Rate'),
        order_by=('_abs_flow_rate',)
    )
    flow_rate_unit = columns.ChoiceFieldColumn(
        verbose_name=_('Flow Rate Unit'),
    )
    pressure = tables.Column(
        verbose_name=_('Pressure'),
        order_by=('_abs_pressure',)
    )
    pressure_unit = columns.ChoiceFieldColumn(
        verbose_name=_('Pressure Unit'),
    )
    tenant = tables.Column(
        linkify=True,
        verbose_name=_('Tenant')
    )
    site = tables.Column(
        accessor='rack__site',
        linkify=True,
        verbose_name=_('Site'),
    )
    tags = columns.TagColumn(
        url_name='dcim:coolingfeed_list'
    )

    class Meta(CableTerminationTable.Meta, PrimaryModelTable.Meta):
        model = CoolingFeed
        fields = (
            'pk', 'id', 'name', 'cooling_source', 'site', 'rack', 'status', 'type', 'fluid_type', 'cooling_capacity',
            'flow_rate', 'flow_rate_unit', 'pressure', 'pressure_unit', 'mark_connected', 'cable', 'cable_color',
            'link_peer', 'tenant', 'tenant_group', 'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'cooling_source', 'rack', 'status', 'type', 'fluid_type', 'cooling_capacity', 'flow_rate',
            'cable', 'link_peer',
        )


#
# Cooling ports
#

class CoolingPortTable(ModularDeviceComponentTable, PathEndpointTable):
    device = tables.Column(
        verbose_name=_('Device'),
        linkify={
            'viewname': 'dcim:device_coolingports',
            'args': [Accessor('device_id')],
        }
    )
    type = columns.ChoiceFieldColumn(
        verbose_name=_('Type'),
    )
    connector_type = columns.ChoiceFieldColumn(
        verbose_name=_('Connector Type'),
    )
    diameter = columns.TemplateColumn(
        verbose_name=_('Diameter'),
        template_code=DIAMETER,
        order_by=('_abs_diameter', 'diameter_unit')
    )
    maximum_flow = tables.Column(
        verbose_name=_('Maximum flow (L/min)')
    )
    heat_capacity = tables.Column(
        verbose_name=_('Heat capacity (kW)')
    )
    tags = columns.TagColumn(
        url_name='dcim:coolingport_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.CoolingPort
        fields = (
            'pk', 'id', 'name', 'device', 'module_bay', 'module', 'label', 'type', 'connector_type', 'diameter',
            'description', 'mark_connected', 'maximum_flow', 'heat_capacity', 'cable', 'cable_color', 'link_peer',
            'connection', 'inventory_items', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'device', 'label', 'type', 'connector_type', 'diameter', 'maximum_flow', 'heat_capacity',
            'description',
        )


#
# Cooling outlets
#

class CoolingOutletTable(ModularDeviceComponentTable, PathEndpointTable):
    device = tables.Column(
        verbose_name=_('Device'),
        linkify={
            'viewname': 'dcim:device_coolingoutlets',
            'args': [Accessor('device_id')],
        }
    )
    type = columns.ChoiceFieldColumn(
        verbose_name=_('Type'),
    )
    connector_type = columns.ChoiceFieldColumn(
        verbose_name=_('Connector Type'),
    )
    diameter = columns.TemplateColumn(
        verbose_name=_('Diameter'),
        template_code=DIAMETER,
        order_by=('_abs_diameter', 'diameter_unit')
    )
    cooling_port = tables.Column(
        verbose_name=_('Cooling Port'),
        linkify=True
    )
    color = columns.ColorColumn()
    tags = columns.TagColumn(
        url_name='dcim:coolingoutlet_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.CoolingOutlet
        fields = (
            'pk', 'id', 'name', 'device', 'module_bay', 'module', 'label', 'type', 'connector_type', 'diameter',
            'description', 'cooling_port', 'color', 'mark_connected', 'cable', 'cable_color', 'link_peer', 'connection',
            'inventory_items', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'device', 'label', 'type', 'connector_type', 'diameter', 'color', 'cooling_port',
            'description',
        )


#
# Cooling port templates
#

class CoolingPortTemplateTable(ComponentTemplateTable):
    diameter = columns.TemplateColumn(
        verbose_name=_('Diameter'),
        template_code=DIAMETER,
        order_by=('_abs_diameter', 'diameter_unit')
    )
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=MODULAR_COMPONENT_TEMPLATE_BUTTONS
    )

    class Meta(ComponentTemplateTable.Meta):
        model = models.CoolingPortTemplate
        fields = (
            'pk', 'name', 'label', 'type', 'connector_type', 'diameter', 'maximum_flow', 'heat_capacity',
            'description', 'actions',
        )
        empty_text = "None"


#
# Cooling outlet templates
#

class CoolingOutletTemplateTable(ComponentTemplateTable):
    diameter = columns.TemplateColumn(
        verbose_name=_('Diameter'),
        template_code=DIAMETER,
        order_by=('_abs_diameter', 'diameter_unit')
    )
    color = columns.ColorColumn(
        verbose_name=_('Color'),
    )
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=MODULAR_COMPONENT_TEMPLATE_BUTTONS
    )

    class Meta(ComponentTemplateTable.Meta):
        model = models.CoolingOutletTemplate
        fields = (
            'pk', 'name', 'label', 'type', 'connector_type', 'diameter', 'color', 'cooling_port', 'description',
            'actions',
        )
        empty_text = "None"


#
# Device cooling components
#

class DeviceCoolingPortTable(CoolingPortTable):
    name = tables.TemplateColumn(
        verbose_name=_('Name'),
        template_code='<i class="mdi mdi-snowflake"></i> <a href="{{ record.get_absolute_url }}">{{ value }}</a>',
        attrs={'td': {'class': 'text-nowrap'}}
    )
    actions = columns.ActionsColumn(
        extra_buttons=COOLINGPORT_BUTTONS
    )

    class Meta(CableTerminationTable.Meta, DeviceComponentTable.Meta):
        model = models.CoolingPort
        fields = (
            'pk', 'id', 'name', 'module_bay', 'module', 'label', 'type', 'connector_type', 'diameter', 'maximum_flow',
            'heat_capacity', 'description', 'mark_connected', 'cable', 'cable_color', 'link_peer', 'connection', 'tags',
            'actions',
        )
        default_columns = (
            'pk', 'name', 'label', 'type', 'connector_type', 'diameter', 'maximum_flow', 'heat_capacity',
            'description', 'cable', 'connection',
        )


class DeviceCoolingOutletTable(CoolingOutletTable):
    name = tables.TemplateColumn(
        verbose_name=_('Name'),
        template_code='<i class="mdi mdi-snowflake"></i> <a href="{{ record.get_absolute_url }}">{{ value }}</a>',
        attrs={'td': {'class': 'text-nowrap'}}
    )
    actions = columns.ActionsColumn(
        extra_buttons=COOLINGOUTLET_BUTTONS
    )

    class Meta(CableTerminationTable.Meta, DeviceComponentTable.Meta):
        model = models.CoolingOutlet
        fields = (
            'pk', 'id', 'name', 'module_bay', 'module', 'label', 'type', 'connector_type', 'diameter', 'color',
            'cooling_port', 'description', 'mark_connected', 'cable', 'cable_color', 'link_peer', 'connection', 'tags',
            'actions',
        )
        default_columns = (
            'pk', 'name', 'label', 'type', 'connector_type', 'diameter', 'color', 'cooling_port', 'description',
            'cable', 'connection',
        )
