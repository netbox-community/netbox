import django_filters
from django.db.models import Q

from dcim.base_filtersets import ScopedFilterSet
from dcim.choices import LinkStatusChoices
from dcim.models import Interface
from ipam.models import VLAN
from netbox.filtersets import NestedGroupModelFilterSet, PrimaryModelFilterSet
from tenancy.filtersets import TenancyFilterSet
from utilities.filters import TreeNodeMultipleChoiceFilter
from utilities.filtersets import register_filterset

from .choices import *
from .models import *

__all__ = (
    'WirelessLANFilterSet',
    'WirelessLANGroupFilterSet',
    'WirelessLinkFilterSet',
)


@register_filterset
class WirelessLANGroupFilterSet(NestedGroupModelFilterSet):
    parent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=WirelessLANGroup.objects.all(),
        distinct=False,
    )
    parent = django_filters.ModelMultipleChoiceFilter(
        field_name='parent__slug',
        queryset=WirelessLANGroup.objects.all(),
        distinct=False,
        to_field_name='slug'
    )
    ancestor_id = TreeNodeMultipleChoiceFilter(
        queryset=WirelessLANGroup.objects.all(),
        field_name='parent',
        lookup_expr='in'
    )
    ancestor = TreeNodeMultipleChoiceFilter(
        queryset=WirelessLANGroup.objects.all(),
        field_name='parent',
        lookup_expr='in',
        to_field_name='slug'
    )

    class Meta:
        model = WirelessLANGroup
        fields = ('id', 'name', 'slug', 'description')


@register_filterset
class WirelessLANFilterSet(PrimaryModelFilterSet, ScopedFilterSet, TenancyFilterSet):
    group_id = TreeNodeMultipleChoiceFilter(
        queryset=WirelessLANGroup.objects.all(),
        field_name='group',
        lookup_expr='in'
    )
    group = TreeNodeMultipleChoiceFilter(
        queryset=WirelessLANGroup.objects.all(),
        field_name='group',
        lookup_expr='in',
        to_field_name='slug'
    )
    status = django_filters.MultipleChoiceFilter(
        choices=WirelessLANStatusChoices,
        distinct=False,
    )
    vlan_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VLAN.objects.all(),
        distinct=False,
    )
    interface_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Interface.objects.all(),
        field_name='interfaces'
    )
    auth_type = django_filters.MultipleChoiceFilter(
        choices=WirelessAuthTypeChoices,
        distinct=False,
    )
    auth_cipher = django_filters.MultipleChoiceFilter(
        choices=WirelessAuthCipherChoices,
        distinct=False,
    )

    class Meta:
        model = WirelessLAN
        fields = ('id', 'ssid', 'auth_psk', 'scope_id', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(ssid__icontains=value) |
            Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)


@register_filterset
class WirelessLinkFilterSet(PrimaryModelFilterSet, TenancyFilterSet):
    interface_a_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Interface.objects.all(),
        distinct=False,
    )
    interface_b_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Interface.objects.all(),
        distinct=False,
    )
    status = django_filters.MultipleChoiceFilter(
        choices=LinkStatusChoices,
        distinct=False,
    )
    auth_type = django_filters.MultipleChoiceFilter(
        choices=WirelessAuthTypeChoices,
        distinct=False,
    )
    auth_cipher = django_filters.MultipleChoiceFilter(
        choices=WirelessAuthCipherChoices,
        distinct=False,
    )

    class Meta:
        model = WirelessLink
        fields = ('id', 'ssid', 'auth_psk', 'distance', 'distance_unit', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(ssid__icontains=value) |
            Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)
