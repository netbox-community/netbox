from dataclasses import dataclass
from typing import Annotated, TYPE_CHECKING
import strawberry
import strawberry_django

from core.graphql.filter_mixins import *

if TYPE_CHECKING:
    from .enums import *
    from core.graphql.filter_lookups import *

__all__ = ['ServiceBaseFilterMixin']


@dataclass
class ServiceBaseFilterMixin(BaseFilterMixin):
    protocol: Annotated['ServiceProtocolEnum', strawberry.lazy('ipam.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    ports: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
