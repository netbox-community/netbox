import django_tables2 as tables

from dcim.models import ModuleType
from utilities.tables import BaseTable, MarkdownColumn, TagColumn, ToggleColumn

__all__ = (
    'ModuleTypeTable',
)


class ModuleTypeTable(BaseTable):
    pk = ToggleColumn()
    model = tables.Column(
        linkify=True,
        verbose_name='Device Type'
    )
    # instance_count = LinkedCountColumn(
    #     viewname='dcim:module_list',
    #     url_params={'module_type_id': 'pk'},
    #     verbose_name='Instances'
    # )
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
