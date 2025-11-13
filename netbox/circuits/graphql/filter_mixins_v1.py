from dataclasses import dataclass
from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django

from netbox.graphql.filter_mixins_v1 import OrganizationalModelFilterMixinV1

if TYPE_CHECKING:
    from netbox.graphql.enums import ColorEnum

__all__ = (
    'BaseCircuitTypeFilterMixinV1',
)


@dataclass
class BaseCircuitTypeFilterMixinV1(OrganizationalModelFilterMixinV1):
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()
