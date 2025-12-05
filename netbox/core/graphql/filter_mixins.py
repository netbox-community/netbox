from dataclasses import dataclass

import strawberry_django
from strawberry import ID
from strawberry_django import FilterLookup

__all__ = (
    'BaseFilter',
    'BaseObjectTypeFilterMixin',
)


# @strawberry.input
class BaseFilter: ...


@dataclass
class BaseObjectTypeFilterMixin(BaseFilter):
    id: FilterLookup[ID] | None = strawberry_django.filter_field()
