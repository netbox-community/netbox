from dataclasses import dataclass
from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django

from core.graphql.filter_mixins_v1 import BaseFilterMixinV1

if TYPE_CHECKING:
    from netbox.graphql.filter_lookups import IntegerLookup
    from .enums import *

__all__ = (
    'ServiceBaseFilterMixinV1',
)


@dataclass
class ServiceBaseFilterMixinV1(BaseFilterMixinV1):
    protocol: Annotated['ServiceProtocolEnum', strawberry.lazy('ipam.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    ports: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
