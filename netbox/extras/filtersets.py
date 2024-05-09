import django_filters
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.translation import gettext as _

from core.models import DataSource, ObjectType
from dcim.models import DeviceRole, DeviceType, Location, Platform, Region, Site, SiteGroup
from netbox.filtersets import BaseFilterSet, ChangeLoggedModelFilterSet, NetBoxModelFilterSet
from tenancy.models import Tenant, TenantGroup
from utilities.filters import ContentTypeFilter, MultiValueCharFilter, MultiValueNumberFilter
from virtualization.models import Cluster, ClusterGroup, ClusterType
from .choices import *
from .filters import TagFilter
from .models import *

__all__ = (
    'BookmarkFilterSet',
    'ConfigContextFilterSet',
    'ConfigTemplateFilterSet',
    'CustomFieldChoiceSetFilterSet',
    'CustomFieldFilterSet',
    'CustomLinkFilterSet',
    'EventRuleFilterSet',
    'ExportTemplateFilterSet',
    'ImageAttachmentFilterSet',
    'JournalEntryFilterSet',
    'LocalConfigContextFilterSet',
    'ObjectChangeFilterSet',
    'ObjectTypeFilterSet',
    'SavedFilterFilterSet',
    'ScriptFilterSet',
    'TagFilterSet',
    'WebhookFilterSet',
)


class ScriptFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    module_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ScriptModule.objects.all(),
        label=_('Script module (ID)'),
    )

    class Meta:
        model = Script
        fields = ('id', 'name', 'is_executable')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
        )


class WebhookFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    http_method = django_filters.MultipleChoiceFilter(
        choices=WebhookHttpMethodChoices
    )
    payload_url = MultiValueCharFilter(
        lookup_expr='icontains'
    )

    class Meta:
        model = Webhook
        fields = (
            'id', 'name', 'payload_url', 'http_method', 'http_content_type', 'secret', 'ssl_verification',
            'ca_file_path', 'description',
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(payload_url__icontains=value)
        )


class EventRuleFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    object_type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ObjectType.objects.all(),
        field_name='object_types'
    )
    object_type = ContentTypeFilter(
        field_name='object_types'
    )
    action_type = django_filters.MultipleChoiceFilter(
        choices=EventRuleActionChoices
    )
    action_object_type = ContentTypeFilter()
    action_object_id = MultiValueNumberFilter()

    class Meta:
        model = EventRule
        fields = (
            'id', 'name', 'type_create', 'type_update', 'type_delete', 'type_job_start', 'type_job_end', 'enabled',
            'action_type', 'description',
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        )


class CustomFieldFilterSet(ChangeLoggedModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    type = django_filters.MultipleChoiceFilter(
        choices=CustomFieldTypeChoices
    )
    object_type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ObjectType.objects.all(),
        field_name='object_types'
    )
    object_type = ContentTypeFilter(
        field_name='object_types'
    )
    related_object_type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ObjectType.objects.all(),
        field_name='related_object_type'
    )
    related_object_type = ContentTypeFilter()
    choice_set_id = django_filters.ModelMultipleChoiceFilter(
        queryset=CustomFieldChoiceSet.objects.all()
    )
    choice_set = django_filters.ModelMultipleChoiceFilter(
        field_name='choice_set__name',
        queryset=CustomFieldChoiceSet.objects.all(),
        to_field_name='name'
    )

    class Meta:
        model = CustomField
        fields = (
            'id', 'name', 'label', 'group_name', 'required', 'search_weight', 'filter_logic', 'ui_visible',
            'ui_editable', 'weight', 'is_cloneable', 'description', 'validation_minimum', 'validation_maximum',
            'validation_regex',
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(label__icontains=value) |
            Q(group_name__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        )


class CustomFieldChoiceSetFilterSet(ChangeLoggedModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    choice = MultiValueCharFilter(
        method='filter_by_choice'
    )

    class Meta:
        model = CustomFieldChoiceSet
        fields = (
            'id', 'name', 'description', 'base_choices', 'order_alphabetically',
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )

    def filter_by_choice(self, queryset, name, value):
        # TODO: Support case-insensitive matching
        return queryset.filter(extra_choices__overlap=value)


class CustomLinkFilterSet(ChangeLoggedModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    object_type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ObjectType.objects.all(),
        field_name='object_types'
    )
    object_type = ContentTypeFilter(
        field_name='object_types'
    )

    class Meta:
        model = CustomLink
        fields = (
            'id', 'name', 'enabled', 'link_text', 'link_url', 'weight', 'group_name', 'new_window', 'button_class',
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(link_text__icontains=value) |
            Q(link_url__icontains=value) |
            Q(group_name__icontains=value)
        )


class ExportTemplateFilterSet(ChangeLoggedModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    object_type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ObjectType.objects.all(),
        field_name='object_types'
    )
    object_type = ContentTypeFilter(
        field_name='object_types'
    )
    data_source_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DataSource.objects.all(),
        label=_('Data source (ID)'),
    )
    data_file_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DataSource.objects.all(),
        label=_('Data file (ID)'),
    )

    class Meta:
        model = ExportTemplate
        fields = (
            'id', 'name', 'description', 'mime_type', 'file_extension', 'as_attachment', 'auto_sync_enabled',
            'data_synced',
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )


