from django import forms
from django.contrib.contenttypes.models import ContentType

from extras.choices import *
from extras.models import *
from extras.utils import FeatureQuery
from utilities.forms import (
    BootstrapMixin, BulkEditForm, BulkEditNullBooleanSelect, ColorField, ContentTypeChoiceField, StaticSelect,
)

__all__ = (
    'ConfigContextBulkEditForm',
    'CustomFieldBulkEditForm',
    'CustomLinkBulkEditForm',
    'ExportTemplateBulkEditForm',
    'JournalEntryBulkEditForm',
    'TagBulkEditForm',
    'WebhookBulkEditForm',
)


class CustomFieldBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=CustomField.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    description = forms.CharField(
        required=False
    )
    required = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    weight = forms.IntegerField(
        required=False
    )

    class Meta:
        nullable_fields = []


class CustomLinkBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=CustomLink.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    content_type = ContentTypeChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_fields'),
        required=False
    )
    new_window = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    weight = forms.IntegerField(
        required=False
    )
    button_class = forms.ChoiceField(
        choices=CustomLinkButtonClassChoices,
        required=False,
        widget=StaticSelect()
    )

    class Meta:
        nullable_fields = []


class ExportTemplateBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ExportTemplate.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    content_type = ContentTypeChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_fields'),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    mime_type = forms.CharField(
        max_length=50,
        required=False
    )
    file_extension = forms.CharField(
        max_length=15,
        required=False
    )
    as_attachment = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect()
    )

    class Meta:
        nullable_fields = ['description', 'mime_type', 'file_extension']


class WebhookBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Webhook.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    enabled = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    type_create = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    type_update = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    type_delete = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    http_method = forms.ChoiceField(
        choices=WebhookHttpMethodChoices,
        required=False
    )
    payload_url = forms.CharField(
        required=False
    )
    ssl_verification = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    secret = forms.CharField(
        required=False
    )
    ca_file_path = forms.CharField(
        required=False
    )

    class Meta:
        nullable_fields = ['secret', 'conditions', 'ca_file_path']


class TagBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    color = ColorField(
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    class Meta:
        nullable_fields = ['description']


class ConfigContextBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ConfigContext.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    weight = forms.IntegerField(
        required=False,
        min_value=0
    )
    is_active = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    description = forms.CharField(
        required=False,
        max_length=100
    )

    class Meta:
        nullable_fields = [
            'description',
        ]


class JournalEntryBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=JournalEntry.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    kind = forms.ChoiceField(
        choices=JournalEntryKindChoices,
        required=False
    )
    comments = forms.CharField(
        required=False,
        widget=forms.Textarea()
    )

    class Meta:
        nullable_fields = []
