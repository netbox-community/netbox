import django_filters
from django.db.models import Q

from dcim.models import DeviceRole, Interface, Platform, Region, Site
from extras.filters import CustomFieldFilterSet, CreatedUpdatedFilterSet, LocalConfigContextFilterSet
from tenancy.filters import TenancyFilterSet
from tenancy.models import Tenant
from utilities.filters import (
    MultiValueMACAddressFilter, NameSlugSearchFilterSet, NumericInFilter, TagFilter, TreeNodeMultipleChoiceFilter,
)
from .choices import *
from .models import Cluster, ClusterGroup, ClusterType, VirtualMachine

__all__ = (
    'ClusterFilterSet',
    'ClusterGroupFilterSet',
    'ClusterTypeFilterSet',
    'InterfaceFilterSet',
    'VirtualMachineFilterSet',
)


class ClusterTypeFilterSet(NameSlugSearchFilterSet):

    class Meta:
        model = ClusterType
        fields = ['id', 'name', 'slug']


class ClusterGroupFilterSet(NameSlugSearchFilterSet):

    class Meta:
        model = ClusterGroup
        fields = ['id', 'name', 'slug']


class ClusterFilterSet(TenancyFilterSet, CustomFieldFilterSet, CreatedUpdatedFilterSet):
    id__in = NumericInFilter(
        field_name='id',
        lookup_expr='in'
    )
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region__in',
        label='Region (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region__in',
        to_field_name='slug',
        label='Region (slug)',
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
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ClusterGroup.objects.all(),
        label='Parent group (ID)',
    )
    group = django_filters.ModelMultipleChoiceFilter(
        field_name='group__slug',
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        label='Parent group (slug)',
    )
    type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ClusterType.objects.all(),
        label='Cluster type (ID)',
    )
    type = django_filters.ModelMultipleChoiceFilter(
        field_name='type__slug',
        queryset=ClusterType.objects.all(),
        to_field_name='slug',
        label='Cluster type (slug)',
    )
    tag = TagFilter()

    class Meta:
        model = Cluster
        fields = ['name']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(comments__icontains=value)
        )


class VirtualMachineFilterSet(
    LocalConfigContextFilterSet,
    TenancyFilterSet,
    CustomFieldFilterSet,
    CreatedUpdatedFilterSet
):
    id__in = NumericInFilter(
        field_name='id',
        lookup_expr='in'
    )
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=VirtualMachineStatusChoices,
        null_value=None
    )
    cluster_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__group',
        queryset=ClusterGroup.objects.all(),
        label='Cluster group (ID)',
    )
    cluster_group = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__group__slug',
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        label='Cluster group (slug)',
    )
    cluster_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__type',
        queryset=ClusterType.objects.all(),
        label='Cluster type (ID)',
    )
    cluster_type = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__type__slug',
        queryset=ClusterType.objects.all(),
        to_field_name='slug',
        label='Cluster type (slug)',
    )
    cluster_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Cluster.objects.all(),
        label='Cluster (ID)',
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='cluster__site__region__in',
        label='Region (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='cluster__site__region__in',
        to_field_name='slug',
        label='Region (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DeviceRole.objects.all(),
        label='Role (ID)',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='role__slug',
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        label='Role (slug)',
    )
    platform_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Platform.objects.all(),
        label='Platform (ID)',
    )
    platform = django_filters.ModelMultipleChoiceFilter(
        field_name='platform__slug',
        queryset=Platform.objects.all(),
        to_field_name='slug',
        label='Platform (slug)',
    )
    mac_address = MultiValueMACAddressFilter(
        field_name='interfaces__mac_address',
        label='MAC address',
    )
    tag = TagFilter()

    class Meta:
        model = VirtualMachine
        fields = ['id', 'name', 'cluster', 'vcpus', 'memory', 'disk']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(comments__icontains=value)
        )


class InterfaceFilterSet(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    virtual_machine_id = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_machine',
        queryset=VirtualMachine.objects.all(),
        label='Virtual machine (ID)',
    )
    virtual_machine = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_machine__name',
        queryset=VirtualMachine.objects.all(),
        to_field_name='name',
        label='Virtual machine',
    )
    mac_address = MultiValueMACAddressFilter(
        label='MAC address',
    )

    class Meta:
        model = Interface
        fields = ['id', 'name', 'enabled', 'mtu']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
        )
