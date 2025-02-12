from dataclasses import dataclass
from typing import Annotated, TYPE_CHECKING
import strawberry
from strawberry import ID
import strawberry_django
from strawberry_django import FilterLookup

from netbox.graphql.filter_mixins import NetBoxModelFilterMixin

if TYPE_CHECKING:
    from .filters import *

__all__ = ['VMComponentFilterMixin']


@dataclass
class VMComponentFilterMixin(NetBoxModelFilterMixin):
    virtual_manchine: Annotated['VirtualMachineFilter', strawberry.lazy('virtualization.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    virtual_machine_id: ID | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
