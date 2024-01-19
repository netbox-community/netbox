import json
import re

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from core.forms.mixins import SyncedDataMixin
from core.models import ContentType
from dcim.models import DeviceRole, DeviceType, Location, Platform, Region, Site, SiteGroup
from extras.choices import *
from extras.models import *
from netbox.forms import NetBoxModelForm
from tenancy.models import Tenant, TenantGroup
from utilities.forms import add_blank_choice, get_field_value
from utilities.forms.fields import (
    CommentField, ContentTypeChoiceField, ContentTypeMultipleChoiceField, DynamicModelChoiceField,
    DynamicModelMultipleChoiceField, JSONField, SlugField,
)
from utilities.forms.widgets import ChoicesWidget, HTMXSelect
from virtualization.models import Cluster, ClusterGroup, ClusterType

__all__ = (
    'BookmarkForm',
    'ConfigContextForm',
    'ConfigTemplateForm',
    'CustomFieldChoiceSetForm',
    'CustomFieldForm',
    'CustomLinkForm',
    'EventRuleForm',
    'ExportTemplateForm',
    'ImageAttachmentForm',
    'JournalEntryForm',
    'SavedFilterForm',
    'TagForm',
    'WebhookForm',
)


class CustomFieldForm(forms.ModelForm):
    content_types = ContentTypeMultipleChoiceField(
        label=_('Content types'),
        queryset=ContentType.objects.with_feature('custom_fields')
    )
    object_type = ContentTypeChoiceField(
        label=_('Object type'),
        queryset=ContentType.objects.public(),
        required=False,
        help_text=_("Type of the related object (for object/multi-object fields only)")
    )
    choice_set = DynamicModelChoiceField(
        queryset=CustomFieldChoiceSet.objects.all(),
        required=False
    )

    fieldsets = (
        (_('Custom Field'), (
            'content_types', 'name', 'label', 'group_name', 'type', 'object_type', 'required', 'description',
        )),
        (_('Behavior'), ('search_weight', 'filter_logic', 'ui_visible', 'ui_editable', 'weight', 'is_cloneable')),
        (_('Values'), ('default', 'choice_set')),
        (_('Validation'), ('validation_minimum', 'validation_maximum', 'validation_regex')),
    )

    class Meta:
        model = CustomField
        fields = '__all__'
        help_texts = {
            'type': _(
                "The type of data stored in this field. For object/multi-object fields, select the related object "
                "type below."
            ),
            'description': _("This will be displayed as help text for the form field. Markdown is supported.")
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Disable changing the type of a CustomField as it almost universally causes errors if custom field data
        # is already present.
        if self.instance.pk:
            self.fields['type'].disabled = True


class CustomFieldChoiceSetForm(forms.ModelForm):
    extra_choices = forms.CharField(
        widget=ChoicesWidget(),
        required=False,
        help_text=mark_safe(_(
            'Enter one choice per line. An optional label may be specified for each choice by appending it with a '
            'colon. Example:'
        ) + ' <code>choice1:First Choice</code>')
    )

    class Meta:
        model = CustomFieldChoiceSet
        fields = ('name', 'description', 'base_choices', 'extra_choices', 'order_alphabetically')

    def __init__(self, *args, initial=None, **kwargs):
        super().__init__(*args, initial=initial, **kwargs)

        # Escape colons in extra_choices
        if 'extra_choices' in self.initial and self.initial['extra_choices']:
            choices = []
            for choice in self.initial['extra_choices']:
                choice = (choice[0].replace(':', '\\:'), choice[1].replace(':', '\\:'))
                choices.append(choice)

            self.initial['extra_choices'] = choices

    def clean_extra_choices(self):
        data = []
        for line in self.cleaned_data['extra_choices'].splitlines():
            try:
                value, label = re.split(r'(?<!\\):', line, maxsplit=1)
                value = value.replace('\\:', ':')
                label = label.replace('\\:', ':')
            except ValueError:
                value, label = line, line
            data.append((value, label))
        return data


class CustomLinkForm(forms.ModelForm):
    content_types = ContentTypeMultipleChoiceField(
        label=_('Content types'),
        queryset=ContentType.objects.with_feature('custom_links')
    )

    fieldsets = (
        (_('Custom Link'), ('name', 'content_types', 'weight', 'group_name', 'button_class', 'enabled', 'new_window')),
        (_('Templates'), ('link_text', 'link_url')),
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


class ExportTemplateForm(SyncedDataMixin, forms.ModelForm):
    content_types = ContentTypeMultipleChoiceField(
        label=_('Content types'),
        queryset=ContentType.objects.with_feature('export_templates')
    )
    template_code = forms.CharField(
        label=_('Template code'),
        required=False,
        widget=forms.Textarea(attrs={'class': 'font-monospace'})
    )

    fieldsets = (
        (_('Export Template'), ('name', 'content_types', 'description', 'template_code')),
        (_('Data Source'), ('data_source', 'data_file', 'auto_sync_enabled')),
        (_('Rendering'), ('mime_type', 'file_extension', 'as_attachment')),
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
            raise forms.ValidationError(_("Must specify either local content or a data file"))

        return self.cleaned_data


class SavedFilterForm(forms.ModelForm):
    slug = SlugField()
    content_types = ContentTypeMultipleChoiceField(
        label=_('Content types'),
        queryset=ContentType.objects.all()
    )
    parameters = JSONField()

    fieldsets = (
        (_('Saved Filter'), ('name', 'slug', 'content_types', 'description', 'weight', 'enabled', 'shared')),
        (_('Parameters'), ('parameters',)),
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


class BookmarkForm(forms.ModelForm):
    object_type = ContentTypeChoiceField(
        label=_('Object type'),
        queryset=ContentType.objects.with_feature('bookmarks')
    )

    class Meta:
        model = Bookmark
        fields = ('object_type', 'object_id')


class WebhookForm(NetBoxModelForm):

    fieldsets = (
        (_('Webhook'), ('name', 'description', 'tags',)),
        (_('HTTP Request'), (
            'payload_url', 'http_method', 'http_content_type', 'additional_headers', 'body_template', 'secret',
        )),
        (_('SSL'), ('ssl_verification', 'ca_file_path')),
    )

    class Meta:
        model = Webhook
        fields = '__all__'
        widgets = {
            'additional_headers': forms.Textarea(attrs={'class': 'font-monospace'}),
            'body_template': forms.Textarea(attrs={'class': 'font-monospace'}),
        }


class EventRuleForm(NetBoxModelForm):
    content_types = ContentTypeMultipleChoiceField(
        label=_('Content types'),
        queryset=ContentType.objects.with_feature('event_rules'),
    )
    action_choice = forms.ChoiceField(
        label=_('Action choice'),
        choices=[]
    )
    conditions = JSONField(
        required=False,
        help_text=_('Enter conditions in <a href="https://json.org/">JSON</a> format.')
    )
    action_data = JSONField(
        required=False,
        help_text=_('Enter parameters to pass to the action in <a href="https://json.org/">JSON</a> format.')
    )

    fieldsets = (
        (_('Event Rule'), ('name', 'description', 'content_types', 'enabled', 'tags')),
        (_('Events'), ('type_create', 'type_update', 'type_delete', 'type_job_start', 'type_job_end')),
        (_('Conditions'), ('conditions',)),
        (_('Action'), (
            'action_type', 'action_choice', 'action_object_type', 'action_object_id', 'action_data',
        )),
    )

    class Meta:
        model = EventRule
        fields = (
            'content_types', 'name', 'description', 'type_create', 'type_update', 'type_delete', 'type_job_start',
            'type_job_end', 'enabled', 'conditions', 'action_type', 'action_object_type', 'action_object_id',
            'action_data', 'comments', 'tags'
        )
        labels = {
            'type_create': _('Creations'),
            'type_update': _('Updates'),
            'type_delete': _('Deletions'),
            'type_job_start': _('Job executions'),
            'type_job_end': _('Job terminations'),
        }
        widgets = {
            'conditions': forms.Textarea(attrs={'class': 'font-monospace'}),
            'action_type': HTMXSelect(),
            'action_object_type': forms.HiddenInput,
            'action_object_id': forms.HiddenInput,
        }

    def init_script_choice(self):
        choices = []
        for module in ScriptModule.objects.all():
            scripts = []
            for script_name in module.scripts.keys():
                name = f"{str(module.pk)}:{script_name}"
                scripts.append((name, script_name))
            if scripts:
                choices.append((str(module), scripts))
        self.fields['action_choice'].choices = choices

        if self.instance.action_type == EventRuleActionChoices.SCRIPT and self.instance.action_parameters:
            scriptmodule_id = self.instance.action_object_id
            script_name = self.instance.action_parameters.get('script_name')
            self.fields['action_choice'].initial = f'{scriptmodule_id}:{script_name}'

    def init_webhook_choice(self):
        initial = None
        if self.instance.action_type == EventRuleActionChoices.WEBHOOK:
            webhook_id = get_field_value(self, 'action_object_id')
            initial = Webhook.objects.get(pk=webhook_id) if webhook_id else None
        self.fields['action_choice'] = DynamicModelChoiceField(
            label=_('Webhook'),
            queryset=Webhook.objects.all(),
            required=True,
            initial=initial
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['action_object_type'].required = False
        self.fields['action_object_id'].required = False

        # Determine the action type
        action_type = get_field_value(self, 'action_type')

        if action_type == EventRuleActionChoices.WEBHOOK:
            self.init_webhook_choice()
        elif action_type == EventRuleActionChoices.SCRIPT:
            self.init_script_choice()

    def clean(self):
        super().clean()

        action_choice = self.cleaned_data.get('action_choice')
        # Webhook
        if self.cleaned_data.get('action_type') == EventRuleActionChoices.WEBHOOK:
            self.cleaned_data['action_object_type'] = ContentType.objects.get_for_model(action_choice)
            self.cleaned_data['action_object_id'] = action_choice.id
        # Script
        elif self.cleaned_data.get('action_type') == EventRuleActionChoices.SCRIPT:
            self.cleaned_data['action_object_type'] = ContentType.objects.get_for_model(
                ScriptModule,
                for_concrete_model=False
            )
            module_id, script_name = action_choice.split(":", maxsplit=1)
            self.cleaned_data['action_object_id'] = module_id

        return self.cleaned_data

    def save(self, *args, **kwargs):
        # Set action_parameters on the instance
        if self.cleaned_data['action_type'] == EventRuleActionChoices.SCRIPT:
            module_id, script_name = self.cleaned_data.get('action_choice').split(":", maxsplit=1)
            self.instance.action_parameters = {
                'script_name': script_name,
            }
        else:
            self.instance.action_parameters = None

        return super().save(*args, **kwargs)


class TagForm(forms.ModelForm):
    slug = SlugField()
    object_types = ContentTypeMultipleChoiceField(
        label=_('Object types'),
        queryset=ContentType.objects.with_feature('tags'),
        required=False
    )

    fieldsets = (
        ('Tag', ('name', 'slug', 'color', 'description', 'object_types')),
    )

    class Meta:
        model = Tag
        fields = [
            'name', 'slug', 'color', 'description', 'object_types',
        ]


class ConfigContextForm(SyncedDataMixin, forms.ModelForm):
    regions = DynamicModelMultipleChoiceField(
        label=_('Regions'),
        queryset=Region.objects.all(),
        required=False
    )
    site_groups = DynamicModelMultipleChoiceField(
        label=_('Site groups'),
        queryset=SiteGroup.objects.all(),
        required=False
    )
    sites = DynamicModelMultipleChoiceField(
        label=_('Sites'),
        queryset=Site.objects.all(),
        required=False
    )
    locations = DynamicModelMultipleChoiceField(
        label=_('Locations'),
        queryset=Location.objects.all(),
        required=False
    )
    device_types = DynamicModelMultipleChoiceField(
        label=_('Device types'),
        queryset=DeviceType.objects.all(),
        required=False
    )
    roles = DynamicModelMultipleChoiceField(
        label=_('Roles'),
        queryset=DeviceRole.objects.all(),
        required=False
    )
    platforms = DynamicModelMultipleChoiceField(
        label=_('Platforms'),
        queryset=Platform.objects.all(),
        required=False
    )
    cluster_types = DynamicModelMultipleChoiceField(
        label=_('Cluster types'),
        queryset=ClusterType.objects.all(),
        required=False
    )
    cluster_groups = DynamicModelMultipleChoiceField(
        label=_('Cluster groups'),
        queryset=ClusterGroup.objects.all(),
        required=False
    )
    clusters = DynamicModelMultipleChoiceField(
        label=_('Clusters'),
        queryset=Cluster.objects.all(),
        required=False
    )
    tenant_groups = DynamicModelMultipleChoiceField(
        label=_('Tenant groups'),
        queryset=TenantGroup.objects.all(),
        required=False
    )
    tenants = DynamicModelMultipleChoiceField(
        label=_('Tenants'),
        queryset=Tenant.objects.all(),
        required=False
    )
    tags = DynamicModelMultipleChoiceField(
        label=_('Tags'),
        queryset=Tag.objects.all(),
        required=False
    )
    data = JSONField(
        label=_('Data'),
        required=False
    )

    fieldsets = (
        (_('Config Context'), ('name', 'weight', 'description', 'data', 'is_active')),
        (_('Data Source'), ('data_source', 'data_file', 'auto_sync_enabled')),
        (_('Assignment'), (
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
            raise forms.ValidationError(_("Must specify either local data or a data file"))

        return self.cleaned_data


class ConfigTemplateForm(SyncedDataMixin, forms.ModelForm):
    tags = DynamicModelMultipleChoiceField(
        label=_('Tags'),
        queryset=Tag.objects.all(),
        required=False
    )
    template_code = forms.CharField(
        label=_('Template code'),
        required=False,
        widget=forms.Textarea(attrs={'class': 'font-monospace'})
    )

    fieldsets = (
        (_('Config Template'), ('name', 'description', 'environment_params', 'tags')),
        (_('Content'), ('template_code',)),
        (_('Data Source'), ('data_source', 'data_file', 'auto_sync_enabled')),
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
            raise forms.ValidationError(_("Must specify either local content or a data file"))

        return self.cleaned_data


class ImageAttachmentForm(forms.ModelForm):

    class Meta:
        model = ImageAttachment
        fields = [
            'name', 'image',
        ]


class JournalEntryForm(NetBoxModelForm):
    kind = forms.ChoiceField(
        label=_('Kind'),
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
