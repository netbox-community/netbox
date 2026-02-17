from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import FilterLookup

if TYPE_CHECKING:
    from .filters import VirtualMachineFilter

__all__ = (
    'VMComponentFilterMixin',
)


@dataclass
class VMComponentFilterMixin:
    virtual_machine: Annotated['VirtualMachineFilter', strawberry.lazy('virtualization.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    virtual_machine_id: ID | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
