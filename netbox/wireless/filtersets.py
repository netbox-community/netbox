import django_filters
from django.db.models import Q

from dcim.choices import LinkStatusChoices
from dcim.models import Interface
from ipam.models import VLAN
from netbox.filtersets import OrganizationalModelFilterSet, NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet
from utilities.filters import MultiValueNumberFilter, TreeNodeMultipleChoiceFilter
from .choices import *
from .models import *

__all__ = (
    'WirelessLANFilterSet',
    'WirelessLANGroupFilterSet',
    'WirelessLinkFilterSet',
)


class WirelessLANGroupFilterSet(OrganizationalModelFilterSet):
    parent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=WirelessLANGroup.objects.all()
    )
    parent = django_filters.ModelMultipleChoiceFilter(
        field_name='parent__slug',
        queryset=WirelessLANGroup.objects.all(),
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
        fields = ['id', 'name', 'slug', 'description']


class WirelessLANFilterSet(NetBoxModelFilterSet, TenancyFilterSet):
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
        choices=WirelessLANStatusChoices
    )
    vlan_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VLAN.objects.all()
    )
    interface_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Interface.objects.all(),
        field_name='interfaces'
    )
    auth_type = django_filters.MultipleChoiceFilter(
        choices=WirelessAuthTypeChoices
    )
    auth_cipher = django_filters.MultipleChoiceFilter(
        choices=WirelessAuthCipherChoices
    )

    class Meta:
        model = WirelessLAN
        fields = ['id', 'ssid', 'auth_psk', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(ssid__icontains=value) |
            Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)


class WirelessLinkFilterSet(NetBoxModelFilterSet, TenancyFilterSet):
    interface_a_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Interface.objects.all()
    )
    interface_b_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Interface.objects.all()
    )
    status = django_filters.MultipleChoiceFilter(
        choices=LinkStatusChoices
    )
    auth_type = django_filters.MultipleChoiceFilter(
        choices=WirelessAuthTypeChoices
    )
    auth_cipher = django_filters.MultipleChoiceFilter(
        choices=WirelessAuthCipherChoices
    )

    class Meta:
        model = WirelessLink
        fields = ['id', 'ssid', 'auth_psk', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(ssid__icontains=value) |
            Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)
