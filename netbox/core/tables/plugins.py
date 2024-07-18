from datetime import datetime
import django_tables2 as tables
from django.contrib.humanize.templatetags.humanize import naturalday
from django.utils.translation import gettext_lazy as _
from netbox.tables import BaseTable

__all__ = (
    'CatalogPluginTable',
    'PluginVersionTable',
)


class PluginVersionTable(BaseTable):
    version = tables.Column(
        verbose_name=_('Version')
    )
    last_updated = tables.Column(
        accessor=tables.A('date'),
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

    def render_last_updated(self, value, record):
        return naturalday(value)


class CatalogPluginTable(BaseTable):
    title_short = tables.Column(
        linkify=('core:plugin', [tables.A('slug')]),
        verbose_name=_('Name')
    )
    author = tables.Column(
        accessor=tables.A('author.name'),
        verbose_name=_('Author')
    )
    is_local = tables.BooleanColumn(
        verbose_name=_('Local')
    )
    is_installed = tables.BooleanColumn(
        verbose_name=_('Installed')
    )
    is_certified = tables.BooleanColumn(
        verbose_name=_('Certified')
    )
    created_at = tables.Column(
        verbose_name=_('Published')
    )
    updated_at = tables.Column(
        verbose_name=_('Updated')
    )

    class Meta(BaseTable.Meta):
        empty_text = _('No plugin data found')
        fields = (
            'title_short', 'author', 'is_local', 'is_installed', 'is_certified', 'created_at', 'updated_at',
        )
        default_columns = (
            'title_short', 'author', 'is_local', 'is_installed', 'is_certified', 'created_at', 'updated_at',
        )
