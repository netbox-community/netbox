from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _

from dcim.models import DeviceRole, DeviceType, Platform, Region, Site, SiteGroup
from extras.choices import *
from extras.models import *
from extras.utils import FeatureQuery
from tenancy.models import Tenant, TenantGroup
from utilities.forms import (
    add_blank_choice, APISelectMultiple, BootstrapMixin, ContentTypeChoiceField,
    ContentTypeMultipleChoiceField, DateTimePicker, DynamicModelMultipleChoiceField, StaticSelect,
    StaticSelectMultiple, BOOLEAN_WITH_BLANK_CHOICES,
)
from virtualization.models import Cluster, ClusterGroup

__all__ = (
    'ConfigContextFilterForm',
    'CustomFieldFilterForm',
    'CustomLinkFilterForm',
    'ExportTemplateFilterForm',
    'JournalEntryFilterForm',
    'LocalConfigContextFilterForm',
    'ObjectChangeFilterForm',
    'TagFilterForm',
    'WebhookFilterForm',
)


class CustomFieldFilterForm(BootstrapMixin, forms.Form):
    field_groups = [
        ['q'],
        ['type', 'content_types'],
        ['weight', 'required'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    content_types = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_fields'),
        required=False
    )
    type = forms.MultipleChoiceField(
        choices=CustomFieldTypeChoices,
        required=False,
        widget=StaticSelectMultiple(),
        label=_('Field type')
    )
    weight = forms.IntegerField(
        required=False
    )
    required = forms.NullBooleanField(
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


class CustomLinkFilterForm(BootstrapMixin, forms.Form):
    field_groups = [
        ['q'],
        ['content_type', 'weight', 'new_window'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    content_type = ContentTypeChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_fields'),
        required=False
    )
    weight = forms.IntegerField(
        required=False
    )
    new_window = forms.NullBooleanField(
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


class ExportTemplateFilterForm(BootstrapMixin, forms.Form):
    field_groups = [
        ['q'],
        ['content_type', 'mime_type', 'file_extension', 'as_attachment'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    content_type = ContentTypeChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_fields'),
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
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


class WebhookFilterForm(BootstrapMixin, forms.Form):
    field_groups = [
        ['q'],
        ['content_types', 'http_method', 'enabled'],
        ['type_create', 'type_update', 'type_delete'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    content_types = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_fields'),
        required=False
    )
    http_method = forms.MultipleChoiceField(
        choices=WebhookHttpMethodChoices,
        required=False,
        widget=StaticSelectMultiple(),
        label=_('HTTP method')
    )
    enabled = forms.NullBooleanField(
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    type_create = forms.NullBooleanField(
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    type_update = forms.NullBooleanField(
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    type_delete = forms.NullBooleanField(
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


class TagFilterForm(BootstrapMixin, forms.Form):
    model = Tag
    q = forms.CharField(
        required=False,
        label=_('Search')
    )
    content_type_id = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.filter(FeatureQuery('tags').get_query()),
        required=False,
        label=_('Tagged object type')
    )


class ConfigContextFilterForm(BootstrapMixin, forms.Form):
    field_groups = [
        ['q', 'tag'],
        ['region_id', 'site_group_id', 'site_id'],
        ['device_type_id', 'platform_id', 'role_id'],
        ['cluster_group_id', 'cluster_id'],
        ['tenant_group_id', 'tenant_id']
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Regions'),
        fetch_trigger='open'
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site groups'),
        fetch_trigger='open'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_('Sites'),
        fetch_trigger='open'
    )
    device_type_id = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        label=_('Device types'),
        fetch_trigger='open'
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        label=_('Roles'),
        fetch_trigger='open'
    )
    platform_id = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        label=_('Platforms'),
        fetch_trigger='open'
    )
    cluster_group_id = DynamicModelMultipleChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        label=_('Cluster groups'),
        fetch_trigger='open'
    )
    cluster_id = DynamicModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        label=_('Clusters'),
        fetch_trigger='open'
    )
    tenant_group_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        label=_('Tenant groups'),
        fetch_trigger='open'
    )
    tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_('Tenant'),
        fetch_trigger='open'
    )
    tag = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        to_field_name='slug',
        required=False,
        label=_('Tags'),
        fetch_trigger='open'
    )


class LocalConfigContextFilterForm(forms.Form):
    local_context_data = forms.NullBooleanField(
        required=False,
        label=_('Has local config context data'),
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


class JournalEntryFilterForm(BootstrapMixin, forms.Form):
    model = JournalEntry
    field_groups = [
        ['q'],
        ['created_before', 'created_after', 'created_by_id'],
        ['assigned_object_type_id', 'kind']
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
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
        ),
        fetch_trigger='open'
    )
    assigned_object_type_id = DynamicModelMultipleChoiceField(
        queryset=ContentType.objects.all(),
        required=False,
        label=_('Object Type'),
        widget=APISelectMultiple(
            api_url='/api/extras/content-types/',
        ),
        fetch_trigger='open'
    )
    kind = forms.ChoiceField(
        choices=add_blank_choice(JournalEntryKindChoices),
        required=False,
        widget=StaticSelect()
    )


class ObjectChangeFilterForm(BootstrapMixin, forms.Form):
    model = ObjectChange
    field_groups = [
        ['q'],
        ['time_before', 'time_after', 'action'],
        ['user_id', 'changed_object_type_id'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
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
        required=False,
        widget=StaticSelect()
    )
    user_id = DynamicModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        label=_('User'),
        widget=APISelectMultiple(
            api_url='/api/users/users/',
        ),
        fetch_trigger='open'
    )
    changed_object_type_id = DynamicModelMultipleChoiceField(
        queryset=ContentType.objects.all(),
        required=False,
        label=_('Object Type'),
        widget=APISelectMultiple(
            api_url='/api/extras/content-types/',
        ),
        fetch_trigger='open'
    )
