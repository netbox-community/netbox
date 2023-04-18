import json

from django import forms
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _

from core.forms.mixins import SyncedDataMixin
from dcim.models import DeviceRole, DeviceType, Location, Platform, Region, Site, SiteGroup
from extras.choices import *
from extras.models import *
from extras.utils import FeatureQuery
from netbox.forms import NetBoxModelForm
from tenancy.models import Tenant, TenantGroup
from utilities.forms import BootstrapMixin, add_blank_choice
from utilities.forms.fields import (
    CommentField, ContentTypeChoiceField, ContentTypeMultipleChoiceField, DynamicModelMultipleChoiceField, JSONField,
    SlugField,
)
from virtualization.models import Cluster, ClusterGroup, ClusterType

__all__ = (
    'ConfigContextForm',
    'ConfigTemplateForm',
    'CustomFieldForm',
    'CustomLinkForm',
    'ExportTemplateForm',
    'ImageAttachmentForm',
    'JournalEntryForm',
    'SavedFilterForm',
    'TagForm',
    'WebhookForm',
)


class CustomFieldForm(BootstrapMixin, forms.ModelForm):
    content_types = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_fields'),
    )
    object_type = ContentTypeChoiceField(
        queryset=ContentType.objects.all(),
        # TODO: Come up with a canonical way to register suitable models
        limit_choices_to=FeatureQuery('webhooks').get_query() | Q(app_label='auth', model__in=['user', 'group']),
        required=False,
        help_text=_("Type of the related object (for object/multi-object fields only)")
    )

    fieldsets = (
        ('Custom Field', (
            'content_types', 'name', 'label', 'group_name', 'type', 'object_type', 'required', 'description',
        )),
        ('Behavior', ('search_weight', 'filter_logic', 'ui_visibility', 'weight', 'is_cloneable')),
        ('Values', ('default', 'choices')),
        ('Validation', ('validation_minimum', 'validation_maximum', 'validation_regex')),
    )

    class Meta:
        model = CustomField
        fields = '__all__'
        help_texts = {
            'type': _(
                "The type of data stored in this field. For object/multi-object fields, select the related object "
                "type below."
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Disable changing the type of a CustomField as it almost universally causes errors if custom field data is already present.
        if self.instance.pk:
            self.fields['type'].disabled = True


class CustomLinkForm(BootstrapMixin, forms.ModelForm):
    content_types = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_links')
    )

    fieldsets = (
        ('Custom Link', ('name', 'content_types', 'weight', 'group_name', 'button_class', 'enabled', 'new_window')),
        ('Templates', ('link_text', 'link_url')),
    )

    class Meta:
        model = CustomLink
        fields = '__all__'
        widgets = {
            'link_text': forms.Textarea(attrs={'class': 'font-monospace'}),
            'link_url': forms.Textarea(attrs={'class': 'font-monospace'}),
        }
        help_texts = {
            'link_text': _(
                "Jinja2 template code for the link text. Reference the object as <code>{{ object }}</code>. Links "
                "which render as empty text will not be displayed."
            ),
            'link_url': _("Jinja2 template code for the link URL. Reference the object as <code>{{ object }}</code>."),
        }


class ExportTemplateForm(BootstrapMixin, SyncedDataMixin, forms.ModelForm):
    content_types = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('export_templates')
    )
    template_code = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'font-monospace'})
    )

    fieldsets = (
        ('Export Template', ('name', 'content_types', 'description', 'template_code')),
        ('Data Source', ('data_source', 'data_file', 'auto_sync_enabled')),
        ('Rendering', ('mime_type', 'file_extension', 'as_attachment')),
    )

    class Meta:
        model = ExportTemplate
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Disable data field when a DataFile has been set
        if self.instance.data_file:
            self.fields['template_code'].widget.attrs['readonly'] = True
            self.fields['template_code'].help_text = _(
                'Template content is populated from the remote source selected below.'
            )

    def clean(self):
        super().clean()

        if not self.cleaned_data.get('template_code') and not self.cleaned_data.get('data_file'):
            raise forms.ValidationError("Must specify either local content or a data file")

        return self.cleaned_data


class SavedFilterForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()
    content_types = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.all()
    )
    parameters = JSONField()

    fieldsets = (
        ('Saved Filter', ('name', 'slug', 'content_types', 'description', 'weight', 'enabled', 'shared')),
        ('Parameters', ('parameters',)),
    )

    class Meta:
        model = SavedFilter
        exclude = ('user',)

    def __init__(self, *args, initial=None, **kwargs):

        # Convert any parameters delivered via initial data to JSON data
        if initial and 'parameters' in initial:
            if type(initial['parameters']) is str:
                initial['parameters'] = json.loads(initial['parameters'])

        super().__init__(*args, initial=initial, **kwargs)


