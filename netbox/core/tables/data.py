import django_tables2 as tables

from core.models import *
from netbox.tables import NetBoxTable, columns

__all__ = (
    'DataFileTable',
    'DataSourceTable',
)


class DataSourceTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    type = columns.ChoiceFieldColumn()
    status = columns.ChoiceFieldColumn()
    enabled = columns.BooleanColumn()
    tags = columns.TagColumn(
        url_name='core:datasource_list'
    )
    file_count = tables.Column(
        verbose_name='Files'
    )

    class Meta(NetBoxTable.Meta):
        model = DataSource
        fields = (
            'pk', 'id', 'name', 'type', 'status', 'enabled', 'source_url', 'description', 'comments', 'parameters', 'created',
            'last_updated', 'file_count',
        )
        default_columns = ('pk', 'name', 'type', 'status', 'enabled', 'description', 'file_count')


class DataFileTable(NetBoxTable):
    source = tables.Column(
        linkify=True
    )
    path = tables.Column(
        linkify=True
    )
    last_updated = columns.DateTimeColumn()
    actions = columns.ActionsColumn(
        actions=('delete',)
    )

    class Meta(NetBoxTable.Meta):
        model = DataFile
        fields = (
            'pk', 'id', 'source', 'path', 'last_updated', 'size', 'hash',
        )
        default_columns = ('pk', 'source', 'path', 'size', 'last_updated')
