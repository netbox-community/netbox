import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import BaseTable, columns

__all__ = (
    'CatalogPluginTable',
    'PluginVersionTable',
)


class PluginVersionTable(BaseTable):
    version = tables.Column(
        verbose_name=_('Version')
    )
    last_updated = columns.DateTimeColumn(
        accessor=tables.A('date'),
        timespec='minutes',
        verbose_name=_('Last Updated')
    )
    min_version = tables.Column(
        accessor=tables.A('netbox_min_version'),
        verbose_name=_('Minimum NetBox Version')
    )
    max_version = tables.Column(
        accessor=tables.A('netbox_max_version'),
        verbose_name=_('Maximum NetBox Version')
    )

    class Meta(BaseTable.Meta):
        empty_text = _('No plugin data found')
        fields = (
            'version', 'last_updated', 'min_version', 'max_version',
        )
        default_columns = (
            'version', 'last_updated', 'min_version', 'max_version',
        )
        orderable = False


class CatalogPluginTable(BaseTable):
    name = tables.Column(
        linkify=('core:plugin', [tables.A('slug')]),
        verbose_name=_('Name')
    )
    author = tables.Column(
        verbose_name=_('Author')
    )
    is_local = columns.BooleanColumn(
        verbose_name=_('Local')
    )
    is_installed = columns.BooleanColumn(
        verbose_name=_('Installed')
    )
    is_certified = columns.BooleanColumn(
        verbose_name=_('Certified')
    )
    created = columns.DateTimeColumn(
        verbose_name=_('Published')
    )
    updated = columns.DateTimeColumn(
        verbose_name=_('Updated')
    )

    class Meta(BaseTable.Meta):
        empty_text = _('No plugin data found')
        fields = (
            'name', 'author', 'is_local', 'is_installed', 'is_certified', 'created', 'updated',
        )
        default_columns = (
            'name', 'author', 'is_local', 'is_installed', 'is_certified', 'created', 'updated',
        )
