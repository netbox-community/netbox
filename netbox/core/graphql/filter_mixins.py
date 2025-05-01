from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry import ID
from strawberry_django import DatetimeFilterLookup

if TYPE_CHECKING:
    from .filters import *

__all__ = (
    'BaseFilterMixin',
    'BaseObjectTypeFilterMixin',
    'ChangeLogFilterMixin',
)


# @strawberry.input
class BaseFilterMixin: ...


@dataclass
class BaseObjectTypeFilterMixin(BaseFilterMixin):
    id: ID | None = strawberry.UNSET


@dataclass
class ChangeLogFilterMixin(BaseFilterMixin):
    id: ID | None = strawberry.UNSET
    changelog: Annotated['ObjectChangeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    created: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()
    last_updated: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()
