import django_tables2 as tables

from dcim.models import Module, ModuleType
from utilities.tables import BaseTable, LinkedCountColumn, MarkdownColumn, TagColumn, ToggleColumn

__all__ = (
    'ModuleTable',
    'ModuleTypeTable',
)


class ModuleTypeTable(BaseTable):
    pk = ToggleColumn()
    model = tables.Column(
        linkify=True,
        verbose_name='Module Type'
    )
    instance_count = LinkedCountColumn(
        viewname='dcim:module_list',
        url_params={'module_type_id': 'pk'},
        verbose_name='Instances'
    )
    comments = MarkdownColumn()
    tags = TagColumn(
        url_name='dcim:moduletype_list'
    )

    class Meta(BaseTable.Meta):
        model = ModuleType
        fields = (
            'pk', 'id', 'model', 'manufacturer', 'part_number', 'comments', 'tags',
        )
        default_columns = (
            'pk', 'model', 'manufacturer', 'part_number',
        )


class ModuleTable(BaseTable):
    pk = ToggleColumn()
    device = tables.Column(
        linkify=True
    )
    module_bay = tables.Column(
        linkify=True
    )
    module_type = tables.Column(
        linkify=True
    )
    comments = MarkdownColumn()
    tags = TagColumn(
        url_name='dcim:module_list'
    )

    class Meta(BaseTable.Meta):
        model = Module
        fields = (
            'pk', 'id', 'device', 'module_bay', 'module_type', 'serial', 'asset_tag', 'comments', 'tags',
        )
        default_columns = (
            'pk', 'id', 'device', 'module_bay', 'module_type', 'serial', 'asset_tag',
        )
