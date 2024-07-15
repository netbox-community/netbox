from datetime import datetime
import django_tables2 as tables
from django.contrib.humanize.templatetags.humanize import naturalday
from django.utils.translation import gettext_lazy as _
from netbox.tables import BaseTable

__all__ = (
    'CertifiedPluginTable',
    'InstalledPluginTable',
    'PluginVersionTable',
)


class InstalledPluginTable(BaseTable):
    name = tables.Column(
        accessor=tables.A('verbose_name'),
        verbose_name=_('Name')
    )
    version = tables.Column(
        verbose_name=_('Version')
    )
    package = tables.Column(
        accessor=tables.A('name'),
        verbose_name=_('Package')
    )
    author = tables.Column(
        verbose_name=_('Author')
    )
    author_email = tables.Column(
        verbose_name=_('Author Email')
    )
    description = tables.Column(
        verbose_name=_('Description')
    )

    class Meta(BaseTable.Meta):
        empty_text = _('No plugins found')
        fields = (
            'name', 'version', 'package', 'author', 'author_email', 'description',
        )
        default_columns = (
            'name', 'version', 'package', 'description',
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
        return naturalday(datetime.fromisoformat(value))


class CertifiedPluginTable(BaseTable):
    name = tables.Column(
        linkify=('core:plugin', [tables.A('slug')]),
        verbose_name=_('Name')
    )
    author = tables.Column(
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
    created = tables.Column(
        verbose_name=_('Published')
    )
    updated = tables.Column(
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