class WebhookForm(BootstrapMixin, forms.ModelForm):
    content_types = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('webhooks')
    )

    fieldsets = (
        ('Webhook', ('name', 'content_types', 'enabled')),
        ('Events', ('type_create', 'type_update', 'type_delete', 'type_job_start', 'type_job_end')),
        ('HTTP Request', (
            'payload_url', 'http_method', 'http_content_type', 'additional_headers', 'body_template', 'secret',
        )),
        ('Conditions', ('conditions',)),
        ('SSL', ('ssl_verification', 'ca_file_path')),
    )

    class Meta:
        model = Webhook
        fields = '__all__'
        labels = {
            'type_create': 'Creations',
            'type_update': 'Updates',
            'type_delete': 'Deletions',
            'type_job_start': 'Job executions',
            'type_job_end': 'Job terminations',
        }
        widgets = {
            'additional_headers': forms.Textarea(attrs={'class': 'font-monospace'}),
            'body_template': forms.Textarea(attrs={'class': 'font-monospace'}),
            'conditions': forms.Textarea(attrs={'class': 'font-monospace'}),
        }


class TagForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    fieldsets = (
        ('Tag', ('name', 'slug', 'color', 'description')),
    )

    class Meta:
        model = Tag
        fields = [
            'name', 'slug', 'color', 'description'
        ]


class ConfigContextForm(BootstrapMixin, SyncedDataMixin, forms.ModelForm):
    regions = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False
    )
    site_groups = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False
    )
    sites = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    locations = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False
    )
    device_types = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        required=False
    )
    roles = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False
    )
    platforms = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        required=False
    )
    cluster_types = DynamicModelMultipleChoiceField(
        queryset=ClusterType.objects.all(),
        required=False
    )
    cluster_groups = DynamicModelMultipleChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False
    )
    clusters = DynamicModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        required=False
    )
    tenant_groups = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False
    )
    tenants = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )
    data = JSONField(
        required=False
    )

    fieldsets = (
        ('Config Context', ('name', 'weight', 'description', 'data', 'is_active')),
        ('Data Source', ('data_source', 'data_file', 'auto_sync_enabled')),
        ('Assignment', (
            'regions', 'site_groups', 'sites', 'locations', 'device_types', 'roles', 'platforms', 'cluster_types',
            'cluster_groups', 'clusters', 'tenant_groups', 'tenants', 'tags',
        )),
    )

    class Meta:
        model = ConfigContext
        fields = (
            'name', 'weight', 'description', 'data', 'is_active', 'regions', 'site_groups', 'sites', 'locations',
            'roles', 'device_types', 'platforms', 'cluster_types', 'cluster_groups', 'clusters', 'tenant_groups',
            'tenants', 'tags', 'data_source', 'data_file', 'auto_sync_enabled',
        )

    def __init__(self, *args, initial=None, **kwargs):

        # Convert data delivered via initial data to JSON data
        if initial and 'data' in initial:
            if type(initial['data']) is str:
                initial['data'] = json.loads(initial['data'])

        super().__init__(*args, initial=initial, **kwargs)

        # Disable data field when a DataFile has been set
        if self.instance.data_file:
            self.fields['data'].widget.attrs['readonly'] = True
            self.fields['data'].help_text = _('Data is populated from the remote source selected below.')

    def clean(self):
        super().clean()

        if not self.cleaned_data.get('data') and not self.cleaned_data.get('data_file'):
            raise forms.ValidationError("Must specify either local data or a data file")

        return self.cleaned_data


class ConfigTemplateForm(BootstrapMixin, SyncedDataMixin, forms.ModelForm):
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )
    template_code = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'font-monospace'})
    )

    fieldsets = (
        ('Config Template', ('name', 'description', 'environment_params', 'tags')),
        ('Content', ('template_code',)),
        ('Data Source', ('data_source', 'data_file', 'auto_sync_enabled')),
    )

    class Meta:
        model = ConfigTemplate
        fields = '__all__'
        widgets = {
            'environment_params': forms.Textarea(attrs={'rows': 5})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Disable content field when a DataFile has been set
        if self.instance.data_file:
            self.fields['template_code'].widget.attrs['readonly'] = True
            self.fields['template_code'].help_text = _(
                'Template content is populated from the remote source selected below.'
            )

    def clean(self):
        super().clean()

        if not self.cleaned_data.get('template_code') and not self.cleaned_data.get('data_file'):
            raise forms.ValidationError("Must specify either local content or a data file")

        return self.cleaned_data


class ImageAttachmentForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = ImageAttachment
        fields = [
            'name', 'image',
        ]


class JournalEntryForm(NetBoxModelForm):
    kind = forms.ChoiceField(
        choices=add_blank_choice(JournalEntryKindChoices),
        required=False
    )
    comments = CommentField()

    class Meta:
        model = JournalEntry
        fields = ['assigned_object_type', 'assigned_object_id', 'kind', 'tags', 'comments']
        widgets = {
            'assigned_object_type': forms.HiddenInput,
            'assigned_object_id': forms.HiddenInput,
        }
