from typing import Annotated, List

import strawberry
import strawberry_django

from netbox.graphql.types import OrganizationalObjectType, NetBoxObjectType
from wireless import models
from .filters import *

__all__ = (
    'WirelessLANType',
    'WirelessLANGroupType',
    'WirelessLinkType',
)


@strawberry_django.type(
    models.WirelessLANGroup,
    fields='__all__',
    filters=WirelessLANGroupFilter
)
class WirelessLANGroupType(OrganizationalObjectType):
    parent: Annotated["WirelessLANGroupType", strawberry.lazy('wireless.graphql.types')] | None

    wireless_lans: List[Annotated["WirelessLANType", strawberry.lazy('wireless.graphql.types')]]
    children: List[Annotated["WirelessLANGroupType", strawberry.lazy('wireless.graphql.types')]]


@strawberry_django.type(
    models.WirelessLAN,
    fields='__all__',
    filters=WirelessLANFilter
)
class WirelessLANType(NetBoxObjectType):
    group: Annotated["WirelessLANGroupType", strawberry.lazy('wireless.graphql.types')] | None
    vlan: Annotated["VLANType", strawberry.lazy('ipam.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None

    interfaces: List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.WirelessLink,
    fields='__all__',
    filters=WirelessLinkFilter
)
class WirelessLinkType(NetBoxObjectType):
    interface_a: Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]
    interface_b: Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None
    _interface_a_device: Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')] | None
    _interface_b_device: Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')] | None
