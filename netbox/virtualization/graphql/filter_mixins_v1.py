from dataclasses import dataclass
from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry import ID
from strawberry_django import FilterLookup

from netbox.graphql.filter_mixins_v1 import NetBoxModelFilterMixinV1

if TYPE_CHECKING:
    from .filters_v1 import VirtualMachineFilterV1

__all__ = (
    'VMComponentFilterMixinV1',
)


@dataclass
class VMComponentFilterMixinV1(NetBoxModelFilterMixinV1):
    virtual_machine: Annotated[
        'VirtualMachineFilterV1', strawberry.lazy('virtualization.graphql.filters_v1')
    ] | None = (
        strawberry_django.filter_field()
    )
    virtual_machine_id: ID | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
