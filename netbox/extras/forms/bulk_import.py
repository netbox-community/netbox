import re

from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from core.models import DataFile, DataSource, ObjectType
from extras.choices import *
from extras.models import *
from netbox.events import get_event_type_choices
from netbox.forms import NetBoxModelImportForm, OwnerCSVMixin, PrimaryModelImportForm
from users.models import Group, User
from utilities.forms import CSVModelForm
from utilities.forms.fields import (
    CSVChoiceField,
    CSVContentTypeField,
    CSVModelChoiceField,
    CSVModelMultipleChoiceField,
    CSVMultipleChoiceField,
    CSVMultipleContentTypeField,
    SlugField,
)

__all__ = (
    'ConfigContextProfileImportForm',
    'ConfigTemplateImportForm',
    'CustomFieldChoiceSetImportForm',
    'CustomFieldImportForm',
    'CustomLinkImportForm',
    'EventRuleImportForm',
    'ExportTemplateImportForm',
    'JournalEntryImportForm',
    'NotificationGroupImportForm',
    'SavedFilterImportForm',
    'TagImportForm',
    'WebhookImportForm',
)


class CustomFieldImportForm(OwnerCSVMixin, CSVModelForm):
    object_types = CSVMultipleContentTypeField(
        label=_('Object types'),
        queryset=ObjectType.objects.with_feature('custom_fields'),
        help_text=_("One or more assigned object types")
    )
    type = CSVChoiceField(
        label=_('Type'),
        choices=CustomFieldTypeChoices,
        help_text=_('Field data type (e.g. text, integer, etc.)')
    )
    related_object_type = CSVContentTypeField(
        label=_('Object type'),
        queryset=ObjectType.objects.public(),
        required=False,
        help_text=_("Object type (for object or multi-object fields)")
    )
    choice_set = CSVModelChoiceField(
        label=_('Choice set'),
        queryset=CustomFieldChoiceSet.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Choice set (for selection fields)')
    )
    ui_visible = CSVChoiceField(
        label=_('UI visible'),
        choices=CustomFieldUIVisibleChoices,
        required=False,
        help_text=_('Whether the custom field is displayed in the UI')
    )
    ui_editable = CSVChoiceField(
        label=_('UI editable'),
        choices=CustomFieldUIEditableChoices,
        required=False,
        help_text=_('Whether the custom field is editable in the UI')
    )

    class Meta:
        model = CustomField
        fields = (
            'name', 'label', 'group_name', 'type', 'object_types', 'related_object_type', 'required', 'unique',
            'description', 'search_weight', 'filter_logic', 'default', 'choice_set', 'weight', 'validation_minimum',
            'validation_maximum', 'validation_regex', 'ui_visible', 'ui_editable', 'is_cloneable', 'owner', 'comments',
        )


class CustomFieldChoiceSetImportForm(OwnerCSVMixin, CSVModelForm):
    base_choices = CSVChoiceField(
        choices=CustomFieldChoiceSetBaseChoices,
        required=False,
        help_text=_('The base set of predefined choices to use (if any)')
    )
    extra_choices = SimpleArrayField(
        base_field=forms.CharField(),
        required=False,
        help_text=_(
            'Quoted string of comma-separated field choices with optional labels separated by colon: '
            '"choice1:First Choice,choice2:Second Choice"'
        )
    )

    class Meta:
        model = CustomFieldChoiceSet
        fields = (
            'name', 'description', 'base_choices', 'extra_choices', 'order_alphabetically', 'owner',
        )

    def clean_extra_choices(self):
        if isinstance(self.cleaned_data['extra_choices'], list):
            data = []
            for line in self.cleaned_data['extra_choices']:
                try:
                    value, label = re.split(r'(?<!\\):', line, maxsplit=1)
                    value = value.replace('\\:', ':')
                    label = label.replace('\\:', ':')
                except ValueError:
                    value, label = line, line
                data.append((value, label))
            return data
        return None


class CustomLinkImportForm(OwnerCSVMixin, CSVModelForm):
    object_types = CSVMultipleContentTypeField(
        label=_('Object types'),
        queryset=ObjectType.objects.with_feature('custom_links'),
        help_text=_("One or more assigned object types")
    )
    button_class = CSVChoiceField(
        label=_('button class'),
        required=False,
        choices=CustomLinkButtonClassChoices,
        help_text=_('The class of the first link in a group will be used for the dropdown button')
    )

    class Meta:
        model = CustomLink
        fields = (
            'name', 'object_types', 'enabled', 'weight', 'group_name', 'button_class', 'new_window', 'link_text',
            'link_url', 'owner',
        )


class ExportTemplateImportForm(OwnerCSVMixin, CSVModelForm):
    object_types = CSVMultipleContentTypeField(
        label=_('Object types'),
        queryset=ObjectType.objects.with_feature('export_templates'),
        help_text=_("One or more assigned object types")
    )

    class Meta:
        model = ExportTemplate
        fields = (
            'name', 'object_types', 'description', 'environment_params', 'mime_type', 'file_name', 'file_extension',
            'as_attachment', 'template_code', 'owner',
        )


class ConfigContextProfileImportForm(PrimaryModelImportForm):

    class Meta:
        model = ConfigContextProfile
        fields = [
            'name', 'description', 'schema', 'owner', 'comments', 'tags',
        ]


