from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _

from core.models import DataFile, DataSource
from dcim.models import DeviceRole, DeviceType, Location, Platform, Region, Site, SiteGroup
from extras.choices import *
from extras.models import *
from extras.utils import FeatureQuery
from netbox.forms.base import NetBoxModelFilterSetForm
from tenancy.models import Tenant, TenantGroup
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, FilterForm, add_blank_choice
from utilities.forms.fields import ContentTypeMultipleChoiceField, DynamicModelMultipleChoiceField, TagFilterField
from utilities.forms.widgets import APISelectMultiple, DateTimePicker
from virtualization.models import Cluster, ClusterGroup, ClusterType
from .mixins import SavedFiltersMixin

__all__ = (
    'ConfigContextFilterForm',
    'ConfigTemplateFilterForm',
    'CustomFieldFilterForm',
    'CustomLinkFilterForm',
    'ExportTemplateFilterForm',
    'JournalEntryFilterForm',
    'LocalConfigContextFilterForm',
    'ObjectChangeFilterForm',
    'SavedFilterFilterForm',
    'TagFilterForm',
    'WebhookFilterForm',
)


class CustomFieldFilterForm(SavedFiltersMixin, FilterForm):
    fieldsets = (
        (None, ('q', 'filter_id')),
        ('Attributes', (
            'type', 'content_type_id', 'group_name', 'weight', 'required', 'ui_visibility', 'is_cloneable',
        )),
    )
    content_type_id = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.filter(FeatureQuery('custom_fields').get_query()),
        required=False,
        label=_('Object type')
    )
    type = forms.MultipleChoiceField(
        choices=CustomFieldTypeChoices,
        required=False,
        label=_('Field type')
    )
    group_name = forms.CharField(
        required=False
    )
    weight = forms.IntegerField(
        required=False
    )
    required = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    ui_visibility = forms.ChoiceField(
        choices=add_blank_choice(CustomFieldVisibilityChoices),
        required=False,
        label=_('UI visibility')
    )
    is_cloneable = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


class CustomLinkFilterForm(SavedFiltersMixin, FilterForm):
    fieldsets = (
        (None, ('q', 'filter_id')),
        ('Attributes', ('content_types', 'enabled', 'new_window', 'weight')),
    )
    content_types = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.filter(FeatureQuery('custom_links').get_query()),
        required=False
    )
    enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    new_window = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    weight = forms.IntegerField(
        required=False
    )


class ExportTemplateFilterForm(SavedFiltersMixin, FilterForm):
    fieldsets = (
        (None, ('q', 'filter_id')),
        ('Data', ('data_source_id', 'data_file_id')),
        ('Attributes', ('content_types', 'mime_type', 'file_extension', 'as_attachment')),
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
    content_types = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.filter(FeatureQuery('export_templates').get_query()),
        required=False
    )
    mime_type = forms.CharField(
        required=False,
        label=_('MIME type')
    )
    file_extension = forms.CharField(
        required=False
    )
    as_attachment = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


class SavedFilterFilterForm(SavedFiltersMixin, FilterForm):
    fieldsets = (
        (None, ('q', 'filter_id')),
        ('Attributes', ('content_types', 'enabled', 'shared', 'weight')),
    )
    content_types = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.filter(FeatureQuery('export_templates').get_query()),
        required=False
    )
    enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    shared = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    weight = forms.IntegerField(
        required=False
    )


class WebhookFilterForm(SavedFiltersMixin, FilterForm):
    fieldsets = (
        (None, ('q', 'filter_id')),
        ('Attributes', ('content_type_id', 'http_method', 'enabled')),
        ('Events', ('type_create', 'type_update', 'type_delete', 'type_job_start', 'type_job_end')),
    )
    content_type_id = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.filter(FeatureQuery('webhooks').get_query()),
        required=False,
        label=_('Object type')
    )
    http_method = forms.MultipleChoiceField(
        choices=WebhookHttpMethodChoices,
        required=False,
        label=_('HTTP method')
    )
    enabled = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    type_create = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        ),
        label=_('Object creations')
    )
    type_update = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        ),
        label=_('Object updates')
    )
    type_delete = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        ),
        label=_('Object deletions')
    )
    type_job_start = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        ),
        label=_('Job starts')
    )
    type_job_end = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        ),
        label=_('Job terminations')
    )


class TagFilterForm(SavedFiltersMixin, FilterForm):
    model = Tag
    content_type_id = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.filter(FeatureQuery('tags').get_query()),
        required=False,
        label=_('Tagged object type')
    )


class ConfigContextFilterForm(SavedFiltersMixin, FilterForm):
    fieldsets = (
        (None, ('q', 'filter_id', 'tag_id')),
        ('Data', ('data_source_id', 'data_file_id')),
        ('Location', ('region_id', 'site_group_id', 'site_id', 'location_id')),
        ('Device', ('device_type_id', 'platform_id', 'role_id')),
        ('Cluster', ('cluster_type_id', 'cluster_group_id', 'cluster_id')),
        ('Tenant', ('tenant_group_id', 'tenant_id'))
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
        label=_('Cluster types'),
        fetch_trigger='open'
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
        (None, ('q', 'filter_id', 'tag')),
        ('Data', ('data_source_id', 'data_file_id')),
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
        (None, ('q', 'filter_id', 'tag')),
        ('Creation', ('created_before', 'created_after', 'created_by_id')),
        ('Attributes', ('assigned_object_type_id', 'kind'))
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
        queryset=User.objects.all(),
        required=False,
        label=_('User'),
        widget=APISelectMultiple(
            api_url='/api/users/users/',
        )
    )
    assigned_object_type_id = DynamicModelMultipleChoiceField(
        queryset=ContentType.objects.all(),
        required=False,
        label=_('Object Type'),
        widget=APISelectMultiple(
            api_url='/api/extras/content-types/',
        )
    )
    kind = forms.ChoiceField(
        choices=add_blank_choice(JournalEntryKindChoices),
        required=False
    )
    tag = TagFilterField(model)


class ObjectChangeFilterForm(SavedFiltersMixin, FilterForm):
    model = ObjectChange
    fieldsets = (
        (None, ('q', 'filter_id')),
        ('Time', ('time_before', 'time_after')),
        ('Attributes', ('action', 'user_id', 'changed_object_type_id')),
    )
    time_after = forms.DateTimeField(
        required=False,
        label=_('After'),
        widget=DateTimePicker()
    )
    time_before = forms.DateTimeField(
        required=False,
        label=_('Before'),
        widget=DateTimePicker()
    )
    action = forms.ChoiceField(
        choices=add_blank_choice(ObjectChangeActionChoices),
        required=False
    )
    user_id = DynamicModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        label=_('User'),
        widget=APISelectMultiple(
            api_url='/api/users/users/',
        )
    )
    changed_object_type_id = DynamicModelMultipleChoiceField(
        queryset=ContentType.objects.all(),
        required=False,
        label=_('Object Type'),
        widget=APISelectMultiple(
            api_url='/api/extras/content-types/',
        )
    )
