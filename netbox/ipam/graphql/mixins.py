from typing import Annotated, List

import strawberry
import strawberry_django

__all__ = (
    'IPAddressesMixin',
    'VLANGroupsMixin',
)


@strawberry.type
class IPAddressesMixin:
    ip_addresses: List[Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')]]


@strawberry.type
class VLANGroupsMixin:
    vlan_groups: List[Annotated["VLANGroupType", strawberry.lazy('ipam.graphql.types')]]
