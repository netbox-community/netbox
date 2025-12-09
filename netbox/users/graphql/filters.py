from datetime import datetime
from typing import Annotated

import strawberry
import strawberry_django
from strawberry_django import DatetimeFilterLookup, FilterLookup

from netbox.graphql.filters import BaseModelFilter
from users import models

__all__ = (
    'GroupFilter',
    'OwnerFilter',
    'OwnerGroupFilter',
    'UserFilter',
)


@strawberry_django.filter_type(models.Group, lookups=True)
class GroupFilter(BaseModelFilter):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.User, lookups=True)
class UserFilter(BaseModelFilter):
    username: FilterLookup[str] | None = strawberry_django.filter_field()
    first_name: FilterLookup[str] | None = strawberry_django.filter_field()
    last_name: FilterLookup[str] | None = strawberry_django.filter_field()
    email: FilterLookup[str] | None = strawberry_django.filter_field()
    is_superuser: FilterLookup[bool] | None = strawberry_django.filter_field()
    is_active: FilterLookup[bool] | None = strawberry_django.filter_field()
    date_joined: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()
    last_login: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()
    groups: Annotated['GroupFilter', strawberry.lazy('users.graphql.filters')] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.Owner, lookups=True)
class OwnerFilter(BaseModelFilter):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    group: Annotated['OwnerGroupFilter', strawberry.lazy('users.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    user_groups: Annotated['GroupFilter', strawberry.lazy('users.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    users: Annotated['UserFilter', strawberry.lazy('users.graphql.filters')] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.OwnerGroup, lookups=True)
class OwnerGroupFilter(BaseModelFilter):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
