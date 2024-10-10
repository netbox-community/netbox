from typing import Annotated, List

import strawberry

__all__ = (
    'IPAddressesMixin',
    'VLANGroupsMixin',
)


@strawberry.type
class IPAddressesMixin:
    ip_addresses: List[Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')]]  # noqa: F821


@strawberry.type
class VLANGroupsMixin:
    vlan_groups: List[Annotated["VLANGroupType", strawberry.lazy('ipam.graphql.types')]]  # noqa: F821
