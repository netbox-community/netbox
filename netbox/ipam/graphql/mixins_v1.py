from typing import Annotated, List

import strawberry

__all__ = (
    'IPAddressesMixinV1',
    'VLANGroupsMixinV1',
)


@strawberry.type
class IPAddressesMixinV1:
    ip_addresses: List[Annotated["IPAddressTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]  # noqa: F821


@strawberry.type
class VLANGroupsMixinV1:
    vlan_groups: List[Annotated["VLANGroupTypeV1", strawberry.lazy('ipam.graphql.types_v1')]]  # noqa: F821
