from datetime import date
from typing import Annotated, TYPE_CHECKING

import netaddr
import strawberry
import strawberry_django
from django.db.models import Q
from netaddr.core import AddrFormatError
from strawberry.scalars import ID
from strawberry_django import FilterLookup, DateFilterLookup

from core.graphql.filter_mixins import BaseObjectTypeFilterMixin, ChangeLogFilterMixin
from dcim.graphql.filter_mixins import ScopedFilterMixin
from dcim.models import Device
from ipam import models
from ipam.graphql.filter_mixins import ServiceBaseFilterMixin
from netbox.graphql.filter_mixins import NetBoxModelFilterMixin, OrganizationalModelFilterMixin, PrimaryModelFilterMixin
from tenancy.graphql.filter_mixins import ContactFilterMixin, TenancyFilterMixin
from virtualization.models import VMInterface

if TYPE_CHECKING:
    from netbox.graphql.filter_lookups import IntegerLookup, IntegerRangeArrayLookup
    from circuits.graphql.filters import ProviderFilter
    from core.graphql.filters import ContentTypeFilter
    from dcim.graphql.filters import SiteFilter
    from vpn.graphql.filters import L2VPNFilter
    from .enums import *

__all__ = (
    'ASNFilter',
    'ASNRangeFilter',
    'AggregateFilter',
    'FHRPGroupFilter',
    'FHRPGroupAssignmentFilter',
    'IPAddressFilter',
    'IPRangeFilter',
    'PrefixFilter',
    'RIRFilter',
    'RoleFilter',
    'RouteTargetFilter',
    'ServiceFilter',
    'ServiceTemplateFilter',
    'VLANFilter',
    'VLANGroupFilter',
    'VLANTranslationPolicyFilter',
    'VLANTranslationRuleFilter',
    'VRFFilter',
)


@strawberry_django.filter_type(models.ASN, lookups=True)
class ASNFilter(TenancyFilterMixin, PrimaryModelFilterMixin):
    rir: Annotated['RIRFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    rir_id: ID | None = strawberry_django.filter_field()
    asn: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    sites: (
        Annotated['SiteFilter', strawberry.lazy('dcim.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    providers: (
        Annotated['ProviderFilter', strawberry.lazy('circuits.graphql.filters')] | None
    ) = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ASNRange, lookups=True)
class ASNRangeFilter(TenancyFilterMixin, OrganizationalModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    rir: Annotated['RIRFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    rir_id: ID | None = strawberry_django.filter_field()
    start: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    end: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.Aggregate, lookups=True)
class AggregateFilter(ContactFilterMixin, TenancyFilterMixin, PrimaryModelFilterMixin):
    prefix: Annotated['PrefixFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    prefix_id: ID | None = strawberry_django.filter_field()
    rir: Annotated['RIRFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    rir_id: ID | None = strawberry_django.filter_field()
    date_added: DateFilterLookup[date] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.FHRPGroup, lookups=True)
class FHRPGroupFilter(PrimaryModelFilterMixin):
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
    ip_addresses: Annotated['IPAddressFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.FHRPGroupAssignment, lookups=True)
class FHRPGroupAssignmentFilter(BaseObjectTypeFilterMixin, ChangeLogFilterMixin):
    interface_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    interface_id: FilterLookup[str] | None = strawberry_django.filter_field()
    group: Annotated['FHRPGroupFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
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
class IPAddressFilter(ContactFilterMixin, TenancyFilterMixin, PrimaryModelFilterMixin):
    address: FilterLookup[str] | None = strawberry_django.filter_field()
    vrf: Annotated['VRFFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    vrf_id: ID | None = strawberry_django.filter_field()
    status: Annotated['IPAddressStatusEnum', strawberry.lazy('ipam.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    role: Annotated['IPAddressRoleEnum', strawberry.lazy('ipam.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    assigned_object_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    assigned_object_id: ID | None = strawberry_django.filter_field()
    nat_inside: Annotated['IPAddressFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    nat_inside_id: ID | None = strawberry_django.filter_field()
    nat_outside: Annotated['IPAddressFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
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
class IPRangeFilter(ContactFilterMixin, TenancyFilterMixin, PrimaryModelFilterMixin):
    start_address: FilterLookup[str] | None = strawberry_django.filter_field()
    end_address: FilterLookup[str] | None = strawberry_django.filter_field()
    size: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    vrf: Annotated['VRFFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    vrf_id: ID | None = strawberry_django.filter_field()
    status: Annotated['IPRangeStatusEnum', strawberry.lazy('ipam.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    role: Annotated['RoleFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
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
class PrefixFilter(ContactFilterMixin, ScopedFilterMixin, TenancyFilterMixin, PrimaryModelFilterMixin):
    prefix: FilterLookup[str] | None = strawberry_django.filter_field()
    vrf: Annotated['VRFFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    vrf_id: ID | None = strawberry_django.filter_field()
    vlan: Annotated['VLANFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    vlan_id: ID | None = strawberry_django.filter_field()
    status: Annotated['PrefixStatusEnum', strawberry.lazy('ipam.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    role: Annotated['RoleFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
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
class RIRFilter(OrganizationalModelFilterMixin):
    is_private: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.Role, lookups=True)
class RoleFilter(OrganizationalModelFilterMixin):
    weight: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.RouteTarget, lookups=True)
class RouteTargetFilter(TenancyFilterMixin, PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    importing_vrfs: Annotated['VRFFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    exporting_vrfs: Annotated['VRFFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    importing_l2vpns: Annotated['L2VPNFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    exporting_l2vpns: Annotated['L2VPNFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.Service, lookups=True)
class ServiceFilter(ContactFilterMixin, ServiceBaseFilterMixin, PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    ip_addresses: Annotated['IPAddressFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    parent_object_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    parent_object_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ServiceTemplate, lookups=True)
class ServiceTemplateFilter(ServiceBaseFilterMixin, PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.VLAN, lookups=True)
class VLANFilter(TenancyFilterMixin, PrimaryModelFilterMixin):
    site: Annotated['SiteFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    site_id: ID | None = strawberry_django.filter_field()
    group: Annotated['VLANGroupFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    group_id: ID | None = strawberry_django.filter_field()
    vid: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    status: Annotated['VLANStatusEnum', strawberry.lazy('ipam.graphql.enums')] | None = strawberry_django.filter_field()
    role: Annotated['RoleFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    role_id: ID | None = strawberry_django.filter_field()
    qinq_svlan: Annotated['VLANFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    qinq_svlan_id: ID | None = strawberry_django.filter_field()
    qinq_cvlans: Annotated['VLANFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    qinq_role: Annotated['VLANQinQRoleEnum', strawberry.lazy('ipam.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    l2vpn_terminations: Annotated['L2VPNFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.VLANGroup, lookups=True)
class VLANGroupFilter(ScopedFilterMixin, OrganizationalModelFilterMixin):
    vid_ranges: Annotated['IntegerRangeArrayLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.VLANTranslationPolicy, lookups=True)
class VLANTranslationPolicyFilter(PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.VLANTranslationRule, lookups=True)
class VLANTranslationRuleFilter(NetBoxModelFilterMixin):
    policy: Annotated['VLANTranslationPolicyFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
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
class VRFFilter(TenancyFilterMixin, PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    rd: FilterLookup[str] | None = strawberry_django.filter_field()
    enforce_unique: FilterLookup[bool] | None = strawberry_django.filter_field()
    import_targets: Annotated['RouteTargetFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    export_targets: Annotated['RouteTargetFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
