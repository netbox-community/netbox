from core.models import *
from netbox.forms import NetBoxModelImportForm

__all__ = (
    'DataSourceImportForm',
)


class DataSourceImportForm(NetBoxModelImportForm):

    class Meta:
        model = DataSource
        fields = (
            'name', 'type', 'source_url', 'enabled', 'description', 'sync_interval', 'parameters', 'ignore_rules',
            'comments',
        )
