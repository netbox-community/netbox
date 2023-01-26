from core.models import *
from netbox.forms import NetBoxModelForm, StaticSelect

__all__ = (
    'DataSourceForm',
)


class DataSourceForm(NetBoxModelForm):
    fieldsets = (
        ('Source', ('name', 'type', 'url', 'enabled', 'description')),
        ('Git', ('git_branch',)),
        ('Authentication', ('username', 'password')),
    )

    class Meta:
        model = DataSource
        fields = [
            'name', 'type', 'url', 'enabled', 'description', 'git_branch', 'ignore_rules', 'username', 'password',
        ]
        widgets = {
            'type': StaticSelect(),
        }
