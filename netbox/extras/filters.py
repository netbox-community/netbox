import django_filters
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.forms import DateField, IntegerField, NullBooleanField

from dcim.models import DeviceRole, DeviceType, Platform, Region, Site, SiteGroup
from tenancy.models import Tenant, TenantGroup
from utilities.filters import BaseFilterSet, ContentTypeFilter
from virtualization.models import Cluster, ClusterGroup
from .choices import *
from .models import *


__all__ = (
    'ConfigContextFilterSet',
    'ContentTypeFilterSet',
    'CreatedUpdatedFilterSet',
    'CustomFieldFilter',
    'CustomLinkFilterSet',
    'CustomFieldModelFilterSet',
    'ExportTemplateFilterSet',
    'ImageAttachmentFilterSet',
    'JournalEntryFilterSet',
    'LocalConfigContextFilterSet',
    'ObjectChangeFilterSet',
    'TagFilterSet',
    'WebhookFilterSet',
)

EXACT_FILTER_TYPES = (
    CustomFieldTypeChoices.TYPE_BOOLEAN,
    CustomFieldTypeChoices.TYPE_DATE,
    CustomFieldTypeChoices.TYPE_INTEGER,
    CustomFieldTypeChoices.TYPE_SELECT,
)


class WebhookFilterSet(BaseFilterSet):
    content_types = ContentTypeFilter()
    http_method = django_filters.MultipleChoiceFilter(
        choices=WebhookHttpMethodChoices
    )

    class Meta:
        model = Webhook
        fields = [
            'id', 'content_types', 'name', 'type_create', 'type_update', 'type_delete', 'payload_url', 'enabled',
            'http_method', 'http_content_type', 'secret', 'ssl_verification', 'ca_file_path',
        ]


class CustomFieldFilter(django_filters.Filter):
    """
    Filter objects by the presence of a CustomFieldValue. The filter's name is used as the CustomField name.
    """
    def __init__(self, custom_field, *args, **kwargs):
        self.custom_field = custom_field

        if custom_field.type == CustomFieldTypeChoices.TYPE_INTEGER:
            self.field_class = IntegerField
        elif custom_field.type == CustomFieldTypeChoices.TYPE_BOOLEAN:
            self.field_class = NullBooleanField
        elif custom_field.type == CustomFieldTypeChoices.TYPE_DATE:
            self.field_class = DateField

        super().__init__(*args, **kwargs)

        self.field_name = f'custom_field_data__{self.field_name}'

        if custom_field.type not in EXACT_FILTER_TYPES:
            if custom_field.filter_logic == CustomFieldFilterLogicChoices.FILTER_LOOSE:
                self.lookup_expr = 'icontains'


