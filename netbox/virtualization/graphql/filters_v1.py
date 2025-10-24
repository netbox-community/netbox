from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import FilterLookup

from dcim.graphql.filter_mixins_v1 import InterfaceBaseFilterMixinV1, RenderConfigFilterMixinV1, ScopedFilterMixinV1
from extras.graphql.filter_mixins_v1 import ConfigContextFilterMixinV1
from netbox.graphql.filter_mixins_v1 import (
    ImageAttachmentFilterMixinV1,
    OrganizationalModelFilterMixinV1,
    PrimaryModelFilterMixinV1,
)
from tenancy.graphql.filter_mixins_v1 import ContactFilterMixinV1, TenancyFilterMixinV1
from virtualization import models
from virtualization.graphql.filter_mixins_v1 import VMComponentFilterMixinV1

if TYPE_CHECKING:
    from .enums import *
    from netbox.graphql.filter_lookups import FloatLookup, IntegerLookup
    from dcim.graphql.filters_v1 import (
        DeviceFilterV1, DeviceRoleFilterV1, MACAddressFilterV1, PlatformFilterV1, SiteFilterV1
    )
    from ipam.graphql.filters_v1 import (
        FHRPGroupAssignmentFilterV1,
        IPAddressFilterV1,
        ServiceFilterV1,
        VLANGroupFilterV1,
        VRFFilterV1,
    )
    from vpn.graphql.filters_v1 import L2VPNFilterV1, TunnelTerminationFilterV1

__all__ = (
    'ClusterFilterV1',
    'ClusterGroupFilterV1',
    'ClusterTypeFilterV1',
    'VirtualMachineFilterV1',
    'VMInterfaceFilterV1',
    'VirtualDiskFilterV1',
)


@strawberry_django.filter_type(models.Cluster, lookups=True)
class ClusterFilterV1(ContactFilterMixinV1, ScopedFilterMixinV1, TenancyFilterMixinV1, PrimaryModelFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    type: Annotated['ClusterTypeFilterV1', strawberry.lazy('virtualization.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    type_id: ID | None = strawberry_django.filter_field()
    group: Annotated['ClusterGroupFilterV1', strawberry.lazy('virtualization.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    group_id: ID | None = strawberry_django.filter_field()
    status: Annotated['ClusterStatusEnum', strawberry.lazy('virtualization.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    vlan_groups: Annotated['VLANGroupFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.ClusterGroup, lookups=True)
class ClusterGroupFilterV1(ContactFilterMixinV1, OrganizationalModelFilterMixinV1):
    vlan_groups: Annotated['VLANGroupFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.ClusterType, lookups=True)
class ClusterTypeFilterV1(OrganizationalModelFilterMixinV1):
    pass


@strawberry_django.filter_type(models.VirtualMachine, lookups=True)
class VirtualMachineFilterV1(
    ContactFilterMixinV1,
    ImageAttachmentFilterMixinV1,
    RenderConfigFilterMixinV1,
    ConfigContextFilterMixinV1,
    TenancyFilterMixinV1,
    PrimaryModelFilterMixinV1,
):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    site: Annotated['SiteFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    site_id: ID | None = strawberry_django.filter_field()
    cluster: Annotated['ClusterFilterV1', strawberry.lazy('virtualization.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    cluster_id: ID | None = strawberry_django.filter_field()
    device: Annotated['DeviceFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    device_id: ID | None = strawberry_django.filter_field()
    platform: Annotated['PlatformFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    platform_id: ID | None = strawberry_django.filter_field()
    status: Annotated['VirtualMachineStatusEnum', strawberry.lazy('virtualization.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    role: Annotated['DeviceRoleFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    role_id: ID | None = strawberry_django.filter_field()
    primary_ip4: Annotated['IPAddressFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    primary_ip4_id: ID | None = strawberry_django.filter_field()
    primary_ip6: Annotated['IPAddressFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
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
    interfaces: Annotated['VMInterfaceFilterV1', strawberry.lazy('virtualization.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    services: Annotated['ServiceFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    virtual_disks: Annotated['VirtualDiskFilterV1', strawberry.lazy('virtualization.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.VMInterface, lookups=True)
class VMInterfaceFilterV1(VMComponentFilterMixinV1, InterfaceBaseFilterMixinV1):
    ip_addresses: Annotated['IPAddressFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    vrf: Annotated['VRFFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = strawberry_django.filter_field()
    vrf_id: ID | None = strawberry_django.filter_field()
    parent: Annotated['VMInterfaceFilterV1', strawberry.lazy('virtualization.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    parent_id: ID | None = strawberry_django.filter_field()
    fhrp_group_assignments: Annotated[
        'FHRPGroupAssignmentFilterV1', strawberry.lazy('ipam.graphql.filters_v1')
    ] | None = (
        strawberry_django.filter_field()
    )
    tunnel_terminations: Annotated['TunnelTerminationFilterV1', strawberry.lazy('vpn.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    l2vpn_terminations: Annotated['L2VPNFilterV1', strawberry.lazy('vpn.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    mac_addresses: Annotated['MACAddressFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.VirtualDisk, lookups=True)
class VirtualDiskFilterV1(VMComponentFilterMixinV1):
    size: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
