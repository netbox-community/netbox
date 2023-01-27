from django.db.models import Q
from django.utils.translation import gettext as _

import django_filters

from .models import *

__all__ = (
    'DataFileFilterSet',
    'DataSourceFilterSet',
)


class DataSourceFilterSet(django_filters.FilterSet):

    class Meta:
        model = DataSource
        fields = ('id', 'name', 'type', 'enabled', 'status', 'git_branch', 'username')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )


class DataFileFilterSet(django_filters.FilterSet):
    datasource_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DataSource.objects.all(),
        label=_('Data source (ID)'),
    )
    datasource = django_filters.ModelMultipleChoiceFilter(
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
