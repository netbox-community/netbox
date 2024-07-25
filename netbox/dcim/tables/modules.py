from django.utils.translation import gettext_lazy as _
import django_tables2 as tables

from dcim.models import Module, ModuleType
from netbox.tables import NetBoxTable, columns
from .template_code import WEIGHT

__all__ = (
    'ModuleTable',
    'ModuleTypeTable',
)


class ModuleTypeTable(NetBoxTable):
    model = tables.Column(
        linkify=True,
        verbose_name=_('Module Type')
    )
    manufacturer = tables.Column(
        verbose_name=_('Manufacturer'),
        linkify=True
    )
    instance_count = columns.LinkedCountColumn(
        viewname='dcim:module_list',
        url_params={'module_type_id': 'pk'},
        verbose_name=_('Instances')
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
    tags = columns.TagColumn(
        url_name='dcim:moduletype_list'
    )
    weight = columns.TemplateColumn(
        verbose_name=_('Weight'),
        template_code=WEIGHT,
        order_by=('_abs_weight', 'weight_unit')
    )

    class Meta(NetBoxTable.Meta):
        model = ModuleType
        fields = (
            'pk', 'id', 'model', 'manufacturer', 'part_number', 'airflow', 'weight', 'description', 'comments', 'tags',
        )
        default_columns = (
            'pk', 'model', 'manufacturer', 'part_number',
        )


class ModuleTable(NetBoxTable):
    device = tables.Column(
        verbose_name=_('Device'),
        linkify=True
    )
    module_bay = tables.Column(
        verbose_name=_('Module Bay'),
        linkify=True
    )
    manufacturer = tables.Column(
        verbose_name=_('Manufacturer'),
        accessor=tables.A('module_type__manufacturer'),
        linkify=True
    )
    module_type = tables.Column(
        verbose_name=_('Module Type'),
        linkify=True
    )
    status = columns.ChoiceFieldColumn(
        verbose_name=_('Status'),
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
    tags = columns.TagColumn(
        url_name='dcim:module_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Module
        fields = (
            'pk', 'id', 'device', 'module_bay', 'manufacturer', 'module_type', 'status', 'serial', 'asset_tag',
            'description', 'comments', 'tags',
        )
        default_columns = (
            'pk', 'id', 'device', 'module_bay', 'manufacturer', 'module_type', 'status', 'serial', 'asset_tag',
        )
