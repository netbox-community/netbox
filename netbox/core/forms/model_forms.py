import copy

from django import forms

from core.models import *
from netbox.forms import NetBoxModelForm
from netbox.registry import registry
from utilities.forms import CommentField, get_field_value

__all__ = (
    'DataSourceForm',
)


class DataSourceForm(NetBoxModelForm):
    comments = CommentField()

    class Meta:
        model = DataSource
        fields = [
            'name', 'type', 'source_url', 'enabled', 'description', 'comments', 'ignore_rules', 'tags',
        ]
        widgets = {
            'type': forms.Select(
                attrs={
                    'hx-get': '.',
                    'hx-include': '#form_fields input',
                    'hx-target': '#form_fields',
                }
            ),
            'ignore_rules': forms.Textarea(
                attrs={
                    'rows': 5,
                    'class': 'font-monospace',
                    'placeholder': '.cache\n*.txt'
                }
            ),
        }

    @property
    def fieldsets(self):
        fieldsets = [
            ('Source', ('name', 'type', 'source_url', 'enabled', 'description', 'tags', 'ignore_rules')),
        ]
        if self.backend_fields:
            fieldsets.append(
                ('Backend Parameters', self.backend_fields)
            )

        return fieldsets

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Determine the selected backend type
        backend_type = get_field_value(self, 'type')
        backend = registry['data_backends'].get(backend_type)

        # Add backend-specific form fields
        self.backend_fields = []
        for name, form_field in backend.parameters.items():
            field_name = f'backend_{name}'
            self.backend_fields.append(field_name)
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
