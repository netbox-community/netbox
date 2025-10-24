from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry import ID
from strawberry_django import DatetimeFilterLookup

if TYPE_CHECKING:
    from .filters_v1 import *

__all__ = (
    'BaseFilterMixinV1',
    'BaseObjectTypeFilterMixinV1',
    'ChangeLogFilterMixinV1',
)


# @strawberry.input
class BaseFilterMixinV1: ...


@dataclass
class BaseObjectTypeFilterMixinV1(BaseFilterMixinV1):
    id: ID | None = strawberry.UNSET


@dataclass
class ChangeLogFilterMixinV1(BaseFilterMixinV1):
    id: ID | None = strawberry.UNSET
    changelog: Annotated['ObjectChangeFilterV1', strawberry.lazy('core.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    created: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()
    last_updated: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()
