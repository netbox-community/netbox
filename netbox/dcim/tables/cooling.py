import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from django_tables2.utils import Accessor

from dcim import models
from dcim.models import CoolingFeed, CoolingSource
from netbox.tables import PrimaryModelTable, columns
from tenancy.tables import ContactsColumnMixin, TenancyColumnsMixin

from .devices import DeviceComponentTable, ModularDeviceComponentTable
from .devicetypes import ComponentTemplateTable
from .template_code import (
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
    coolingfeed_count = columns.LinkedCountColumn(
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
            'return_temperature', 'temperature_unit', 'coolingfeed_count', 'contacts', 'description', 'comments',
            'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'site', 'location', 'type', 'status', 'cooling_capacity', 'coolingfeed_count',
        )


#
# Cooling feeds
#

class CoolingFeedTable(TenancyColumnsMixin, PrimaryModelTable):
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
    flow_direction = columns.ChoiceFieldColumn(
        verbose_name=_('Flow Direction'),
    )
    fluid_type = columns.ChoiceFieldColumn(
        verbose_name=_('Fluid Type'),
    )
    cooling_capacity = tables.Column(
        verbose_name=_('Cooling Capacity (kW)')
    )
    rated_flow_rate = tables.Column(
        verbose_name=_('Rated Flow Rate'),
        order_by=('_abs_rated_flow_rate',)
    )
    rated_flow_rate_unit = columns.ChoiceFieldColumn(
        verbose_name=_('Rated Flow Rate Unit'),
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

    class Meta(PrimaryModelTable.Meta):
        model = CoolingFeed
        fields = (
            'pk', 'id', 'name', 'cooling_source', 'site', 'rack', 'status', 'flow_direction', 'fluid_type',
            'cooling_capacity', 'rated_flow_rate', 'rated_flow_rate_unit', 'supply_temperature',
            'return_temperature', 'temperature_unit', 'tenant', 'tenant_group', 'description', 'comments', 'tags',
            'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'cooling_source', 'rack', 'status', 'flow_direction', 'fluid_type', 'cooling_capacity',
            'rated_flow_rate',
        )


#
# Cooling ports
#

class CoolingPortTable(ModularDeviceComponentTable):
    device = tables.Column(
        verbose_name=_('Device'),
        linkify={
            'viewname': 'dcim:device_coolingports',
            'args': [Accessor('device_id')],
        }
    )
    flow_direction = columns.ChoiceFieldColumn(
        verbose_name=_('Flow Direction'),
    )
    type = columns.ChoiceFieldColumn(
        verbose_name=_('Type'),
    )
    diameter = columns.TemplateColumn(
        verbose_name=_('Diameter'),
        template_code=DIAMETER,
        order_by=('_abs_diameter', 'diameter_unit')
    )
    maximum_flow = tables.Column(
        verbose_name=_('Maximum flow'),
        order_by=('_abs_maximum_flow',)
    )
    maximum_flow_unit = columns.ChoiceFieldColumn(
        verbose_name=_('Maximum Flow Unit')
    )
    heat_capacity = tables.Column(
        verbose_name=_('Heat capacity (kW)')
    )
    cooling_outlet = tables.Column(
        verbose_name=_('Cooling Outlet'),
        linkify=True
    )
    cooling_feed = tables.Column(
        verbose_name=_('Cooling Feed'),
        linkify=True
    )
    tags = columns.TagColumn(
        url_name='dcim:coolingport_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.CoolingPort
        fields = (
            'pk', 'id', 'name', 'device', 'module_bay', 'module', 'label', 'flow_direction', 'type', 'diameter',
            'description', 'maximum_flow', 'maximum_flow_unit', 'heat_capacity', 'cooling_outlet', 'cooling_feed',
            'inventory_items', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'device', 'label', 'flow_direction', 'type', 'diameter', 'maximum_flow', 'heat_capacity',
            'description',
        )


#
# Cooling outlets
#

class CoolingOutletTable(ModularDeviceComponentTable):
    device = tables.Column(
        verbose_name=_('Device'),
        linkify={
            'viewname': 'dcim:device_coolingoutlets',
            'args': [Accessor('device_id')],
        }
    )
    flow_direction = columns.ChoiceFieldColumn(
        verbose_name=_('Flow Direction'),
    )
    type = columns.ChoiceFieldColumn(
        verbose_name=_('Type'),
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
            'pk', 'id', 'name', 'device', 'module_bay', 'module', 'label', 'flow_direction', 'type', 'diameter',
            'description', 'cooling_port', 'color', 'inventory_items', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'device', 'label', 'flow_direction', 'type', 'diameter', 'color', 'cooling_port',
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
    maximum_flow = tables.Column(
        verbose_name=_('Maximum flow'),
        order_by=('_abs_maximum_flow',)
    )
    maximum_flow_unit = columns.ChoiceFieldColumn(
        verbose_name=_('Maximum Flow Unit')
    )
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=MODULAR_COMPONENT_TEMPLATE_BUTTONS
    )

    class Meta(ComponentTemplateTable.Meta):
        model = models.CoolingPortTemplate
        fields = (
            'pk', 'name', 'label', 'flow_direction', 'type', 'diameter', 'maximum_flow', 'maximum_flow_unit',
            'heat_capacity', 'description', 'actions',
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
            'pk', 'name', 'label', 'flow_direction', 'type', 'diameter', 'color', 'cooling_port', 'description',
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

    class Meta(DeviceComponentTable.Meta):
        model = models.CoolingPort
        fields = (
            'pk', 'id', 'name', 'module_bay', 'module', 'label', 'flow_direction', 'type', 'diameter', 'maximum_flow',
            'maximum_flow_unit', 'heat_capacity', 'description', 'cooling_outlet', 'cooling_feed', 'tags', 'actions',
        )
        default_columns = (
            'pk', 'name', 'label', 'flow_direction', 'type', 'diameter', 'maximum_flow', 'heat_capacity',
            'description',
        )


class DeviceCoolingOutletTable(CoolingOutletTable):
    name = tables.TemplateColumn(
        verbose_name=_('Name'),
        template_code='<i class="mdi mdi-snowflake"></i> <a href="{{ record.get_absolute_url }}">{{ value }}</a>',
        attrs={'td': {'class': 'text-nowrap'}}
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.CoolingOutlet
        fields = (
            'pk', 'id', 'name', 'module_bay', 'module', 'label', 'flow_direction', 'type', 'diameter', 'color',
            'cooling_port', 'description', 'tags', 'actions',
        )
        default_columns = (
            'pk', 'name', 'label', 'flow_direction', 'type', 'diameter', 'color', 'cooling_port', 'description',
        )
