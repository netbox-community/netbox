from datetime import date
from typing import Annotated, TYPE_CHECKING

import netaddr
import strawberry
import strawberry_django
from django.db.models import Q
from netaddr.core import AddrFormatError
from strawberry.scalars import ID
from strawberry_django import FilterLookup, DateFilterLookup

from core.graphql.filter_mixins_v1 import BaseObjectTypeFilterMixinV1, ChangeLogFilterMixinV1
from dcim.graphql.filter_mixins_v1 import ScopedFilterMixinV1
from dcim.models import Device
from ipam import models
from ipam.graphql.filter_mixins_v1 import ServiceBaseFilterMixinV1
from netbox.graphql.filter_mixins_v1 import (
    NetBoxModelFilterMixinV1, OrganizationalModelFilterMixinV1, PrimaryModelFilterMixinV1
)
from tenancy.graphql.filter_mixins_v1 import ContactFilterMixinV1, TenancyFilterMixinV1
from virtualization.models import VMInterface

if TYPE_CHECKING:
    from netbox.graphql.filter_lookups import IntegerLookup, IntegerRangeArrayLookup
    from circuits.graphql.filters_v1 import ProviderFilterV1
    from core.graphql.filters_v1 import ContentTypeFilterV1
    from dcim.graphql.filters_v1 import SiteFilterV1
    from vpn.graphql.filters_v1 import L2VPNFilterV1
    from .enums import *

__all__ = (
    'ASNFilterV1',
    'ASNRangeFilterV1',
    'AggregateFilterV1',
    'FHRPGroupFilterV1',
    'FHRPGroupAssignmentFilterV1',
    'IPAddressFilterV1',
    'IPRangeFilterV1',
    'PrefixFilterV1',
    'RIRFilterV1',
    'RoleFilterV1',
    'RouteTargetFilterV1',
    'ServiceFilterV1',
    'ServiceTemplateFilterV1',
    'VLANFilterV1',
    'VLANGroupFilterV1',
    'VLANTranslationPolicyFilterV1',
    'VLANTranslationRuleFilterV1',
    'VRFFilterV1',
)


