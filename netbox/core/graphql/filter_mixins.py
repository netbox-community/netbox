from dataclasses import dataclass

import strawberry_django
from strawberry_django import DatetimeFilterLookup

__all__ = (
    'ChangeLoggingMixin',
)


@dataclass
class ChangeLoggingMixin:
    created: DatetimeFilterLookup | None = strawberry_django.filter_field()
    last_updated: DatetimeFilterLookup | None = strawberry_django.filter_field()
