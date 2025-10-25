from datetime import datetime
from typing import Annotated

import strawberry
import strawberry_django
from strawberry_django import DatetimeFilterLookup, FilterLookup

from core.graphql.filter_mixins_v1 import BaseObjectTypeFilterMixinV1
from users import models

__all__ = (
    'GroupFilterV1',
    'OwnerFilterV1',
    'OwnerGroupFilterV1',
    'UserFilterV1',
)


@strawberry_django.filter_type(models.Group, lookups=True)
class GroupFilterV1(BaseObjectTypeFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.User, lookups=True)
class UserFilterV1(BaseObjectTypeFilterMixinV1):
    username: FilterLookup[str] | None = strawberry_django.filter_field()
    first_name: FilterLookup[str] | None = strawberry_django.filter_field()
    last_name: FilterLookup[str] | None = strawberry_django.filter_field()
    email: FilterLookup[str] | None = strawberry_django.filter_field()
    is_superuser: FilterLookup[bool] | None = strawberry_django.filter_field()
    is_active: FilterLookup[bool] | None = strawberry_django.filter_field()
    date_joined: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()
    last_login: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()
    groups: Annotated['GroupFilterV1', strawberry.lazy('users.graphql.filters_v1')] | None = (
        strawberry_django.filter_field())


@strawberry_django.filter_type(models.Owner, lookups=True)
class OwnerFilterV1(BaseObjectTypeFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    group: Annotated['OwnerGroupFilterV1', strawberry.lazy('users.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    user_groups: Annotated['GroupFilterV1', strawberry.lazy('users.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    users: Annotated['UserFilterV1', strawberry.lazy('users.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.OwnerGroup, lookups=True)
class OwnerGroupFilterV1(BaseObjectTypeFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