@strawberry_django.filter_type(models.ASN, lookups=True)
class ASNFilterV1(TenancyFilterMixinV1, PrimaryModelFilterMixinV1):
    rir: Annotated['RIRFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = strawberry_django.filter_field()
    rir_id: ID | None = strawberry_django.filter_field()
    asn: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    sites: (
        Annotated['SiteFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()
    providers: (
        Annotated['ProviderFilterV1', strawberry.lazy('circuits.graphql.filters_v1')] | None
    ) = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ASNRange, lookups=True)
class ASNRangeFilterV1(TenancyFilterMixinV1, OrganizationalModelFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    rir: Annotated['RIRFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = strawberry_django.filter_field()
    rir_id: ID | None = strawberry_django.filter_field()
    start: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    end: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.Aggregate, lookups=True)
class AggregateFilterV1(ContactFilterMixinV1, TenancyFilterMixinV1, PrimaryModelFilterMixinV1):
    prefix: Annotated['PrefixFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    prefix_id: ID | None = strawberry_django.filter_field()
    rir: Annotated['RIRFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = strawberry_django.filter_field()
    rir_id: ID | None = strawberry_django.filter_field()
    date_added: DateFilterLookup[date] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.FHRPGroup, lookups=True)
class FHRPGroupFilterV1(PrimaryModelFilterMixinV1):
    group_id: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    protocol: Annotated['FHRPGroupProtocolEnum', strawberry.lazy('ipam.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    auth_type: Annotated['FHRPGroupAuthTypeEnum', strawberry.lazy('ipam.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    auth_key: FilterLookup[str] | None = strawberry_django.filter_field()
    ip_addresses: Annotated['IPAddressFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.FHRPGroupAssignment, lookups=True)
class FHRPGroupAssignmentFilterV1(BaseObjectTypeFilterMixinV1, ChangeLogFilterMixinV1):
    interface_type: Annotated['ContentTypeFilterV1', strawberry.lazy('core.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    interface_id: FilterLookup[str] | None = strawberry_django.filter_field()
    group: Annotated['FHRPGroupFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    group_id: ID | None = strawberry_django.filter_field()
    priority: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )

    @strawberry_django.filter_field()
    def device_id(self, queryset, value: list[str], prefix) -> Q:
        return self.filter_device('id', value)

    @strawberry_django.filter_field()
    def device(self, value: list[str], prefix) -> Q:
        return self.filter_device('name', value)

    @strawberry_django.filter_field()
    def virtual_machine_id(self, value: list[str], prefix) -> Q:
        return Q(interface_id__in=VMInterface.objects.filter(virtual_machine_id__in=value))

    @strawberry_django.filter_field()
    def virtual_machine(self, value: list[str], prefix) -> Q:
        return Q(interface_id__in=VMInterface.objects.filter(virtual_machine__name__in=value))

    def filter_device(self, field, value) -> Q:
        """Helper to standardize logic for device and device_id filters"""
        devices = Device.objects.filter(**{f'{field}__in': value})
        interface_ids = []
        for device in devices:
            interface_ids.extend(device.vc_interfaces().values_list('id', flat=True))
        return Q(interface_id__in=interface_ids)


@strawberry_django.filter_type(models.IPAddress, lookups=True)
class IPAddressFilterV1(ContactFilterMixinV1, TenancyFilterMixinV1, PrimaryModelFilterMixinV1):
    address: FilterLookup[str] | None = strawberry_django.filter_field()
    vrf: Annotated['VRFFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = strawberry_django.filter_field()
    vrf_id: ID | None = strawberry_django.filter_field()
    status: Annotated['IPAddressStatusEnum', strawberry.lazy('ipam.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    role: Annotated['IPAddressRoleEnum', strawberry.lazy('ipam.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    assigned_object_type: Annotated['ContentTypeFilterV1', strawberry.lazy('core.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    assigned_object_id: ID | None = strawberry_django.filter_field()
    nat_inside: Annotated['IPAddressFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    nat_inside_id: ID | None = strawberry_django.filter_field()
    nat_outside: Annotated['IPAddressFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    nat_outside_id: ID | None = strawberry_django.filter_field()
    dns_name: FilterLookup[str] | None = strawberry_django.filter_field()

    @strawberry_django.filter_field()
    def assigned(self, value: bool, prefix) -> Q:
        return Q(assigned_object_id__isnull=(not value))

    @strawberry_django.filter_field()
    def parent(self, value: list[str], prefix) -> Q:
        if not value:
            return Q()
        q = Q()
        for subnet in value:
            try:
                query = str(netaddr.IPNetwork(subnet.strip()).cidr)
                q |= Q(address__net_host_contained=query)
            except (AddrFormatError, ValueError):
                return Q()
        return q

    @strawberry_django.filter_field()
    def family(
        self,
        value: Annotated['IPAddressFamilyEnum', strawberry.lazy('ipam.graphql.enums')],
        prefix,
    ) -> Q:
        return Q(**{f"{prefix}address__family": value.value})


@strawberry_django.filter_type(models.IPRange, lookups=True)
class IPRangeFilterV1(ContactFilterMixinV1, TenancyFilterMixinV1, PrimaryModelFilterMixinV1):
    start_address: FilterLookup[str] | None = strawberry_django.filter_field()
    end_address: FilterLookup[str] | None = strawberry_django.filter_field()
    size: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    vrf: Annotated['VRFFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = strawberry_django.filter_field()
    vrf_id: ID | None = strawberry_django.filter_field()
    status: Annotated['IPRangeStatusEnum', strawberry.lazy('ipam.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    role: Annotated['RoleFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    mark_utilized: FilterLookup[bool] | None = strawberry_django.filter_field()

    @strawberry_django.filter_field()
    def parent(self, value: list[str], prefix) -> Q:
        if not value:
            return Q()
        q = Q()
        for subnet in value:
            try:
                query = str(netaddr.IPNetwork(subnet.strip()).cidr)
                q |= Q(start_address__net_host_contained=query, end_address__net_host_contained=query)
            except (AddrFormatError, ValueError):
                return Q()
        return q

    @strawberry_django.filter_field()
    def contains(self, value: list[str], prefix) -> Q:
        if not value:
            return Q()
        q = Q()
        for subnet in value:
            net = netaddr.IPNetwork(subnet.strip())
            q |= Q(
                start_address__host__inet__lte=str(netaddr.IPAddress(net.first)),
                end_address__host__inet__gte=str(netaddr.IPAddress(net.last)),
            )
        return q


@strawberry_django.filter_type(models.Prefix, lookups=True)
class PrefixFilterV1(ContactFilterMixinV1, ScopedFilterMixinV1, TenancyFilterMixinV1, PrimaryModelFilterMixinV1):
    prefix: FilterLookup[str] | None = strawberry_django.filter_field()
    vrf: Annotated['VRFFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = strawberry_django.filter_field()
    vrf_id: ID | None = strawberry_django.filter_field()
    vlan: Annotated['VLANFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    vlan_id: ID | None = strawberry_django.filter_field()
    status: Annotated['PrefixStatusEnum', strawberry.lazy('ipam.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    role: Annotated['RoleFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    role_id: ID | None = strawberry_django.filter_field()
    is_pool: FilterLookup[bool] | None = strawberry_django.filter_field()
    mark_utilized: FilterLookup[bool] | None = strawberry_django.filter_field()

    @strawberry_django.filter_field()
    def contains(self, value: list[str], prefix) -> Q:
        if not value:
            return Q()
        q = Q()
        for subnet in value:
            query = str(netaddr.IPNetwork(subnet.strip()).cidr)
            q |= Q(prefix__net_contains=query)
        return q


@strawberry_django.filter_type(models.RIR, lookups=True)
class RIRFilterV1(OrganizationalModelFilterMixinV1):
    is_private: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.Role, lookups=True)
class RoleFilterV1(OrganizationalModelFilterMixinV1):
    weight: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.RouteTarget, lookups=True)
class RouteTargetFilterV1(TenancyFilterMixinV1, PrimaryModelFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    importing_vrfs: Annotated['VRFFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    exporting_vrfs: Annotated['VRFFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    importing_l2vpns: Annotated['L2VPNFilterV1', strawberry.lazy('vpn.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    exporting_l2vpns: Annotated['L2VPNFilterV1', strawberry.lazy('vpn.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.Service, lookups=True)
class ServiceFilterV1(ContactFilterMixinV1, ServiceBaseFilterMixinV1, PrimaryModelFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    ip_addresses: Annotated['IPAddressFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    parent_object_type: Annotated['ContentTypeFilterV1', strawberry.lazy('core.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    parent_object_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ServiceTemplate, lookups=True)
class ServiceTemplateFilterV1(ServiceBaseFilterMixinV1, PrimaryModelFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.VLAN, lookups=True)
class VLANFilterV1(TenancyFilterMixinV1, PrimaryModelFilterMixinV1):
    site: Annotated['SiteFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    site_id: ID | None = strawberry_django.filter_field()
    group: Annotated['VLANGroupFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    group_id: ID | None = strawberry_django.filter_field()
    vid: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    status: Annotated['VLANStatusEnum', strawberry.lazy('ipam.graphql.enums')] | None = strawberry_django.filter_field()
    role: Annotated['RoleFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    role_id: ID | None = strawberry_django.filter_field()
    qinq_svlan: Annotated['VLANFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    qinq_svlan_id: ID | None = strawberry_django.filter_field()
    qinq_cvlans: Annotated['VLANFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    qinq_role: Annotated['VLANQinQRoleEnum', strawberry.lazy('ipam.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    l2vpn_terminations: Annotated['L2VPNFilterV1', strawberry.lazy('vpn.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.VLANGroup, lookups=True)
class VLANGroupFilterV1(ScopedFilterMixinV1, OrganizationalModelFilterMixinV1):
    vid_ranges: Annotated['IntegerRangeArrayLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.VLANTranslationPolicy, lookups=True)
class VLANTranslationPolicyFilterV1(PrimaryModelFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.VLANTranslationRule, lookups=True)
class VLANTranslationRuleFilterV1(NetBoxModelFilterMixinV1):
    policy: Annotated['VLANTranslationPolicyFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    policy_id: ID | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    local_vid: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    remote_vid: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.VRF, lookups=True)
class VRFFilterV1(TenancyFilterMixinV1, PrimaryModelFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    rd: FilterLookup[str] | None = strawberry_django.filter_field()
    enforce_unique: FilterLookup[bool] | None = strawberry_django.filter_field()
    import_targets: Annotated['RouteTargetFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    export_targets: Annotated['RouteTargetFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
