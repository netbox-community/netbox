from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import FilterLookup

from dcim.graphql.filter_mixins import InterfaceBaseFilterMixin, RenderConfigFilterMixin, ScopedFilterMixin
from extras.graphql.filter_mixins import ConfigContextFilterMixin
from netbox.graphql.filter_mixins import (
    ImageAttachmentFilterMixin,
    OrganizationalModelFilterMixin,
    PrimaryModelFilterMixin,
)
from tenancy.graphql.filter_mixins import ContactFilterMixin, TenancyFilterMixin
from virtualization import models
from virtualization.graphql.filter_mixins import VMComponentFilterMixin

if TYPE_CHECKING:
    from .enums import *
    from netbox.graphql.filter_lookups import FloatLookup, IntegerLookup
    from dcim.graphql.filters import DeviceFilter, DeviceRoleFilter, MACAddressFilter, PlatformFilter, SiteFilter
    from ipam.graphql.filters import (
        FHRPGroupAssignmentFilter,
        IPAddressFilter,
        ServiceFilter,
        VLANGroupFilter,
        VRFFilter,
    )
    from vpn.graphql.filters import L2VPNFilter, TunnelTerminationFilter

__all__ = (
    'ClusterFilter',
    'ClusterGroupFilter',
    'ClusterTypeFilter',
    'VirtualMachineFilter',
    'VMInterfaceFilter',
    'VirtualDiskFilter',
)


@strawberry_django.filter_type(models.Cluster, lookups=True)
class ClusterFilter(ContactFilterMixin, ScopedFilterMixin, TenancyFilterMixin, PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    type: Annotated['ClusterTypeFilter', strawberry.lazy('virtualization.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    type_id: ID | None = strawberry_django.filter_field()
    group: Annotated['ClusterGroupFilter', strawberry.lazy('virtualization.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    group_id: ID | None = strawberry_django.filter_field()
    status: Annotated['ClusterStatusEnum', strawberry.lazy('virtualization.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    vlan_groups: Annotated['VLANGroupFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.ClusterGroup, lookups=True)
class ClusterGroupFilter(ContactFilterMixin, OrganizationalModelFilterMixin):
    vlan_groups: Annotated['VLANGroupFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.ClusterType, lookups=True)
class ClusterTypeFilter(OrganizationalModelFilterMixin):
    pass


@strawberry_django.filter_type(models.VirtualMachine, lookups=True)
class VirtualMachineFilter(
    ContactFilterMixin,
    ImageAttachmentFilterMixin,
    RenderConfigFilterMixin,
    ConfigContextFilterMixin,
    TenancyFilterMixin,
    PrimaryModelFilterMixin,
):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    site: Annotated['SiteFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    site_id: ID | None = strawberry_django.filter_field()
    cluster: Annotated['ClusterFilter', strawberry.lazy('virtualization.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    cluster_id: ID | None = strawberry_django.filter_field()
    device: Annotated['DeviceFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    device_id: ID | None = strawberry_django.filter_field()
    platform: Annotated['PlatformFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    platform_id: ID | None = strawberry_django.filter_field()
    status: Annotated['VirtualMachineStatusEnum', strawberry.lazy('virtualization.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    role: Annotated['DeviceRoleFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    role_id: ID | None = strawberry_django.filter_field()
    primary_ip4: Annotated['IPAddressFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    primary_ip4_id: ID | None = strawberry_django.filter_field()
    primary_ip6: Annotated['IPAddressFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    primary_ip6_id: ID | None = strawberry_django.filter_field()
    vcpus: Annotated['FloatLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    memory: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    disk: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    serial: FilterLookup[str] | None = strawberry_django.filter_field()
    interface_count: FilterLookup[int] | None = strawberry_django.filter_field()
    virtual_disk_count: FilterLookup[int] | None = strawberry_django.filter_field()
    interfaces: Annotated['VMInterfaceFilter', strawberry.lazy('virtualization.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    services: Annotated['ServiceFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    virtual_disks: Annotated['VirtualDiskFilter', strawberry.lazy('virtualization.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.VMInterface, lookups=True)
class VMInterfaceFilter(VMComponentFilterMixin, InterfaceBaseFilterMixin):
    ip_addresses: Annotated['IPAddressFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    vrf: Annotated['VRFFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    vrf_id: ID | None = strawberry_django.filter_field()
    parent: Annotated['VMInterfaceFilter', strawberry.lazy('virtualization.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    parent_id: ID | None = strawberry_django.filter_field()
    fhrp_group_assignments: Annotated['FHRPGroupAssignmentFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tunnel_terminations: Annotated['TunnelTerminationFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    l2vpn_terminations: Annotated['L2VPNFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    mac_addresses: Annotated['MACAddressFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.VirtualDisk, lookups=True)
class VirtualDiskFilter(VMComponentFilterMixin):
    size: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
