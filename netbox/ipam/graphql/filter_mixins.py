from dataclasses import dataclass
from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django

from core.graphql.filter_mixins import BaseFilterMixin

if TYPE_CHECKING:
    from netbox.graphql.filter_lookups import IntegerLookup
    from .enums import *

__all__ = (
    'ServiceBaseFilterMixin',
)


@dataclass
class ServiceBaseFilterMixin(BaseFilterMixin):
    protocol: Annotated['ServiceProtocolEnum', strawberry.lazy('ipam.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    ports: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
