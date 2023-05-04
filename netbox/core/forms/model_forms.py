import copy

from django import forms

from core.forms.mixins import SyncedDataMixin
from core.models import *
from netbox.forms import NetBoxModelForm
from netbox.registry import registry
from utilities.forms import get_field_value
from utilities.forms.fields import CommentField
from utilities.forms.widgets import HTMXSelect

__all__ = (
    'DataSourceForm',
    'ManagedFileForm',
)


class DataSourceForm(NetBoxModelForm):
    comments = CommentField()

    class Meta:
        model = DataSource
        fields = [
            'name', 'type', 'source_url', 'enabled', 'description', 'comments', 'ignore_rules', 'tags',
        ]
        widgets = {
            'type': HTMXSelect(),
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


class ManagedFileForm(SyncedDataMixin, NetBoxModelForm):
    upload_file = forms.FileField(
        required=False
    )

    fieldsets = (
        ('File Upload', ('upload_file',)),
        ('Data Source', ('data_source', 'data_file', 'auto_sync_enabled')),
    )

    class Meta:
        model = ManagedFile
        fields = ('data_source', 'data_file', 'auto_sync_enabled')

    def clean(self):
        super().clean()

        if self.cleaned_data.get('upload_file') and self.cleaned_data.get('data_file'):
            raise forms.ValidationError("Cannot upload a file and sync from an existing file")
        if not self.cleaned_data.get('upload_file') and not self.cleaned_data.get('data_file'):
            raise forms.ValidationError("Must upload a file or select a data file to sync")

        return self.cleaned_data

    def save(self, *args, **kwargs):
        # If a file was uploaded, save it to disk
        if self.cleaned_data['upload_file']:
            self.instance.file_path = self.cleaned_data['upload_file'].name
            with open(self.instance.full_path, 'wb+') as new_file:
                new_file.write(self.cleaned_data['upload_file'].read())

        return super().save(*args, **kwargs)
