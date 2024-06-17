from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.translation import gettext as _

import django_filters

from netbox.filtersets import BaseFilterSet, ChangeLoggedModelFilterSet, NetBoxModelFilterSet
from netbox.utils import get_data_backend_choices
from utilities.filters import ContentTypeFilter
from .choices import *
from .models import *

__all__ = (
    'ConfigRevisionFilterSet',
    'DataFileFilterSet',
    'DataSourceFilterSet',
    'JobFilterSet',
    'ObjectChangeFilterSet',
)


class DataSourceFilterSet(NetBoxModelFilterSet):
    type = django_filters.MultipleChoiceFilter(
        choices=get_data_backend_choices,
        null_value=None
    )
    status = django_filters.MultipleChoiceFilter(
        choices=DataSourceStatusChoices,
        null_value=None
    )

    class Meta:
        model = DataSource
        fields = ('id', 'name', 'enabled', 'description', 'source_url', 'last_synced')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        )


class DataFileFilterSet(ChangeLoggedModelFilterSet):
    q = django_filters.CharFilter(
        method='search'
    )
    source_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DataSource.objects.all(),
        label=_('Data source (ID)'),
    )
    source = django_filters.ModelMultipleChoiceFilter(
        field_name='source__name',
        queryset=DataSource.objects.all(),
        to_field_name='name',
        label=_('Data source (name)'),
    )

    class Meta:
        model = DataFile
        fields = ('id', 'path', 'last_updated', 'size', 'hash')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(path__icontains=value)
        )


class JobFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    created = django_filters.DateTimeFilter()
    created__before = django_filters.DateTimeFilter(
        field_name='created',
        lookup_expr='lte'
    )
    created__after = django_filters.DateTimeFilter(
        field_name='created',
        lookup_expr='gte'
    )
    scheduled = django_filters.DateTimeFilter()
    scheduled__before = django_filters.DateTimeFilter(
        field_name='scheduled',
        lookup_expr='lte'
    )
    scheduled__after = django_filters.DateTimeFilter(
        field_name='scheduled',
        lookup_expr='gte'
    )
    started = django_filters.DateTimeFilter()
    started__before = django_filters.DateTimeFilter(
        field_name='started',
        lookup_expr='lte'
    )
    started__after = django_filters.DateTimeFilter(
        field_name='started',
        lookup_expr='gte'
    )
    completed = django_filters.DateTimeFilter()
    completed__before = django_filters.DateTimeFilter(
        field_name='completed',
        lookup_expr='lte'
    )
    completed__after = django_filters.DateTimeFilter(
        field_name='completed',
        lookup_expr='gte'
    )
    status = django_filters.MultipleChoiceFilter(
        choices=JobStatusChoices,
        null_value=None
    )

    class Meta:
        model = Job
        fields = ('id', 'object_type', 'object_id', 'name', 'interval', 'status', 'user', 'job_id')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(user__username__icontains=value) |
            Q(name__icontains=value)
        )


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


class ConfigRevisionFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )

    class Meta:
        model = ConfigRevision
        fields = ('id', 'created', 'comment')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(comment__icontains=value)
        )
