import django_filters
from django.db.models import Q

from dcim.models import Region, Site
from extras.filters import CustomFieldFilterSet
from tenancy.filtersets import TenancyFilterSet
from utilities.filters import NameSlugSearchFilterSet, NumericInFilter, TagFilter, TreeNodeMultipleChoiceFilter
from .constants import CIRCUIT_STATUS_CHOICES
from .models import Provider, Circuit, CircuitTermination, CircuitType


class ProviderFilter(CustomFieldFilterSet):
    id__in = NumericInFilter(
        field_name='id',
        lookup_expr='in'
    )
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='circuits__terminations__site',
        queryset=Site.objects.all(),
        label='Site',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='circuits__terminations__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )
    tag = TagFilter()

    class Meta:
        model = Provider
        fields = ['name', 'slug', 'asn', 'account']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(account__icontains=value) |
            Q(noc_contact__icontains=value) |
            Q(admin_contact__icontains=value) |
            Q(comments__icontains=value)
        )


class CircuitTypeFilter(NameSlugSearchFilterSet):

    class Meta:
        model = CircuitType
        fields = ['id', 'name', 'slug']


class CircuitFilter(CustomFieldFilterSet, TenancyFilterSet):
    id__in = NumericInFilter(
        field_name='id',
        lookup_expr='in'
    )
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    provider_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Provider.objects.all(),
        label='Provider (ID)',
    )
    provider = django_filters.ModelMultipleChoiceFilter(
        field_name='provider__slug',
        queryset=Provider.objects.all(),
        to_field_name='slug',
        label='Provider (slug)',
    )
    type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=CircuitType.objects.all(),
        label='Circuit type (ID)',
    )
    type = django_filters.ModelMultipleChoiceFilter(
        field_name='type__slug',
        queryset=CircuitType.objects.all(),
        to_field_name='slug',
        label='Circuit type (slug)',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=CIRCUIT_STATUS_CHOICES,
        null_value=None
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='terminations__site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='terminations__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='terminations__site__region__in',
        label='Region (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='terminations__site__region__in',
        to_field_name='slug',
        label='Region (slug)',
    )
    tag = TagFilter()

    class Meta:
        model = Circuit
        fields = ['cid', 'install_date', 'commit_rate']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(cid__icontains=value) |
            Q(terminations__xconnect_id__icontains=value) |
            Q(terminations__pp_info__icontains=value) |
            Q(terminations__description__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        ).distinct()


class CircuitTerminationFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    circuit_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Circuit.objects.all(),
        label='Circuit',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )

    class Meta:
        model = CircuitTermination
        fields = ['term_side', 'port_speed', 'upstream_speed', 'xconnect_id']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(circuit__cid__icontains=value) |
            Q(xconnect_id__icontains=value) |
            Q(pp_info__icontains=value) |
            Q(description__icontains=value)
        ).distinct()
