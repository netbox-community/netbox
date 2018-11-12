from __future__ import unicode_literals

import django_filters
from django.db.models import Q

from extras.filters import CustomFieldFilterSet
from utilities.filters import NumericInFilter, TagFilter
from .models import Tenant, TenantGroup


class TenantGroupFilter(django_filters.FilterSet):

    class Meta:
        model = TenantGroup
        fields = ['name', 'slug']


class TenantFilter(CustomFieldFilterSet, django_filters.FilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=TenantGroup.objects.all(),
        label='Group (ID)',
    )
    group = django_filters.ModelMultipleChoiceFilter(
        name='group__slug',
        queryset=TenantGroup.objects.all(),
        to_field_name='slug',
        label='Group (slug)',
    )
    tag = TagFilter()

    class Meta:
        model = Tenant
        fields = ['name']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        )
