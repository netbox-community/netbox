from django import forms
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.forms import SimpleArrayField
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from extras.choices import CustomFieldVisibilityChoices, CustomFieldTypeChoices
from extras.models import *
from extras.utils import FeatureQuery
from utilities.forms import CSVChoiceField, CSVContentTypeField, CSVModelForm, CSVMultipleContentTypeField, SlugField

__all__ = (
    'CustomFieldImportForm',
    'CustomLinkImportForm',
    'ExportTemplateImportForm',
    'SavedFilterImportForm',
    'TagImportForm',
    'WebhookImportForm',
)


class CustomFieldImportForm(CSVModelForm):
    content_types = CSVMultipleContentTypeField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_fields'),
        help_text=_("One or more assigned object types")
    )
    type = CSVChoiceField(
        choices=CustomFieldTypeChoices,
        help_text=_('Field data type (e.g. text, integer, etc.)')
    )
    object_type = CSVContentTypeField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_fields'),
        required=False,
        help_text=_("Object type (for object or multi-object fields)")
    )
    choices = SimpleArrayField(
        base_field=forms.CharField(),
        required=False,
        help_text=_('Comma-separated list of field choices')
    )
    ui_visibility = CSVChoiceField(
        choices=CustomFieldVisibilityChoices,
        help_text=_('How the custom field is displayed in the user interface')
    )

    class Meta:
        model = CustomField
        fields = (
            'name', 'label', 'group_name', 'type', 'content_types', 'object_type', 'required', 'description',
            'search_weight', 'filter_logic', 'default', 'choices', 'weight', 'validation_minimum', 'validation_maximum',
            'validation_regex', 'ui_visibility',
        )


class CustomLinkImportForm(CSVModelForm):
    content_types = CSVMultipleContentTypeField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_links'),
        help_text=_("One or more assigned object types")
    )

    class Meta:
        model = CustomLink
        fields = (
            'name', 'content_types', 'enabled', 'weight', 'group_name', 'button_class', 'new_window', 'link_text',
            'link_url',
        )


class ExportTemplateImportForm(CSVModelForm):
    content_types = CSVMultipleContentTypeField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('export_templates'),
        help_text=_("One or more assigned object types")
    )

    class Meta:
        model = ExportTemplate
        fields = (
            'name', 'content_types', 'description', 'mime_type', 'file_extension', 'as_attachment', 'template_code',
        )


class SavedFilterImportForm(CSVModelForm):
    content_types = CSVMultipleContentTypeField(
        queryset=ContentType.objects.all(),
        help_text=_("One or more assigned object types")
    )

    class Meta:
        model = SavedFilter
        fields = (
            'name', 'slug', 'content_types', 'description', 'weight', 'enabled', 'shared', 'parameters',
        )


class WebhookImportForm(CSVModelForm):
    content_types = CSVMultipleContentTypeField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('webhooks'),
        help_text=_("One or more assigned object types")
    )

    class Meta:
        model = Webhook
        fields = (
            'name', 'enabled', 'content_types', 'type_create', 'type_update', 'type_delete', 'payload_url',
            'http_method', 'http_content_type', 'additional_headers', 'body_template', 'secret', 'ssl_verification',
            'ca_file_path'
        )


class TagImportForm(CSVModelForm):
    slug = SlugField()

    class Meta:
        model = Tag
        fields = ('name', 'slug', 'color', 'description')
        help_texts = {
            'color': mark_safe(_('RGB color in hexadecimal (e.g. <code>00ff00</code>)')),
        }
