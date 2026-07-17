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
    'CoolingIntakeTable',
    'CoolingIntakeTemplateTable',
    'CoolingOutflowTable',
    'CoolingOutflowTemplateTable',
    'CoolingSourceTable',
    'DeviceCoolingIntakeTable',
    'DeviceCoolingOutflowTable',
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
    fluid_type = columns.ChoiceFieldColumn(
        verbose_name=_('Fluid Type'),
    )
    cooling_capacity = tables.Column(
        verbose_name=_('Cooling Capacity (kW)')
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
            'pk', 'id', 'name', 'site', 'location', 'type', 'status', 'fluid_type', 'cooling_capacity',
            'coolingfeed_count', 'contacts', 'description', 'comments', 'tags', 'created', 'last_updated',
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
            'pk', 'id', 'name', 'cooling_source', 'site', 'rack', 'status', 'flow_direction',
            'cooling_capacity', 'rated_flow_rate', 'rated_flow_rate_unit', 'tenant', 'tenant_group', 'description',
            'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'cooling_source', 'rack', 'status', 'flow_direction', 'cooling_capacity',
            'rated_flow_rate',
        )


#
# Cooling ports
#

class CoolingIntakeTable(ModularDeviceComponentTable):
    device = tables.Column(
        verbose_name=_('Device'),
        linkify={
            'viewname': 'dcim:device_coolingintakes',
            'args': [Accessor('device_id')],
        }
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
    cooling_outflow = tables.Column(
        verbose_name=_('Cooling Outlet'),
        linkify=True
    )
    cooling_feed = tables.Column(
        verbose_name=_('Cooling Feed'),
        linkify=True
    )
    tags = columns.TagColumn(
        url_name='dcim:coolingintake_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.CoolingIntake
        fields = (
            'pk', 'id', 'name', 'device', 'module_bay', 'module', 'label', 'type', 'diameter',
            'description', 'maximum_flow', 'maximum_flow_unit', 'cooling_outflow', 'cooling_feed',
            'inventory_items', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'device', 'label', 'type', 'diameter', 'maximum_flow',
            'description',
        )


#
# Cooling outlets
#

class CoolingOutflowTable(ModularDeviceComponentTable):
    device = tables.Column(
        verbose_name=_('Device'),
        linkify={
            'viewname': 'dcim:device_coolingoutflows',
            'args': [Accessor('device_id')],
        }
    )
    type = columns.ChoiceFieldColumn(
        verbose_name=_('Type'),
    )
    diameter = columns.TemplateColumn(
        verbose_name=_('Diameter'),
        template_code=DIAMETER,
        order_by=('_abs_diameter', 'diameter_unit')
    )
    cooling_intake = tables.Column(
        verbose_name=_('Cooling Port'),
        linkify=True
    )
    tags = columns.TagColumn(
        url_name='dcim:coolingoutflow_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.CoolingOutflow
        fields = (
            'pk', 'id', 'name', 'device', 'module_bay', 'module', 'label', 'type', 'diameter',
            'description', 'cooling_intake', 'inventory_items', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'device', 'label', 'type', 'diameter', 'cooling_intake',
            'description',
        )


#
# Cooling port templates
#

class CoolingIntakeTemplateTable(ComponentTemplateTable):
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
        model = models.CoolingIntakeTemplate
        fields = (
            'pk', 'name', 'label', 'type', 'diameter', 'maximum_flow', 'maximum_flow_unit',
            'description', 'actions',
        )
        empty_text = "None"


#
# Cooling outlet templates
#

class CoolingOutflowTemplateTable(ComponentTemplateTable):
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
        model = models.CoolingOutflowTemplate
        fields = (
            'pk', 'name', 'label', 'type', 'diameter', 'cooling_intake', 'description',
            'actions',
        )
        empty_text = "None"


#
# Device cooling components
#

class DeviceCoolingIntakeTable(CoolingIntakeTable):
    name = tables.TemplateColumn(
        verbose_name=_('Name'),
        template_code='<i class="mdi mdi-snowflake"></i> <a href="{{ record.get_absolute_url }}">{{ value }}</a>',
        attrs={'td': {'class': 'text-nowrap'}}
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.CoolingIntake
        fields = (
            'pk', 'id', 'name', 'module_bay', 'module', 'label', 'type', 'diameter', 'maximum_flow',
            'maximum_flow_unit', 'description', 'cooling_outflow', 'cooling_feed', 'tags', 'actions',
        )
        default_columns = (
            'pk', 'name', 'label', 'type', 'diameter', 'maximum_flow',
            'description',
        )


class DeviceCoolingOutflowTable(CoolingOutflowTable):
    name = tables.TemplateColumn(
        verbose_name=_('Name'),
        template_code='<i class="mdi mdi-snowflake"></i> <a href="{{ record.get_absolute_url }}">{{ value }}</a>',
        attrs={'td': {'class': 'text-nowrap'}}
    )

    class Meta(DeviceComponentTable.Meta):
        model = models.CoolingOutflow
        fields = (
            'pk', 'id', 'name', 'module_bay', 'module', 'label', 'type', 'diameter',
            'cooling_intake', 'description', 'tags', 'actions',
        )
        default_columns = (
            'pk', 'name', 'label', 'type', 'diameter', 'cooling_intake', 'description',
        )
