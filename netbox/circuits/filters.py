import django_filters

from django.db.models import Q

from dcim.models import Site
from extras.filters import CustomFieldFilterSet
from tenancy.models import Tenant
from utilities.filters import NullableModelMultipleChoiceFilter

from .models import Provider, Circuit, CircuitType


class ProviderFilter(CustomFieldFilterSet, django_filters.FilterSet):
    q = django_filters.MethodFilter(
        action='search',
        label='Search',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        name='circuits__terminations__site',
        queryset=Site.objects.all(),
        label='Site',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        name='circuits__terminations__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )

    class Meta:
        model = Provider
        fields = ['name', 'account', 'asn']

    def search(self, queryset, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(account__icontains=value) |
            Q(comments__icontains=value)
        )


class CircuitFilter(CustomFieldFilterSet, django_filters.FilterSet):
    q = django_filters.MethodFilter(
        action='search',
        label='Search',
    )
    provider_id = django_filters.ModelMultipleChoiceFilter(
        name='provider',
        queryset=Provider.objects.all(),
        label='Provider (ID)',
    )
    provider = django_filters.ModelMultipleChoiceFilter(
        name='provider__slug',
        queryset=Provider.objects.all(),
        to_field_name='slug',
        label='Provider (slug)',
    )
    type_id = django_filters.ModelMultipleChoiceFilter(
        name='type',
        queryset=CircuitType.objects.all(),
        label='Circuit type (ID)',
    )
    type = django_filters.ModelMultipleChoiceFilter(
        name='type__slug',
        queryset=CircuitType.objects.all(),
        to_field_name='slug',
        label='Circuit type (slug)',
    )
    tenant_id = NullableModelMultipleChoiceFilter(
        name='tenant',
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = NullableModelMultipleChoiceFilter(
        name='tenant',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        name='terminations__site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        name='terminations__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )

    class Meta:
        model = Circuit
        fields = ['install_date']

    def search(self, queryset, value):
        return queryset.filter(
            Q(cid__icontains=value) |
            Q(xconnect_id__icontains=value) |
            Q(comments__icontains=value)
        )
