from typing import Annotated, List, TYPE_CHECKING, Union

import strawberry
import strawberry_django

from netbox.graphql.types_v1 import PrimaryObjectTypeV1, NestedGroupObjectTypeV1
from wireless import models
from .filters_v1 import *

if TYPE_CHECKING:
    from dcim.graphql.types_v1 import (
        DeviceTypeV1, InterfaceTypeV1, LocationTypeV1, RegionTypeV1, SiteGroupTypeV1, SiteTypeV1
    )
    from ipam.graphql.types_v1 import VLANTypeV1
    from tenancy.graphql.types_v1 import TenantTypeV1

__all__ = (
    'WirelessLANTypeV1',
    'WirelessLANGroupTypeV1',
    'WirelessLinkTypeV1',
)


@strawberry_django.type(
    models.WirelessLANGroup,
    fields='__all__',
    filters=WirelessLANGroupFilterV1,
    pagination=True
)
class WirelessLANGroupTypeV1(NestedGroupObjectTypeV1):
    parent: Annotated["WirelessLANGroupTypeV1", strawberry.lazy('wireless.graphql.types_v1')] | None

    wireless_lans: List[Annotated["WirelessLANTypeV1", strawberry.lazy('wireless.graphql.types_v1')]]
    children: List[Annotated["WirelessLANGroupTypeV1", strawberry.lazy('wireless.graphql.types_v1')]]


@strawberry_django.type(
    models.WirelessLAN,
    exclude=['scope_type', 'scope_id', '_location', '_region', '_site', '_site_group'],
    filters=WirelessLANFilterV1,
    pagination=True
)
class WirelessLANTypeV1(PrimaryObjectTypeV1):
    group: Annotated["WirelessLANGroupTypeV1", strawberry.lazy('wireless.graphql.types_v1')] | None
    vlan: Annotated["VLANTypeV1", strawberry.lazy('ipam.graphql.types_v1')] | None
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None

    interfaces: List[Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]

    @strawberry_django.field
    def scope(self) -> Annotated[Union[
        Annotated["LocationTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["RegionTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["SiteGroupTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
        Annotated["SiteTypeV1", strawberry.lazy('dcim.graphql.types_v1')],
    ], strawberry.union("WirelessLANScopeTypeV1")] | None:
        return self.scope


@strawberry_django.type(
    models.WirelessLink,
    fields='__all__',
    filters=WirelessLinkFilterV1,
    pagination=True
)
class WirelessLinkTypeV1(PrimaryObjectTypeV1):
    interface_a: Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]
    interface_b: Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]
    tenant: Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')] | None
    _interface_a_device: Annotated["DeviceTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
    _interface_b_device: Annotated["DeviceTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None
