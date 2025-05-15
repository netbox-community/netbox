from dataclasses import dataclass
from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry import ID
from strawberry_django import FilterLookup

from netbox.graphql.filter_mixins import NetBoxModelFilterMixin

if TYPE_CHECKING:
    from .filters import VirtualMachineFilter

__all__ = (
    'VMComponentFilterMixin',
)


@dataclass
class VMComponentFilterMixin(NetBoxModelFilterMixin):
    virtual_machine: Annotated['VirtualMachineFilter', strawberry.lazy('virtualization.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    virtual_machine_id: ID | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
