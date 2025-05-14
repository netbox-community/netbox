from datetime import datetime
from typing import Annotated

import strawberry
import strawberry_django
from strawberry_django import DatetimeFilterLookup, FilterLookup

from core.graphql.filter_mixins import BaseObjectTypeFilterMixin
from users import models

__all__ = (
    'GroupFilter',
    'UserFilter',
)


@strawberry_django.filter_type(models.Group, lookups=True)
class GroupFilter(BaseObjectTypeFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.User, lookups=True)
class UserFilter(BaseObjectTypeFilterMixin):
    username: FilterLookup[str] | None = strawberry_django.filter_field()
    first_name: FilterLookup[str] | None = strawberry_django.filter_field()
    last_name: FilterLookup[str] | None = strawberry_django.filter_field()
    email: FilterLookup[str] | None = strawberry_django.filter_field()
    is_superuser: FilterLookup[bool] | None = strawberry_django.filter_field()
    is_staff: FilterLookup[bool] | None = strawberry_django.filter_field()
    is_active: FilterLookup[bool] | None = strawberry_django.filter_field()
    date_joined: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()
    last_login: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()
    groups: Annotated['GroupFilter', strawberry.lazy('users.graphql.filters')] | None = strawberry_django.filter_field()
