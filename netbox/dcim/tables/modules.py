from django.utils.translation import gettext_lazy as _
import django_tables2 as tables

from dcim.models import Module, ModuleType, ModuleTypeProfile
from netbox.tables import NetBoxTable, columns
from .template_code import MODULETYPEPROFILE_ATTRIBUTES, WEIGHT

__all__ = (
    'ModuleTable',
    'ModuleTypeProfileTable',
    'ModuleTypeTable',
)


class ModuleTypeProfileTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    attributes = columns.TemplateColumn(
        template_code=MODULETYPEPROFILE_ATTRIBUTES,
        accessor=tables.A('schema__properties'),
        orderable=False,
        verbose_name=_('Attributes')
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
    tags = columns.TagColumn(
        url_name='dcim:moduletypeprofile_list'
    )

    class Meta(NetBoxTable.Meta):
        model = ModuleTypeProfile
        fields = (
            'pk', 'id', 'name', 'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'description', 'attributes',
        )


class ModuleTypeTable(NetBoxTable):
    profile = tables.Column(
        verbose_name=_('Profile'),
        linkify=True
    )
    manufacturer = tables.Column(
        verbose_name=_('Manufacturer'),
        linkify=True
    )
    model = tables.Column(
        linkify=True,
        verbose_name=_('Module Type')
    )
    weight = columns.TemplateColumn(
        verbose_name=_('Weight'),
        template_code=WEIGHT,
        order_by=('_abs_weight', 'weight_unit')
    )
    attributes = columns.DictColumn()
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

    class Meta(NetBoxTable.Meta):
        model = ModuleType
        fields = (
            'pk', 'id', 'model', 'profile', 'manufacturer', 'part_number', 'airflow', 'weight', 'description',
            'attributes', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'model', 'profile', 'manufacturer', 'part_number',
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
            'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'id', 'device', 'module_bay', 'manufacturer', 'module_type', 'status', 'serial', 'asset_tag',
        )
