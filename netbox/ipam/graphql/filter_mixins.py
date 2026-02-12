from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry_django import BaseFilterLookup

if TYPE_CHECKING:
    from netbox.graphql.filter_lookups import IntegerLookup

    from .enums import *

__all__ = (
    'ServiceFilterMixin',
)


@dataclass
class ServiceFilterMixin:
    protocol: BaseFilterLookup[Annotated['ServiceProtocolEnum', strawberry.lazy('ipam.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    ports: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