class SavedFilterFilterSet(ChangeLoggedModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    object_type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ObjectType.objects.all(),
        field_name='object_types'
    )
    object_type = ContentTypeFilter(
        field_name='object_types'
    )
    user_id = django_filters.ModelMultipleChoiceFilter(
        queryset=get_user_model().objects.all(),
        label=_('User (ID)'),
    )
    user = django_filters.ModelMultipleChoiceFilter(
        field_name='user__username',
        queryset=get_user_model().objects.all(),
        to_field_name='username',
        label=_('User (name)'),
    )
    usable = django_filters.BooleanFilter(
        method='_usable'
    )

    class Meta:
        model = SavedFilter
        fields = ('id', 'name', 'slug', 'description', 'enabled', 'shared', 'weight')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )

    def _usable(self, queryset, name, value):
        """
        Return only SavedFilters that are both enabled and are shared (or belong to the current user).
        """
        user = self.request.user if self.request else None
        if not user or user.is_anonymous:
            if value:
                return queryset.filter(enabled=True, shared=True)
            return queryset.filter(Q(enabled=False) | Q(shared=False))
        if value:
            return queryset.filter(enabled=True).filter(Q(shared=True) | Q(user=user))
        return queryset.filter(Q(enabled=False) | Q(Q(shared=False) & ~Q(user=user)))


class BookmarkFilterSet(BaseFilterSet):
    created = django_filters.DateTimeFilter()
    object_type_id = MultiValueNumberFilter()
    object_type = ContentTypeFilter()
    user_id = django_filters.ModelMultipleChoiceFilter(
        queryset=get_user_model().objects.all(),
        label=_('User (ID)'),
    )
    user = django_filters.ModelMultipleChoiceFilter(
        field_name='user__username',
        queryset=get_user_model().objects.all(),
        to_field_name='username',
        label=_('User (name)'),
    )

    class Meta:
        model = Bookmark
        fields = ('id', 'object_id')


class ImageAttachmentFilterSet(ChangeLoggedModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    object_type = ContentTypeFilter()

    class Meta:
        model = ImageAttachment
        fields = ('id', 'object_type_id', 'object_id', 'name', 'image_width', 'image_height')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(name__icontains=value)


class JournalEntryFilterSet(NetBoxModelFilterSet):
    created = django_filters.DateTimeFromToRangeFilter()
    assigned_object_type = ContentTypeFilter()
    assigned_object_type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ContentType.objects.all()
    )
    created_by_id = django_filters.ModelMultipleChoiceFilter(
        queryset=get_user_model().objects.all(),
        label=_('User (ID)'),
    )
    created_by = django_filters.ModelMultipleChoiceFilter(
        field_name='created_by__username',
        queryset=get_user_model().objects.all(),
        to_field_name='username',
        label=_('User (name)'),
    )
    kind = django_filters.MultipleChoiceFilter(
        choices=JournalEntryKindChoices
    )

    class Meta:
        model = JournalEntry
        fields = ('id', 'assigned_object_type_id', 'assigned_object_id', 'created', 'kind')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(comments__icontains=value)


class TagFilterSet(ChangeLoggedModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    content_type = MultiValueCharFilter(
        method='_content_type'
    )
    content_type_id = MultiValueNumberFilter(
        method='_content_type_id'
    )
    for_object_type_id = MultiValueNumberFilter(
        method='_for_object_type'
    )

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color', 'description', 'object_types')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(slug__icontains=value) |
            Q(description__icontains=value)
        )

    def _content_type(self, queryset, name, values):
        ct_filter = Q()

        # Compile list of app_label & model pairings
        for value in values:
            try:
                app_label, model = value.lower().split('.')
                ct_filter |= Q(
                    app_label=app_label,
                    model=model
                )
            except ValueError:
                pass

        # Get ContentType instances
        content_types = ContentType.objects.filter(ct_filter)

        return queryset.filter(extras_taggeditem_items__content_type__in=content_types).distinct()

    def _content_type_id(self, queryset, name, values):

        # Get ContentType instances
        content_types = ContentType.objects.filter(pk__in=values)

        return queryset.filter(extras_taggeditem_items__content_type__in=content_types).distinct()

    def _for_object_type(self, queryset, name, values):
        return queryset.filter(
            Q(object_types__id__in=values) | Q(object_types__isnull=True)
        )


