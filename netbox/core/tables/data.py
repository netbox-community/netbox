from django.utils.translation import gettext_lazy as _
import django_tables2 as tables

from core.models import *
from netbox.tables import NetBoxTable, columns
from .columns import BackendTypeColumn
from .template_code import DATA_SOURCE_SYNC_BUTTON

__all__ = (
    'DataFileTable',
    'DataSourceTable',
)


class DataSourceTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True,
    )
    type = BackendTypeColumn(
        verbose_name=_('Type'),
    )
    status = columns.ChoiceFieldColumn(
        verbose_name=_('Status'),
    )
    enabled = columns.BooleanColumn(
        verbose_name=_('Enabled'),
    )
    sync_interval = columns.ChoiceFieldColumn(
        verbose_name=_('Sync interval'),
    )
    last_synced = tables.DateTimeColumn(
        verbose_name=_('Last Synced'),
    )
    file_count = tables.Column(
        verbose_name=_('Files'),
    )
    tags = columns.TagColumn(
        url_name='core:datasource_list',
    )
    actions = columns.ActionsColumn(
        extra_buttons=DATA_SOURCE_SYNC_BUTTON,
    )

    class Meta(NetBoxTable.Meta):
        model = DataSource
        fields = (
            'pk', 'id', 'name', 'type', 'status', 'enabled', 'source_url', 'description', 'sync_interval', 'comments',
            'parameters', 'last_synced', 'created', 'last_updated', 'file_count',
        )
        default_columns = ('pk', 'name', 'type', 'status', 'enabled', 'description', 'sync_interval', 'file_count')


class DataFileTable(NetBoxTable):
    source = tables.Column(
        verbose_name=_('Source'),
        linkify=True
    )
    path = tables.Column(
        verbose_name=_('Path'),
        linkify=True
    )
    last_updated = columns.DateTimeColumn(
        verbose_name=_('Last updated'),
    )
    actions = columns.ActionsColumn(
        actions=('delete',)
    )

    class Meta(NetBoxTable.Meta):
        model = DataFile
        fields = (
            'pk', 'id', 'source', 'path', 'last_updated', 'size', 'hash',
        )
        default_columns = ('pk', 'source', 'path', 'size', 'last_updated')
