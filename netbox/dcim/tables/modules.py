import django_tables2 as tables

from dcim.models import Module, ModuleType
from netbox.tables import NetBoxTable, columns

__all__ = (
    'ModuleTable',
    'ModuleTypeTable',
)


class ModuleTypeTable(NetBoxTable):
    model = tables.Column(
        linkify=True,
        verbose_name='Module Type'
    )
    instance_count = columns.LinkedCountColumn(
        viewname='dcim:module_list',
        url_params={'module_type_id': 'pk'},
        verbose_name='Instances'
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='dcim:moduletype_list'
    )

    class Meta(NetBoxTable.Meta):
        model = ModuleType
        fields = (
            'pk', 'id', 'model', 'manufacturer', 'part_number', 'comments', 'tags',
        )
        default_columns = (
            'pk', 'model', 'manufacturer', 'part_number',
        )


class ModuleTable(NetBoxTable):
    device = tables.Column(
        linkify=True
    )
    module_bay = tables.Column(
        linkify=True
    )
    module_type = tables.Column(
        linkify=True
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='dcim:module_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Module
        fields = (
            'pk', 'id', 'device', 'module_bay', 'module_type', 'serial', 'asset_tag', 'comments', 'tags',
        )
        default_columns = (
            'pk', 'id', 'device', 'module_bay', 'module_type', 'serial', 'asset_tag',
        )