class ConfigTemplateImportForm(OwnerCSVMixin, CSVModelForm):
    data_source = CSVModelChoiceField(
        label=_('Data source'),
        queryset=DataSource.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Data source which provides the data file')
    )
    data_file = CSVModelChoiceField(
        label=_('Data file'),
        queryset=DataFile.objects.all(),
        required=False,
        to_field_name='path',
        help_text=_('Data file containing the template code')
    )
    auto_sync_enabled = forms.BooleanField(
        required=False,
        label=_('Auto sync enabled'),
        help_text=_("Enable automatic synchronization of template content when the data file is updated")
    )

    class Meta:
        model = ConfigTemplate
        fields = (
            'name', 'description', 'template_code', 'data_source', 'data_file', 'auto_sync_enabled',
            'environment_params', 'mime_type', 'file_name', 'file_extension', 'as_attachment', 'owner', 'tags',
        )

    def clean(self):
        super().clean()

        # Make sure template_code is None when it's not included in the uploaded data
        if not self.data.get('template_code') and not self.data.get('data_file'):
            raise forms.ValidationError(_("Must specify either local content or a data file"))
        return self.cleaned_data['template_code']


class SavedFilterImportForm(OwnerCSVMixin, CSVModelForm):
    object_types = CSVMultipleContentTypeField(
        label=_('Object types'),
        queryset=ObjectType.objects.all(),
        help_text=_("One or more assigned object types")
    )

    class Meta:
        model = SavedFilter
        fields = (
            'name', 'slug', 'object_types', 'description', 'weight', 'enabled', 'shared', 'parameters', 'owner',
        )


class WebhookImportForm(OwnerCSVMixin, NetBoxModelImportForm):

    class Meta:
        model = Webhook
        fields = (
            'name', 'payload_url', 'http_method', 'http_content_type', 'additional_headers', 'body_template',
            'secret', 'ssl_verification', 'ca_file_path', 'description', 'owner', 'tags'
        )


class EventRuleImportForm(OwnerCSVMixin, NetBoxModelImportForm):
    object_types = CSVMultipleContentTypeField(
        label=_('Object types'),
        queryset=ObjectType.objects.with_feature('event_rules'),
        help_text=_("One or more assigned object types")
    )
    event_types = CSVMultipleChoiceField(
        choices=get_event_type_choices(),
        label=_('Event types'),
        help_text=_('The event type(s) which will trigger this rule')
    )
    action_object = forms.CharField(
        label=_('Action object'),
        required=True,
        help_text=_('Webhook name or script as dotted path module.Class')
    )

    class Meta:
        model = EventRule
        fields = (
            'name', 'description', 'enabled', 'conditions', 'object_types', 'event_types', 'action_type',
            'owner', 'comments', 'tags'
        )

    def clean(self):
        super().clean()

        action_object = self.cleaned_data.get('action_object')
        action_type = self.cleaned_data.get('action_type')
        if action_object and action_type:
            # Webhook
            if action_type == EventRuleActionChoices.WEBHOOK:
                try:
                    webhook = Webhook.objects.get(name=action_object)
                except Webhook.DoesNotExist:
                    raise forms.ValidationError(_("Webhook {name} not found").format(name=action_object))
                self.instance.action_object = webhook
            # Script
            elif action_type == EventRuleActionChoices.SCRIPT:
                from extras.scripts import get_module_and_script
                module_name, script_name = action_object.split('.', 1)
                try:
                    script = get_module_and_script(module_name, script_name)[1]
                except ObjectDoesNotExist:
                    raise forms.ValidationError(_("Script {name} not found").format(name=action_object))
                self.instance.action_object = script
                self.instance.action_object_type = ObjectType.objects.get_for_model(script, for_concrete_model=False)


class TagImportForm(OwnerCSVMixin, CSVModelForm):
    slug = SlugField()
    object_types = CSVMultipleContentTypeField(
        label=_('Object types'),
        queryset=ObjectType.objects.with_feature('tags'),
        help_text=_("One or more assigned object types"),
        required=False,
    )

    class Meta:
        model = Tag
        fields = (
            'name', 'slug', 'color', 'weight', 'description', 'object_types', 'owner',
        )


class JournalEntryImportForm(NetBoxModelImportForm):
    assigned_object_type = CSVContentTypeField(
        queryset=ObjectType.objects.all(),
        label=_('Assigned object type'),
    )
    kind = CSVChoiceField(
        label=_('Kind'),
        choices=JournalEntryKindChoices,
        help_text=_('The classification of entry')
    )
    comments = forms.CharField(
        label=_('Comments'),
        required=True
    )

    class Meta:
        model = JournalEntry
        fields = (
            'assigned_object_type', 'assigned_object_id', 'created_by', 'kind', 'comments', 'tags'
        )


class NotificationGroupImportForm(CSVModelForm):
    users = CSVModelMultipleChoiceField(
        label=_('Users'),
        queryset=User.objects.all(),
        required=False,
        to_field_name='username',
        help_text=_('User names separated by commas, encased with double quotes')
    )
    groups = CSVModelMultipleChoiceField(
        label=_('Groups'),
        queryset=Group.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Group names separated by commas, encased with double quotes')
    )

    class Meta:
        model = NotificationGroup
        fields = ('name', 'description', 'users', 'groups')
