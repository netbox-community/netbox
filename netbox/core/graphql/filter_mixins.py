from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry_django import DatetimeFilterLookup

if TYPE_CHECKING:
    from .filters import *

__all__ = (
    'ChangeLoggingMixin',
)


@dataclass
class ChangeLoggingMixin:
    # TODO: "changelog" is not a valid field name; needs to be updated for ObjectChange
    changelog: Annotated['ObjectChangeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    created: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()
    last_updated: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()
