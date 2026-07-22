from typing import Annotated

import strawberry
import strawberry_django
from strawberry_django import DatetimeFilterLookup, FilterLookup, StrFilterLookup

from netbox.graphql.filters import BaseModelFilter, register_filter
from users import models

__all__ = (
    'GroupFilter',
    'OwnerFilter',
    'OwnerGroupFilter',
    'UserFilter',
)


@register_filter(models.Group, lookups=True)
class GroupFilter(BaseModelFilter):
    name: StrFilterLookup | None = strawberry_django.filter_field()
    description: StrFilterLookup | None = strawberry_django.filter_field()


@register_filter(models.User, lookups=True)
class UserFilter(BaseModelFilter):
    username: StrFilterLookup | None = strawberry_django.filter_field()
    first_name: StrFilterLookup | None = strawberry_django.filter_field()
    last_name: StrFilterLookup | None = strawberry_django.filter_field()
    email: StrFilterLookup | None = strawberry_django.filter_field()
    is_superuser: FilterLookup[bool] | None = strawberry_django.filter_field()
    is_active: FilterLookup[bool] | None = strawberry_django.filter_field()
    date_joined: DatetimeFilterLookup | None = strawberry_django.filter_field()
    last_login: DatetimeFilterLookup | None = strawberry_django.filter_field()
    groups: Annotated['GroupFilter', strawberry.lazy('users.graphql.filters')] | None = strawberry_django.filter_field()


@register_filter(models.Owner, lookups=True)
class OwnerFilter(BaseModelFilter):
    name: StrFilterLookup | None = strawberry_django.filter_field()
    description: StrFilterLookup | None = strawberry_django.filter_field()
    group: Annotated['OwnerGroupFilter', strawberry.lazy('users.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    user_groups: Annotated['GroupFilter', strawberry.lazy('users.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    users: Annotated['UserFilter', strawberry.lazy('users.graphql.filters')] | None = strawberry_django.filter_field()


@register_filter(models.OwnerGroup, lookups=True)
class OwnerGroupFilter(BaseModelFilter):
    name: StrFilterLookup | None = strawberry_django.filter_field()
    description: StrFilterLookup | None = strawberry_django.filter_field()
