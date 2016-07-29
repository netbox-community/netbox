import django_filters

from django.db.models import Q

from dcim.models import Site
from tenancy.models import Tenant
from .models import Provider, Circuit, CircuitType


class ProviderFilter(django_filters.FilterSet):
    q = django_filters.MethodFilter(
        action='search',
        label='Search',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        name='circuits__site',
        queryset=Site.objects.all(),
        label='Site',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        name='circuits__site',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )

    class Meta:
        model = Provider
        fields = ['q', 'name', 'account', 'asn']

    def search(self, queryset, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(account__icontains=value) |
            Q(comments__icontains=value)
        )


class CircuitFilter(django_filters.FilterSet):
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
        name='provider',
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
        name='type',
        queryset=CircuitType.objects.all(),
        to_field_name='slug',
        label='Circuit type (slug)',
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        name='tenant',
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        name='tenant',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        name='site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        name='site',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )

    class Meta:
        model = Circuit
        fields = ['q', 'provider_id', 'provider', 'type_id', 'type', 'site_id', 'site', 'interface', 'install_date']

    def search(self, queryset, value):
        return queryset.filter(
            Q(cid__icontains=value) |
            Q(xconnect_id__icontains=value) |
            Q(pp_info__icontains=value) |
            Q(comments__icontains=value)
        )
