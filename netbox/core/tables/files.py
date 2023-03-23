import django_tables2 as tables

from core.models import *
from netbox.tables import NetBoxTable, columns

__all__ = (
    'ManagedFileTable',
)


class ManagedFileTable(NetBoxTable):
    file_path = tables.Column(
        linkify=True
    )
    last_updated = columns.DateTimeColumn()
    actions = columns.ActionsColumn(
        actions=('delete',)
    )

    class Meta(NetBoxTable.Meta):
        model = ManagedFile
        fields = (
            'pk', 'id', 'file_root', 'file_path', 'last_updated', 'size', 'hash',
        )
        default_columns = ('pk', 'file_root', 'file_path', 'last_updated')
