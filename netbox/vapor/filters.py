import django_filters
from django.db.models import Q

from extras.filters import TagFilter, CustomFieldFilter
from utilities.filters import MultiValueNumberFilter, MultiValueMACAddressFilter, MultiValueCharFilter
from tenancy.models import Tenant, TenantGroup
from dcim.models import Site, Device, DeviceRole, Interface, Region
from dcim.choices import (
    InterfaceTypeChoices,
)

from netbox_virtual_circuit_plugin.models import VirtualCircuit


class CustomerFilter(CustomFieldFilter):
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

    device_role = django_filters.ModelMultipleChoiceFilter(
        field_name='devices__device_role__slug',
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        label='Device Role (slug)',
    )

    class Meta:
        model = Tenant
        fields = ['id', 'name', 'slug']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(slug__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        )


class InterfaceFilter(django_filters.FilterSet):
    """
    Not using DeviceComponentFilterSet for Interfaces because we need to check for VirtualChassis membership.
    """
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    device = MultiValueCharFilter(
        method='filter_device',
        field_name='name',
        label='Device',
    )
    device_id = MultiValueNumberFilter(
        method='filter_device_id',
        field_name='pk',
        label='Device (ID)',
    )
    device_role = django_filters.ModelMultipleChoiceFilter(
        field_name='device__device_role__slug',
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        label='Device Role (slug)',
    )
    cabled = django_filters.BooleanFilter(
        field_name='cable',
        lookup_expr='isnull',
        exclude=True
    )
    kind = django_filters.CharFilter(
        method='filter_kind',
        label='Kind of interface',
    )
    lag_id = django_filters.ModelMultipleChoiceFilter(
        field_name='lag',
        queryset=Interface.objects.all(),
        label='LAG interface (ID)',
    )
    mac_address = MultiValueMACAddressFilter()
    tag = TagFilter()
    vlan_id = django_filters.CharFilter(
        method='filter_vlan_id',
        label='Assigned VLAN'
    )
    vlan = django_filters.CharFilter(
        method='filter_vlan',
        label='Assigned VID'
    )
    type = django_filters.MultipleChoiceFilter(
        choices=InterfaceTypeChoices,
        null_value=None
    )

    site = django_filters.ModelMultipleChoiceFilter(
        field_name='device__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )

    customer = django_filters.ModelMultipleChoiceFilter(
        field_name='device__tenant__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Customer (slug)',
    )

    market = django_filters.ModelMultipleChoiceFilter(
        field_name='device__site__region__slug',
        queryset=Region.objects.all(),
        to_field_name='slug',
        label='Region (slug)',
    )

    vc_context = django_filters.ModelMultipleChoiceFilter(
        field_name='tagged_vlans__virtual_circuit__virtual_circuit__context',
        queryset=VirtualCircuit.objects.all(),
        to_field_name='context',
        label='Virtual Circuit (context)',
    )

    vc_name = django_filters.ModelMultipleChoiceFilter(
        field_name='tagged_vlans__virtual_circuit__virtual_circuit__name',
        queryset=VirtualCircuit.objects.all(),
        to_field_name='name',
        label='Virtual Circuit (name)',
    )

    vc_id = django_filters.ModelMultipleChoiceFilter(
        field_name='tagged_vlans__virtual_circuit__virtual_circuit__vcid',
        queryset=VirtualCircuit.objects.all(),
        to_field_name='vcid',
        label='Virtual Circuit (vcid)',
    )

    class Meta:
        model = Interface
        fields = ['id', 'name', 'type', 'enabled', 'mtu', 'mgmt_only', 'mode', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        ).distinct()

    def filter_device(self, queryset, name, value):
        try:
            devices = Device.objects.filter(**{'{}__in'.format(name): value})
            vc_interface_ids = []
            for device in devices:
                vc_interface_ids.extend(device.vc_interfaces().values_list('id', flat=True))
            return queryset.filter(pk__in=vc_interface_ids)
        except Device.DoesNotExist:
            return queryset.none()

    def filter_device_id(self, queryset, name, id_list):
        # Include interfaces belonging to peer virtual chassis members
        vc_interface_ids = []
        try:
            devices = Device.objects.filter(pk__in=id_list)
            for device in devices:
                vc_interface_ids += device.vc_interfaces().values_list('id', flat=True)
            return queryset.filter(pk__in=vc_interface_ids)
        except Device.DoesNotExist:
            return queryset.none()

    def filter_vlan_id(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        return queryset.filter(
            Q(untagged_vlan_id=value) |
            Q(tagged_vlans=value)
        )

    def filter_vlan(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        return queryset.filter(
            Q(untagged_vlan_id__vid=value) |
            Q(tagged_vlans__vid=value)
        )

    def filter_kind(self, queryset, name, value):
        value = value.strip().lower()
        return {
            'physical': queryset.exclude(type__in=NONCONNECTABLE_IFACE_TYPES),
            'virtual': queryset.filter(type__in=VIRTUAL_IFACE_TYPES),
            'wireless': queryset.filter(type__in=WIRELESS_IFACE_TYPES),
        }.get(value, queryset.none())
