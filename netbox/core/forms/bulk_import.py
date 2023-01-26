from core.models import *
from netbox.forms import NetBoxModelImportForm

__all__ = (
    'DataSourceImportForm',
)


class DataSourceImportForm(NetBoxModelImportForm):

    class Meta:
        model = DataSource
        fields = (
            'name', 'type', 'url', 'enabled', 'description', 'git_branch', 'ignore_rules', 'username', 'password',
        )
