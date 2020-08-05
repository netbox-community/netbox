import django_filters
from django.db.models import Q
from django.utils.translation import gettext as _

from dcim.models import DeviceRole, Interface, Platform, Region, Site
from extras.filters import CustomFieldFilterSet, CreatedUpdatedFilterSet, LocalConfigContextFilterSet
from tenancy.filters import TenancyFilterSet
from utilities.filters import (
    BaseFilterSet, MultiValueMACAddressFilter, NameSlugSearchFilterSet, TagFilter,
    TreeNodeMultipleChoiceFilter,
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


class ClusterTypeFilterSet(BaseFilterSet, NameSlugSearchFilterSet):

    class Meta:
        model = ClusterType
        fields = ['id', 'name', 'slug', 'description']


class ClusterGroupFilterSet(BaseFilterSet, NameSlugSearchFilterSet):

    class Meta:
        model = ClusterGroup
        fields = ['id', 'name', 'slug', 'description']


class ClusterFilterSet(BaseFilterSet, TenancyFilterSet, CustomFieldFilterSet, CreatedUpdatedFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label=_('Site (ID)'),
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label=_('Site (slug)'),
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ClusterGroup.objects.all(),
        label=_('Parent group (ID)'),
    )
    group = django_filters.ModelMultipleChoiceFilter(
        field_name='group__slug',
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        label=_('Parent group (slug)'),
    )
    type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ClusterType.objects.all(),
        label=_('Cluster type (ID)'),
    )
    type = django_filters.ModelMultipleChoiceFilter(
        field_name='type__slug',
        queryset=ClusterType.objects.all(),
        to_field_name='slug',
        label=_('Cluster type (slug)'),
    )
    tag = TagFilter()

    class Meta:
        model = Cluster
        fields = ['id', 'name']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(comments__icontains=value)
        )


class VirtualMachineFilterSet(
    BaseFilterSet,
    LocalConfigContextFilterSet,
    TenancyFilterSet,
    CustomFieldFilterSet,
    CreatedUpdatedFilterSet
):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    status = django_filters.MultipleChoiceFilter(
        choices=VirtualMachineStatusChoices,
        null_value=None
    )
    cluster_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__group',
        queryset=ClusterGroup.objects.all(),
        label=_('Cluster group (ID)'),
    )
    cluster_group = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__group__slug',
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        label=_('Cluster group (slug)'),
    )
    cluster_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__type',
        queryset=ClusterType.objects.all(),
        label=_('Cluster type (ID)'),
    )
    cluster_type = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__type__slug',
        queryset=ClusterType.objects.all(),
        to_field_name='slug',
        label=_('Cluster type (slug)'),
    )
    cluster_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Cluster.objects.all(),
        label=_('Cluster (ID)'),
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='cluster__site__region',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='cluster__site__region',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__site',
        queryset=Site.objects.all(),
        label=_('Site (ID)'),
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label=_('Site (slug)'),
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DeviceRole.objects.all(),
        label=_('Role (ID)'),
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='role__slug',
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        label=_('Role (slug)'),
    )
    platform_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Platform.objects.all(),
        label=_('Platform (ID)'),
    )
    platform = django_filters.ModelMultipleChoiceFilter(
        field_name='platform__slug',
        queryset=Platform.objects.all(),
        to_field_name='slug',
        label=_('Platform (slug)'),
    )
    mac_address = MultiValueMACAddressFilter(
        field_name='interfaces__mac_address',
        label=_('MAC address'),
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


class InterfaceFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    virtual_machine_id = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_machine',
        queryset=VirtualMachine.objects.all(),
        label=_('Virtual machine (ID)'),
    )
    virtual_machine = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_machine__name',
        queryset=VirtualMachine.objects.all(),
        to_field_name='name',
        label=_('Virtual machine'),
    )
    mac_address = MultiValueMACAddressFilter(
        label=_('MAC address'),
    )
    tag = TagFilter()

    class Meta:
        model = Interface
        fields = ['id', 'name', 'enabled', 'mtu']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
        )
