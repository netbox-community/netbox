from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django

from netbox.graphql.types import NestedLtreeGroupObjectType, PrimaryObjectType, register_type
from wireless import models

from .filters import *

if TYPE_CHECKING:
    from dcim.graphql.types import DeviceType, InterfaceType, LocationType, RegionType, SiteGroupType, SiteType
    from ipam.graphql.types import VLANType
    from tenancy.graphql.types import TenantType

__all__ = (
    'WirelessLANGroupType',
    'WirelessLANType',
    'WirelessLinkType',
)


@register_type(
    models.WirelessLANGroup,
    exclude=['path', 'sort_path'],
    filters=WirelessLANGroupFilter,
    pagination=True
)
class WirelessLANGroupType(NestedLtreeGroupObjectType):
    parent: Annotated["WirelessLANGroupType", strawberry.lazy('wireless.graphql.types')] | None

    wireless_lans: list[Annotated["WirelessLANType", strawberry.lazy('wireless.graphql.types')]]
    children: list[Annotated["WirelessLANGroupType", strawberry.lazy('wireless.graphql.types')]]


@register_type(
    models.WirelessLAN,
    exclude=['scope_type', 'scope_id', '_location', '_region', '_site', '_site_group'],
    filters=WirelessLANFilter,
    pagination=True
)
class WirelessLANType(PrimaryObjectType):
    group: Annotated["WirelessLANGroupType", strawberry.lazy('wireless.graphql.types')] | None
    vlan: Annotated["VLANType", strawberry.lazy('ipam.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None

    interfaces: list[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]

    @strawberry_django.field(prefetch_related='scope')
    def scope(self) -> Annotated[
        Annotated['LocationType', strawberry.lazy('dcim.graphql.types')]
        | Annotated['RegionType', strawberry.lazy('dcim.graphql.types')]
        | Annotated['SiteGroupType', strawberry.lazy('dcim.graphql.types')]
        | Annotated['SiteType', strawberry.lazy('dcim.graphql.types')],
        strawberry.union('WirelessLANScopeType'),
    ] | None:
        return self.scope


@register_type(
    models.WirelessLink,
    fields='__all__',
    filters=WirelessLinkFilter,
    pagination=True
)
class WirelessLinkType(PrimaryObjectType):
    interface_a: Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]
    interface_b: Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None
    _interface_a_device: Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')] | None
    _interface_b_device: Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')] | None
