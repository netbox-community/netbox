from netbox.forms import PrimaryModelImportForm

from ..models import *

__all__ = (
    'DataSourceImportForm',
)


class DataSourceImportForm(PrimaryModelImportForm):

    class Meta:
        model = DataSource
        fields = (
            'name', 'type', 'source_url', 'enabled', 'description', 'sync_interval', 'parameters', 'ignore_rules',
            'owner', 'comments',
        )
