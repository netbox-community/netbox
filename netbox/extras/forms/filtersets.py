from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from core.models import ObjectType, DataFile, DataSource
from dcim.models import DeviceRole, DeviceType, Location, Platform, Region, Site, SiteGroup
from extras.choices import *
from extras.models import *
from netbox.events import get_event_type_choices
from netbox.forms.base import NetBoxModelFilterSetForm
from netbox.forms.mixins import SavedFiltersMixin
from tenancy.models import Tenant, TenantGroup
from users.models import Group
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, FilterForm, add_blank_choice
from utilities.forms.fields import (
    ContentTypeChoiceField, ContentTypeMultipleChoiceField, DynamicModelMultipleChoiceField, TagFilterField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import DateTimePicker
from virtualization.models import Cluster, ClusterGroup, ClusterType

__all__ = (
    'ConfigContextFilterForm',
    'ConfigTemplateFilterForm',
    'CustomFieldChoiceSetFilterForm',
    'CustomFieldFilterForm',
    'CustomLinkFilterForm',
    'EventRuleFilterForm',
    'ExportTemplateFilterForm',
    'ImageAttachmentFilterForm',
    'JournalEntryFilterForm',
    'LocalConfigContextFilterForm',
    'NotificationGroupFilterForm',
    'SavedFilterFilterForm',
    'TagFilterForm',
    'WebhookFilterForm',
)


class CustomFieldFilterForm(SavedFiltersMixin, FilterForm):
    fieldsets = (
        FieldSet('q', 'filter_id'),
        FieldSet(
            'type', 'related_object_type_id', 'group_name', 'weight', 'required', 'choice_set_id', 'ui_visible',
            'ui_editable', 'is_cloneable', name=_('Attributes')
        ),
        FieldSet(
            'validation_minimum', 'validation_maximum', 'validation_regex', 'validation_unique', name=_('Validation')
        ),
    )
    related_object_type_id = ContentTypeMultipleChoiceField(
        queryset=ObjectType.objects.with_feature('custom_fields'),
        required=False,
        label=_('Related object type')
    )
    type = forms.MultipleChoiceField(
        choices=CustomFieldTypeChoices,
        required=False,
        label=_('Field type')
    )
    group_name = forms.CharField(
        label=_('Group name'),
        required=False
    )
    weight = forms.IntegerField(
        label=_('Weight'),
        required=False
    )
    required = forms.NullBooleanField(
        label=_('Required'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    choice_set_id = DynamicModelMultipleChoiceField(
        queryset=CustomFieldChoiceSet.objects.all(),
        required=False,
        label=_('Choice set')
    )
    ui_visible = forms.ChoiceField(
        choices=add_blank_choice(CustomFieldUIVisibleChoices),
        required=False,
        label=_('UI visible')
    )
    ui_editable = forms.ChoiceField(
        choices=add_blank_choice(CustomFieldUIEditableChoices),
        required=False,
        label=_('UI editable')
    )
    is_cloneable = forms.NullBooleanField(
        label=_('Is cloneable'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    validation_minimum = forms.IntegerField(
        label=_('Minimum value'),
        required=False
    )
    validation_maximum = forms.IntegerField(
        label=_('Maximum value'),
        required=False
    )
    validation_regex = forms.CharField(
        label=_('Validation regex'),
        required=False
    )
    validation_unique = forms.NullBooleanField(
        label=_('Must be unique'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


class CustomFieldChoiceSetFilterForm(SavedFiltersMixin, FilterForm):
    fieldsets = (
        FieldSet('q', 'filter_id'),
        FieldSet('base_choices', 'choice', name=_('Choices')),
    )
    base_choices = forms.MultipleChoiceField(
        choices=CustomFieldChoiceSetBaseChoices,
        required=False
    )
    choice = forms.CharField(
        required=False
    )


class CustomLinkFilterForm(SavedFiltersMixin, FilterForm):
    fieldsets = (
        FieldSet('q', 'filter_id'),
        FieldSet('object_type', 'enabled', 'new_window', 'weight', name=_('Attributes')),
    )
    object_type = ContentTypeMultipleChoiceField(
        label=_('Object types'),
        queryset=ObjectType.objects.with_feature('custom_links'),
        required=False
    )
    enabled = forms.NullBooleanField(
        label=_('Enabled'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    new_window = forms.NullBooleanField(
        label=_('New window'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    weight = forms.IntegerField(
        label=_('Weight'),
        required=False
    )


class ExportTemplateFilterForm(SavedFiltersMixin, FilterForm):
    fieldsets = (
        FieldSet('q', 'filter_id'),
        FieldSet('data_source_id', 'data_file_id', name=_('Data')),
        FieldSet('object_type_id', 'mime_type', 'file_extension', 'as_attachment', name=_('Attributes')),
    )
    data_source_id = DynamicModelMultipleChoiceField(
        queryset=DataSource.objects.all(),
        required=False,
        label=_('Data source')
    )
    data_file_id = DynamicModelMultipleChoiceField(
        queryset=DataFile.objects.all(),
        required=False,
        label=_('Data file'),
        query_params={
            'source_id': '$data_source_id'
        }
    )
    object_type_id = ContentTypeMultipleChoiceField(
        queryset=ObjectType.objects.with_feature('export_templates'),
        required=False,
        label=_('Content types')
    )
    mime_type = forms.CharField(
        required=False,
        label=_('MIME type')
    )
    file_extension = forms.CharField(
        label=_('File extension'),
        required=False
    )
    as_attachment = forms.NullBooleanField(
        label=_('As attachment'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


class ImageAttachmentFilterForm(SavedFiltersMixin, FilterForm):
    fieldsets = (
        FieldSet('q', 'filter_id'),
        FieldSet('object_type_id', 'name', name=_('Attributes')),
    )
    object_type_id = ContentTypeChoiceField(
        label=_('Object type'),
        queryset=ObjectType.objects.with_feature('image_attachments'),
        required=False
    )
    name = forms.CharField(
        label=_('Name'),
        required=False
    )


class SavedFilterFilterForm(SavedFiltersMixin, FilterForm):
    fieldsets = (
        FieldSet('q', 'filter_id'),
        FieldSet('object_type', 'enabled', 'shared', 'weight', name=_('Attributes')),
    )
    object_type = ContentTypeMultipleChoiceField(
        label=_('Object types'),
        queryset=ObjectType.objects.public(),
        required=False
    )
    enabled = forms.NullBooleanField(
        label=_('Enabled'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    shared = forms.NullBooleanField(
        label=_('Shared'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    weight = forms.IntegerField(
        label=_('Weight'),
        required=False
    )


class WebhookFilterForm(NetBoxModelFilterSetForm):
    model = Webhook
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('payload_url', 'http_method', 'http_content_type', name=_('Attributes')),
    )
    http_content_type = forms.CharField(
        label=_('HTTP content type'),
        required=False
    )
    payload_url = forms.CharField(
        label=_('Payload URL'),
        required=False
    )
    http_method = forms.MultipleChoiceField(
        choices=WebhookHttpMethodChoices,
        required=False,
        label=_('HTTP method')
    )
    tag = TagFilterField(model)


class EventRuleFilterForm(NetBoxModelFilterSetForm):
    model = EventRule
    tag = TagFilterField(model)

    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('object_type_id', 'event_type', 'action_type', 'enabled', name=_('Attributes')),
    )
    object_type_id = ContentTypeMultipleChoiceField(
        queryset=ObjectType.objects.with_feature('event_rules'),
        required=False,
        label=_('Object type')
    )
    event_type = forms.MultipleChoiceField(
        choices=get_event_type_choices,
        required=False,
        label=_('Event type')
    )
    action_type = forms.ChoiceField(
        choices=add_blank_choice(EventRuleActionChoices),
        required=False,
        label=_('Action type')
    )
    enabled = forms.NullBooleanField(
        label=_('Enabled'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


class TagFilterForm(SavedFiltersMixin, FilterForm):
    model = Tag
    content_type_id = ContentTypeMultipleChoiceField(
        queryset=ObjectType.objects.with_feature('tags'),
        required=False,
        label=_('Tagged object type')
    )
    for_object_type_id = ContentTypeChoiceField(
        queryset=ObjectType.objects.with_feature('tags'),
        required=False,
        label=_('Allowed object type')
    )


class ConfigContextFilterForm(SavedFiltersMixin, FilterForm):
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag_id'),
        FieldSet('data_source_id', 'data_file_id', name=_('Data')),
        FieldSet('region_id', 'site_group_id', 'site_id', 'location_id', name=_('Location')),
        FieldSet('device_type_id', 'platform_id', 'role_id', name=_('Device')),
        FieldSet('cluster_type_id', 'cluster_group_id', 'cluster_id', name=_('Cluster')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant'))
    )
    data_source_id = DynamicModelMultipleChoiceField(
        queryset=DataSource.objects.all(),
        required=False,
        label=_('Data source')
    )
    data_file_id = DynamicModelMultipleChoiceField(
        queryset=DataFile.objects.all(),
        required=False,
        label=_('Data file'),
        query_params={
            'source_id': '$data_source_id'
        }
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Regions')
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site groups')
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_('Sites')
    )
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        label=_('Locations')
    )
    device_type_id = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        label=_('Device types')
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        label=_('Roles')
    )
    platform_id = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        label=_('Platforms')
    )
    cluster_type_id = DynamicModelMultipleChoiceField(
        queryset=ClusterType.objects.all(),
        required=False,
        label=_('Cluster types')
    )
    cluster_group_id = DynamicModelMultipleChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        label=_('Cluster groups')
    )
    cluster_id = DynamicModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        label=_('Clusters')
    )
    tenant_group_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        label=_('Tenant groups')
    )
    tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_('Tenant')
    )
    tag_id = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label=_('Tags')
    )


class ConfigTemplateFilterForm(SavedFiltersMixin, FilterForm):
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('data_source_id', 'data_file_id', name=_('Data')),
    )
    data_source_id = DynamicModelMultipleChoiceField(
        queryset=DataSource.objects.all(),
        required=False,
        label=_('Data source')
    )
    data_file_id = DynamicModelMultipleChoiceField(
        queryset=DataFile.objects.all(),
        required=False,
        label=_('Data file'),
        query_params={
            'source_id': '$data_source_id'
        }
    )
    tag = TagFilterField(ConfigTemplate)


class LocalConfigContextFilterForm(forms.Form):
    local_context_data = forms.NullBooleanField(
        required=False,
        label=_('Has local config context data'),
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


class JournalEntryFilterForm(NetBoxModelFilterSetForm):
    model = JournalEntry
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('created_before', 'created_after', 'created_by_id', name=_('Creation')),
        FieldSet('assigned_object_type_id', 'kind', name=_('Attributes')),
    )
    created_after = forms.DateTimeField(
        required=False,
        label=_('After'),
        widget=DateTimePicker()
    )
    created_before = forms.DateTimeField(
        required=False,
        label=_('Before'),
        widget=DateTimePicker()
    )
    created_by_id = DynamicModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        required=False,
        label=_('User')
    )
    assigned_object_type_id = ContentTypeMultipleChoiceField(
        queryset=ObjectType.objects.with_feature('journaling'),
        required=False,
        label=_('Object Type'),
    )
    kind = forms.ChoiceField(
        label=_('Kind'),
        choices=add_blank_choice(JournalEntryKindChoices),
        required=False
    )
    tag = TagFilterField(model)


class NotificationGroupFilterForm(SavedFiltersMixin, FilterForm):
    user_id = DynamicModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        required=False,
        label=_('User')
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label=_('Group')
    )
