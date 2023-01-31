import copy

from core.models import *
from netbox.forms import NetBoxModelForm, StaticSelect
from ..models.data import BACKEND_CLASSES

__all__ = (
    'DataSourceForm',
)


class DataSourceForm(NetBoxModelForm):
    # fieldsets = (
    #     ('Source', ('name', 'type', 'url', 'enabled', 'description')),
    #     ('Backend', ('parameters', 'ignore_rules')),
    # )

    class Meta:
        model = DataSource
        fields = [
            'name', 'type', 'url', 'enabled', 'description', 'ignore_rules',
        ]
        widgets = {
            'type': StaticSelect(
                attrs={
                    'hx-get': '.',
                    'hx-include': '#form_fields input',
                    'hx-target': '#form_fields',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.is_bound and self.data.get('type') in BACKEND_CLASSES:
            backend_type = self.data['type']
        elif self.initial and self.initial.get('type') in BACKEND_CLASSES:
            backend_type = self.initial['type']
        else:
            backend_type = self.fields['type'].initial
        backend = BACKEND_CLASSES.get(backend_type)
        for name, form_field in backend.parameters.items():
            field_name = f'backend_{name}'
            self.fields[field_name] = copy.copy(form_field)
            if self.instance and self.instance.parameters:
                self.fields[field_name].initial = self.instance.parameters.get(name)

    def save(self, *args, **kwargs):

        parameters = {}
        for name in self.fields:
            if name.startswith('backend_'):
                parameters[name[8:]] = self.cleaned_data[name]
        self.instance.parameters = parameters

        return super().save(*args, **kwargs)