class ConfigContextFilterSet(ChangeLoggedModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    region_id = django_filters.ModelMultipleChoiceFilter(
        field_name='regions',
        queryset=Region.objects.all(),
        label=_('Region'),
    )
    region = django_filters.ModelMultipleChoiceFilter(
        field_name='regions__slug',
        queryset=Region.objects.all(),
        to_field_name='slug',
        label=_('Region (slug)'),
    )
    site_group = django_filters.ModelMultipleChoiceFilter(
        field_name='site_groups__slug',
        queryset=SiteGroup.objects.all(),
        to_field_name='slug',
        label=_('Site group (slug)'),
    )
    site_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='site_groups',
        queryset=SiteGroup.objects.all(),
        label=_('Site group'),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='sites',
        queryset=Site.objects.all(),
        label=_('Site'),
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='sites__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label=_('Site (slug)'),
    )
    location_id = django_filters.ModelMultipleChoiceFilter(
        field_name='locations',
        queryset=Location.objects.all(),
        label=_('Location'),
    )
    location = django_filters.ModelMultipleChoiceFilter(
        field_name='locations__slug',
        queryset=Location.objects.all(),
        to_field_name='slug',
        label=_('Location (slug)'),
    )
    device_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device_types',
        queryset=DeviceType.objects.all(),
        label=_('Device type'),
    )
    device_role_id = django_filters.ModelMultipleChoiceFilter(
        field_name='roles',
        queryset=DeviceRole.objects.all(),
        label=_('Role'),
    )
    device_role = django_filters.ModelMultipleChoiceFilter(
        field_name='roles__slug',
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        label=_('Role (slug)'),
    )
    platform_id = django_filters.ModelMultipleChoiceFilter(
        field_name='platforms',
        queryset=Platform.objects.all(),
        label=_('Platform'),
    )
    platform = django_filters.ModelMultipleChoiceFilter(
        field_name='platforms__slug',
        queryset=Platform.objects.all(),
        to_field_name='slug',
        label=_('Platform (slug)'),
    )
    cluster_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster_types',
        queryset=ClusterType.objects.all(),
        label=_('Cluster type'),
    )
    cluster_type = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster_types__slug',
        queryset=ClusterType.objects.all(),
        to_field_name='slug',
        label=_('Cluster type (slug)'),
    )
    cluster_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster_groups',
        queryset=ClusterGroup.objects.all(),
        label=_('Cluster group'),
    )
    cluster_group = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster_groups__slug',
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        label=_('Cluster group (slug)'),
    )
    cluster_id = django_filters.ModelMultipleChoiceFilter(
        field_name='clusters',
        queryset=Cluster.objects.all(),
        label=_('Cluster'),
    )
    tenant_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='tenant_groups',
        queryset=TenantGroup.objects.all(),
        label=_('Tenant group'),
    )
    tenant_group = django_filters.ModelMultipleChoiceFilter(
        field_name='tenant_groups__slug',
        queryset=TenantGroup.objects.all(),
        to_field_name='slug',
        label=_('Tenant group (slug)'),
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name='tenants',
        queryset=Tenant.objects.all(),
        label=_('Tenant'),
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        field_name='tenants__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label=_('Tenant (slug)'),
    )
    tag_id = django_filters.ModelMultipleChoiceFilter(
        field_name='tags',
        queryset=Tag.objects.all(),
        label=_('Tag'),
    )
    tag = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
        label=_('Tag (slug)'),
    )
    data_source_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DataSource.objects.all(),
        label=_('Data source (ID)'),
    )
    data_file_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DataSource.objects.all(),
        label=_('Data file (ID)'),
    )

    # TODO: Remove in v4.1
    role = device_role
    role_id = device_role_id

    class Meta:
        model = ConfigContext
        fields = ('id', 'name', 'is_active', 'description', 'weight', 'auto_sync_enabled', 'data_synced')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(data__icontains=value)
        )


class ConfigTemplateFilterSet(ChangeLoggedModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    data_source_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DataSource.objects.all(),
        label=_('Data source (ID)'),
    )
    data_file_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DataSource.objects.all(),
        label=_('Data file (ID)'),
    )
    tag = TagFilter()

    class Meta:
        model = ConfigTemplate
        fields = ('id', 'name', 'description', 'auto_sync_enabled', 'data_synced')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )


#
# Filter for Local Config Context Data
#

class LocalConfigContextFilterSet(django_filters.FilterSet):
    local_context_data = django_filters.BooleanFilter(
        method='_local_context_data',
        label=_('Has local config context data'),
    )

    def _local_context_data(self, queryset, name, value):
        return queryset.exclude(local_context_data__isnull=value)


class ObjectChangeFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    time = django_filters.DateTimeFromToRangeFilter()
    changed_object_type = ContentTypeFilter()
    changed_object_type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ContentType.objects.all()
    )
    user_id = django_filters.ModelMultipleChoiceFilter(
        queryset=get_user_model().objects.all(),
        label=_('User (ID)'),
    )
    user = django_filters.ModelMultipleChoiceFilter(
        field_name='user__username',
        queryset=get_user_model().objects.all(),
        to_field_name='username',
        label=_('User name'),
    )

    class Meta:
        model = ObjectChange
        fields = (
            'id', 'user', 'user_name', 'request_id', 'action', 'changed_object_type_id', 'changed_object_id',
            'related_object_type', 'related_object_id', 'object_repr',
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(user_name__icontains=value) |
            Q(object_repr__icontains=value)
        )


#
# ContentTypes
#

class ObjectTypeFilterSet(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )

    class Meta:
        model = ObjectType
        fields = ('id', 'app_label', 'model')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(app_label__icontains=value) |
            Q(model__icontains=value)
        )
