from dataclasses import dataclass
from typing import Annotated, TYPE_CHECKING
import strawberry
import strawberry_django
from netbox.graphql.filter_mixins import OrganizationalModelFilterMixin

if TYPE_CHECKING:
    from .filters import *
    from core.graphql.filter_lookups import *
    from netbox.graphql.enums import *

__all__ = ['BaseCircuitTypeFilterMixin']


@dataclass
class BaseCircuitTypeFilterMixin(OrganizationalModelFilterMixin):
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()
