import django_filters
from django.db.models import Q

from extras.filters import CustomFieldFilterSet
from utilities.filters import NameSlugSearchFilterSet, NumericInFilter, TagFilter
from .models import Tenant, TenantGroup


class TenantGroupFilter(NameSlugSearchFilterSet):

    class Meta:
        model = TenantGroup
        fields = ['name', 'slug']


class TenantFilter(CustomFieldFilterSet, django_filters.FilterSet):
    id__in = NumericInFilter(
        field_name='id',
        lookup_expr='in'
    )
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=TenantGroup.objects.all(),
        label='Group (ID)',
    )
    group = django_filters.ModelMultipleChoiceFilter(
        field_name='group__slug',
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


class TenancyFilterSet(django_filters.FilterSet):
    tenant_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='tenant__group__id',
        queryset=TenantGroup.objects.all(),
        to_field_name='id',
        label='Tenant Group (ID)',
    )
    tenant_group = django_filters.ModelMultipleChoiceFilter(
        field_name='tenant__group__slug',
        queryset=TenantGroup.objects.all(),
        to_field_name='slug',
        label='Tenant Group (slug)',
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        field_name='tenant__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
