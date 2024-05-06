import copy
import json

from django import forms
from django.conf import settings
from django.forms.fields import JSONField as _JSONField
from django.utils.translation import gettext_lazy as _

from core.forms.mixins import SyncedDataMixin
from core.models import *
from netbox.config import get_config, PARAMS
from netbox.forms import NetBoxModelForm
from netbox.registry import registry
from netbox.utils import get_data_backend_choices
from utilities.forms import get_field_value
from utilities.forms.fields import CommentField, JSONField
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import HTMXSelect

__all__ = (
    'ConfigRevisionForm',
    'DataSourceForm',
    'ManagedFileForm',
)

EMPTY_VALUES = ('', None, [], ())


class DataSourceForm(NetBoxModelForm):
    type = forms.ChoiceField(
        choices=get_data_backend_choices,
        widget=HTMXSelect()
    )
    comments = CommentField()

    class Meta:
        model = DataSource
        fields = [
            'name', 'type', 'source_url', 'enabled', 'description', 'comments', 'ignore_rules', 'tags',
        ]
        widgets = {
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
            FieldSet('name', 'type', 'source_url', 'enabled', 'description', 'tags', 'ignore_rules', name=_('Source')),
        ]
        if self.backend_fields:
            fieldsets.append(
                FieldSet(*self.backend_fields, name=_('Backend Parameters'))
            )

        return fieldsets

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Determine the selected backend type
        backend_type = get_field_value(self, 'type')
        backend = registry['data_backends'].get(backend_type)

        # Add backend-specific form fields
        self.backend_fields = []
        if backend:
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
        FieldSet('upload_file', name=_('File Upload')),
        FieldSet('data_source', 'data_file', 'auto_sync_enabled', name=_('Data Source')),
    )

    class Meta:
        model = ManagedFile
        fields = ('data_source', 'data_file', 'auto_sync_enabled')

    def clean(self):
        super().clean()

        if self.cleaned_data.get('upload_file') and self.cleaned_data.get('data_file'):
            raise forms.ValidationError(_("Cannot upload a file and sync from an existing file"))
        if not self.cleaned_data.get('upload_file') and not self.cleaned_data.get('data_file'):
            raise forms.ValidationError(_("Must upload a file or select a data file to sync"))

        return self.cleaned_data

    def save(self, *args, **kwargs):
        # If a file was uploaded, save it to disk
        if self.cleaned_data['upload_file']:
            self.instance.file_path = self.cleaned_data['upload_file'].name
            with open(self.instance.full_path, 'wb+') as new_file:
                new_file.write(self.cleaned_data['upload_file'].read())

        return super().save(*args, **kwargs)


class ConfigFormMetaclass(forms.models.ModelFormMetaclass):

    def __new__(mcs, name, bases, attrs):

        # Emulate a declared field for each supported configuration parameter
        param_fields = {}
        for param in PARAMS:
            field_kwargs = {
                'required': False,
                'label': param.label,
                'help_text': param.description,
            }
            field_kwargs.update(**param.field_kwargs)
            if param.field is _JSONField:
                # Replace with our own JSONField to get pretty JSON in config editor
                param.field = JSONField
            param_fields[param.name] = param.field(**field_kwargs)
        attrs.update(param_fields)

        return super().__new__(mcs, name, bases, attrs)


class ConfigRevisionForm(forms.ModelForm, metaclass=ConfigFormMetaclass):
    """
    Form for creating a new ConfigRevision.
    """

    fieldsets = (
        FieldSet(
            'RACK_ELEVATION_DEFAULT_UNIT_HEIGHT', 'RACK_ELEVATION_DEFAULT_UNIT_WIDTH', name=_('Rack Elevations')
        ),
        FieldSet(
            'POWERFEED_DEFAULT_VOLTAGE', 'POWERFEED_DEFAULT_AMPERAGE', 'POWERFEED_DEFAULT_MAX_UTILIZATION',
            name=_('Power')
        ),
        FieldSet('ENFORCE_GLOBAL_UNIQUE', 'PREFER_IPV4', name=_('IPAM')),
        FieldSet('ALLOWED_URL_SCHEMES', name=_('Security')),
        FieldSet('BANNER_LOGIN', 'BANNER_MAINTENANCE', 'BANNER_TOP', 'BANNER_BOTTOM', name=_('Banners')),
        FieldSet('PAGINATE_COUNT', 'MAX_PAGE_SIZE', name=_('Pagination')),
        FieldSet('CUSTOM_VALIDATORS', 'PROTECTION_RULES', name=_('Validation')),
        FieldSet('DEFAULT_USER_PREFERENCES', name=_('User Preferences')),
        FieldSet(
            'MAINTENANCE_MODE', 'GRAPHQL_ENABLED', 'CHANGELOG_RETENTION', 'JOB_RETENTION', 'MAPS_URL',
            name=_('Miscellaneous')
        ),
        FieldSet('comment', name=_('Config Revision'))
    )

    class Meta:
        model = ConfigRevision
        fields = '__all__'
        widgets = {
            'BANNER_LOGIN': forms.Textarea(attrs={'class': 'font-monospace'}),
            'BANNER_MAINTENANCE': forms.Textarea(attrs={'class': 'font-monospace'}),
            'BANNER_TOP': forms.Textarea(attrs={'class': 'font-monospace'}),
            'BANNER_BOTTOM': forms.Textarea(attrs={'class': 'font-monospace'}),
            'CUSTOM_VALIDATORS': forms.Textarea(attrs={'class': 'font-monospace'}),
            'PROTECTION_RULES': forms.Textarea(attrs={'class': 'font-monospace'}),
            'comment': forms.Textarea(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Append current parameter values to form field help texts and check for static configurations
        config = get_config()
        for param in PARAMS:
            value = getattr(config, param.name)

            # Set the field's initial value, if it can be serialized. (This may not be the case e.g. for
            # CUSTOM_VALIDATORS, which may reference Python objects.)
            try:
                json.dumps(value)
                if type(value) in (tuple, list):
                    self.fields[param.name].initial = ', '.join(value)
                else:
                    self.fields[param.name].initial = value
            except TypeError:
                pass

            # Check whether this parameter is statically configured (e.g. in configuration.py)
            if hasattr(settings, param.name):
                self.fields[param.name].disabled = True
                self.fields[param.name].help_text = _(
                    'This parameter has been defined statically and cannot be modified.'
                )
                continue

            # Set the field's help text
            help_text = self.fields[param.name].help_text
            if help_text:
                help_text += '<br />'  # Line break
            help_text += _('Current value: <strong>{value}</strong>').format(value=value or '&mdash;')
            if value == param.default:
                help_text += _(' (default)')
            self.fields[param.name].help_text = help_text

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Populate JSON data on the instance
        instance.data = self.render_json()

        if commit:
            instance.save()

        return instance

    def render_json(self):
        json = {}

        # Iterate through each field and populate non-empty values
        for field_name in self.declared_fields:
            if field_name in self.cleaned_data and self.cleaned_data[field_name] not in EMPTY_VALUES:
                json[field_name] = self.cleaned_data[field_name]

        return json
