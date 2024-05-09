import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from netbox.tables import BaseTable

__all__ = (
    'PluginTable',
)


class PluginTable(BaseTable):
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
