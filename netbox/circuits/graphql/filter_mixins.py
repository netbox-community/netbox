from dataclasses import dataclass
from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django

from netbox.graphql.filters import OrganizationalModelFilter

if TYPE_CHECKING:
    from netbox.graphql.enums import ColorEnum

__all__ = (
    'BaseCircuitTypeFilter',
)


@dataclass
class BaseCircuitTypeFilter(OrganizationalModelFilter):
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()
