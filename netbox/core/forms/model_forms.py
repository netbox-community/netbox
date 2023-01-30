from core.models import *
from netbox.forms import NetBoxModelForm, StaticSelect

__all__ = (
    'DataSourceForm',
)


class DataSourceForm(NetBoxModelForm):
    fieldsets = (
        ('Source', ('name', 'type', 'url', 'enabled', 'description')),
        ('Backend', ('parameters', 'ignore_rules')),
    )

    class Meta:
        model = DataSource
        fields = [
            'name', 'type', 'url', 'enabled', 'description', 'parameters', 'ignore_rules',
        ]
        widgets = {
            'type': StaticSelect(),
        }
