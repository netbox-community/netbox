from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry_django import BaseFilterLookup

if TYPE_CHECKING:
    from netbox.graphql.enums import ColorEnum

__all__ = (
    'CircuitTypeFilterMixin',
)


@dataclass
class CircuitTypeFilterMixin:
    color: BaseFilterLookup[Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
