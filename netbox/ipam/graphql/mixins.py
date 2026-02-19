from typing import Annotated

import strawberry

__all__ = (
    'IPAddressesMixin',
    'VLANGroupsMixin',
)


@strawberry.type
class IPAddressesMixin:
    ip_addresses: list[Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')]]  # noqa: F821


@strawberry.type
class VLANGroupsMixin:
    vlan_groups: list[Annotated["VLANGroupType", strawberry.lazy('ipam.graphql.types')]]  # noqa: F821