class CustomFieldModelFilterSet(django_filters.FilterSet):
    """
    Dynamically add a Filter for each CustomField applicable to the parent model.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        custom_fields = CustomField.objects.filter(
            content_types=ContentType.objects.get_for_model(self._meta.model)
        ).exclude(
            filter_logic=CustomFieldFilterLogicChoices.FILTER_DISABLED
        )
        for cf in custom_fields:
            self.filters['cf_{}'.format(cf.name)] = CustomFieldFilter(field_name=cf.name, custom_field=cf)


class CustomFieldFilterSet(django_filters.FilterSet):

    class Meta:
        model = CustomField
        fields = ['id', 'content_types', 'name', 'required', 'filter_logic', 'weight']


class CustomLinkFilterSet(BaseFilterSet):

    class Meta:
        model = CustomLink
        fields = ['id', 'content_type', 'name', 'link_text', 'link_url', 'weight', 'group_name', 'new_window']


class ExportTemplateFilterSet(BaseFilterSet):

    class Meta:
        model = ExportTemplate
        fields = ['id', 'content_type', 'name']


class ImageAttachmentFilterSet(BaseFilterSet):
    content_type = ContentTypeFilter()

    class Meta:
        model = ImageAttachment
        fields = ['id', 'content_type_id', 'object_id', 'name']


class JournalEntryFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    created = django_filters.DateTimeFromToRangeFilter()
    assigned_object_type = ContentTypeFilter()
    created_by_id = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        label='User (ID)',
    )
    created_by = django_filters.ModelMultipleChoiceFilter(
        field_name='created_by__username',
        queryset=User.objects.all(),
        to_field_name='username',
        label='User (name)',
    )
    kind = django_filters.MultipleChoiceFilter(
        choices=JournalEntryKindChoices
    )

    class Meta:
        model = JournalEntry
        fields = ['id', 'assigned_object_type_id', 'assigned_object_id', 'created', 'kind']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(comments__icontains=value)


class TagFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'color']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(slug__icontains=value)
        )


class ConfigContextFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    region_id = django_filters.ModelMultipleChoiceFilter(
        field_name='regions',
        queryset=Region.objects.all(),
        label='Region',
    )
    region = django_filters.ModelMultipleChoiceFilter(
        field_name='regions__slug',
        queryset=Region.objects.all(),
        to_field_name='slug',
        label='Region (slug)',
    )
    site_group = django_filters.ModelMultipleChoiceFilter(
        field_name='site_groups__slug',
        queryset=SiteGroup.objects.all(),
        to_field_name='slug',
        label='Site group (slug)',
    )
    site_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='site_groups',
        queryset=SiteGroup.objects.all(),
        label='Site group',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='sites',
        queryset=Site.objects.all(),
        label='Site',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='sites__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )
    device_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device_types',
        queryset=DeviceType.objects.all(),
        label='Device type',
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        field_name='roles',
        queryset=DeviceRole.objects.all(),
        label='Role',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='roles__slug',
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        label='Role (slug)',
    )
    platform_id = django_filters.ModelMultipleChoiceFilter(
        field_name='platforms',
        queryset=Platform.objects.all(),
        label='Platform',
    )
    platform = django_filters.ModelMultipleChoiceFilter(
        field_name='platforms__slug',
        queryset=Platform.objects.all(),
        to_field_name='slug',
        label='Platform (slug)',
    )
    cluster_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster_groups',
        queryset=ClusterGroup.objects.all(),
        label='Cluster group',
    )
    cluster_group = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster_groups__slug',
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        label='Cluster group (slug)',
    )
    cluster_id = django_filters.ModelMultipleChoiceFilter(
        field_name='clusters',
        queryset=Cluster.objects.all(),
        label='Cluster',
    )
    tenant_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='tenant_groups',
        queryset=TenantGroup.objects.all(),
        label='Tenant group',
    )
    tenant_group = django_filters.ModelMultipleChoiceFilter(
        field_name='tenant_groups__slug',
        queryset=TenantGroup.objects.all(),
        to_field_name='slug',
        label='Tenant group (slug)',
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name='tenants',
        queryset=Tenant.objects.all(),
        label='Tenant',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        field_name='tenants__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    tag = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
        label='Tag (slug)',
    )

    class Meta:
        model = ConfigContext
        fields = ['id', 'name', 'is_active']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(data__icontains=value)
        )


#
# Filter for Local Config Context Data
#

class LocalConfigContextFilterSet(django_filters.FilterSet):
    local_context_data = django_filters.BooleanFilter(
        method='_local_context_data',
        label='Has local config context data',
    )

    def _local_context_data(self, queryset, name, value):
        return queryset.exclude(local_context_data__isnull=value)


class ObjectChangeFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    time = django_filters.DateTimeFromToRangeFilter()
    changed_object_type = ContentTypeFilter()
    user_id = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        label='User (ID)',
    )
    user = django_filters.ModelMultipleChoiceFilter(
        field_name='user__username',
        queryset=User.objects.all(),
        to_field_name='username',
        label='User name',
    )

    class Meta:
        model = ObjectChange
        fields = [
            'id', 'user', 'user_name', 'request_id', 'action', 'changed_object_type_id', 'changed_object_id',
            'object_repr',
        ]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(user_name__icontains=value) |
            Q(object_repr__icontains=value)
        )


class CreatedUpdatedFilterSet(django_filters.FilterSet):
    created = django_filters.DateFilter()
    created__gte = django_filters.DateFilter(
        field_name='created',
        lookup_expr='gte'
    )
    created__lte = django_filters.DateFilter(
        field_name='created',
        lookup_expr='lte'
    )
    last_updated = django_filters.DateTimeFilter()
    last_updated__gte = django_filters.DateTimeFilter(
        field_name='last_updated',
        lookup_expr='gte'
    )
    last_updated__lte = django_filters.DateTimeFilter(
        field_name='last_updated',
        lookup_expr='lte'
    )


#
# Job Results
#

class JobResultFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    created = django_filters.DateTimeFilter()
    completed = django_filters.DateTimeFilter()
    status = django_filters.MultipleChoiceFilter(
        choices=JobResultStatusChoices,
        null_value=None
    )

    class Meta:
        model = JobResult
        fields = [
            'id', 'created', 'completed', 'status', 'user', 'obj_type', 'name'
        ]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(user__username__icontains=value)
        )


#
# ContentTypes
#

class ContentTypeFilterSet(django_filters.FilterSet):

    class Meta:
        model = ContentType
        fields = ['id', 'app_label', 'model']
