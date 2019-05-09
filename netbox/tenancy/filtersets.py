import django_filters
from .models import Tenant, TenantGroup


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
