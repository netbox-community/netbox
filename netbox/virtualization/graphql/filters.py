from typing import Annotated, TYPE_CHECKING
import strawberry
from strawberry.scalars import ID
import strawberry_django
from strawberry_django import (
    FilterLookup,
)
from core.graphql.filter_mixins import *
from netbox.graphql.filter_mixins import *
from tenancy.graphql.filter_mixins import *
from dcim.graphql.filter_mixins import *
from extras.graphql.filter_mixins import *
from virtualization.graphql.filter_mixins import *

from virtualization import models

if TYPE_CHECKING:
    from .enums import *
    from netbox.graphql.enums import *
    from wireless.graphql.enums import *
    from core.graphql.filter_lookups import *
    from extras.graphql.filters import *
    from circuits.graphql.filters import *
    from dcim.graphql.filters import *
    from ipam.graphql.filters import *
    from tenancy.graphql.filters import *
    from wireless.graphql.filters import *
    from users.graphql.filters import *
    from virtualization.graphql.filters import *
    from vpn.graphql.filters import *

__all__ = (
    'ClusterFilter',
    'ClusterGroupFilter',
    'ClusterTypeFilter',
    'VirtualMachineFilter',
    'VMInterfaceFilter',
    'VirtualDiskFilter',
)


@strawberry_django.filter(models.Cluster, lookups=True)
class ClusterFilter(ContactFilterMixin, PrimaryModelFilterMixin):
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
    tenant: Annotated['TenantFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tenant_id: ID | None = strawberry_django.filter_field()
    vlan_groups: Annotated['VLANGroupFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.ClusterGroup, lookups=True)
class ClusterGroupFilter(ContactFilterMixin, OrganizationalModelFilterMixin):
    vlan_groups: Annotated['VLANGroupFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.ClusterType, lookups=True)
class ClusterTypeFilter(OrganizationalModelFilterMixin):
    pass


@strawberry_django.filter(models.VirtualMachine, lookups=True)
class VirtualMachineFilter(
    ContactFilterMixin,
    ImageAttachmentFilterMixin,
    RenderConfigFilterMixin,
    ConfigContextFilterMixin,
    PrimaryModelFilterMixin,
):
    site: Annotated['SiteFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    site_id: ID | None = strawberry_django.filter_field()
    cluster: Annotated['ClusterFilter', strawberry.lazy('virtualization.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    cluster_id: ID | None = strawberry_django.filter_field()
    device: Annotated['DeviceFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    device_id: ID | None = strawberry_django.filter_field()
    tenant: Annotated['TenantFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tenant_id: ID | None = strawberry_django.filter_field()
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
    vcpus: Annotated['FloatLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    memory: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    disk: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    serial: FilterLookup[str] | None = strawberry_django.filter_field()
    interfaces: Annotated['VMInterfaceFilter', strawberry.lazy('virtualization.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    services: Annotated['ServiceFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    virtual_disks: Annotated['VirtualDiskFilter', strawberry.lazy('virtualization.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.VMInterface, lookups=True)
class VMInterfaceFilter(VMComponentFilterMixin, InterfaceBaseFilterMixin):
    ip_addresses: Annotated['IPAddressFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    vrf: Annotated['VRFFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    vrf_id: ID | None = strawberry_django.filter_field()
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


@strawberry_django.filter(models.VirtualDisk, lookups=True)
class VirtualDiskFilter(VMComponentFilterMixin):
    size: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
