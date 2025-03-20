from typing import Annotated, List, TYPE_CHECKING, Union

import strawberry
import strawberry_django

from netbox.graphql.types import OrganizationalObjectType, NetBoxObjectType
from wireless import models
from .filters import *

if TYPE_CHECKING:
    from dcim.graphql.types import DeviceType, InterfaceType, LocationType, RegionType, SiteGroupType, SiteType
    from ipam.graphql.types import VLANType
    from tenancy.graphql.types import TenantType

__all__ = (
    'WirelessLANType',
    'WirelessLANGroupType',
    'WirelessLinkType',
)


@strawberry_django.type(
    models.WirelessLANGroup,
    fields='__all__',
    filters=WirelessLANGroupFilter,
    pagination=True
)
class WirelessLANGroupType(OrganizationalObjectType):
    parent: Annotated["WirelessLANGroupType", strawberry.lazy('wireless.graphql.types')] | None

    wireless_lans: List[Annotated["WirelessLANType", strawberry.lazy('wireless.graphql.types')]]
    children: List[Annotated["WirelessLANGroupType", strawberry.lazy('wireless.graphql.types')]]


@strawberry_django.type(
    models.WirelessLAN,
    exclude=['scope_type', 'scope_id', '_location', '_region', '_site', '_site_group'],
    filters=WirelessLANFilter,
    pagination=True
)
class WirelessLANType(NetBoxObjectType):
    group: Annotated["WirelessLANGroupType", strawberry.lazy('wireless.graphql.types')] | None
    vlan: Annotated["VLANType", strawberry.lazy('ipam.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None

    interfaces: List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]

    @strawberry_django.field
    def scope(self) -> Annotated[Union[
        Annotated["LocationType", strawberry.lazy('dcim.graphql.types')],
        Annotated["RegionType", strawberry.lazy('dcim.graphql.types')],
        Annotated["SiteGroupType", strawberry.lazy('dcim.graphql.types')],
        Annotated["SiteType", strawberry.lazy('dcim.graphql.types')],
    ], strawberry.union("WirelessLANScopeType")] | None:
        return self.scope


@strawberry_django.type(
    models.WirelessLink,
    fields='__all__',
    filters=WirelessLinkFilter,
    pagination=True
)
class WirelessLinkType(NetBoxObjectType):
    interface_a: Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]
    interface_b: Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None
    _interface_a_device: Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')] | None
    _interface_b_device: Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')] | None
