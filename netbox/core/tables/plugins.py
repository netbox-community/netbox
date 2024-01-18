import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from netbox.tables import BaseTable

__all__ = (
    'PluginTable',
)


class PluginTable(BaseTable):
    verbose_name = tables.Column()
    name = tables.Column()
    author = tables.Column()
    author_email = tables.Column()
    description = tables.Column()
    version = tables.Column()

    class Meta:
        empty_text = _('No plugins found')
        fields = (
            'verbose_name', 'name', 'author', 'author_email', 'description', 'version',
        )
        default_columns = (
            'verbose_name', 'name', 'author', 'author_email', 'description', 'version',
        )
        attrs = {
            'class': 'table table-hover object-list',
        }
