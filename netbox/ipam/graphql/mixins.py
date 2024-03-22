from typing import Annotated, List

import strawberry
import strawberry_django

__all__ = (
    'IPAddressesMixin',
    'VLANGroupsMixin',
)


@strawberry.type
class IPAddressesMixin:
    @strawberry_django.field
    def ip_addresses(self) -> List[Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')]]:
        return self.ip_addresses.all()


@strawberry.type
class VLANGroupsMixin:
    @strawberry_django.field
    def vlan_groups(self) -> List[Annotated["VLANGroupType", strawberry.lazy('ipam.graphql.types')]]:
        return self.vlan_groups.all()
