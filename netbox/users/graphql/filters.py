from datetime import datetime
from typing import Annotated, TYPE_CHECKING
import strawberry
import strawberry_django
from strawberry_django import (
    FilterLookup,
    DatetimeFilterLookup,
)
from core.graphql.filter_mixins import *
from netbox.graphql.filter_mixins import *
from tenancy.graphql.filter_mixins import *

from users import models

if TYPE_CHECKING:
    from .enums import *
    from netbox.graphql.enums import *
    from wireless.graphql.enums import *
    from core.graphql.filter_lookups import *
    from extras.graphql.filters import *
    from circuits.graphql.filters import *
    from dcim.graphql.filters import *
    from ipam.graphql.filters import *
    from tenancy.graphql.filters import *
    from wireless.graphql.filters import *
    from users.graphql.filters import *
    from virtualization.graphql.filters import *
    from vpn.graphql.filters import *

__all__ = (
    'GroupFilter',
    'UserFilter',
)


@strawberry_django.filter(models.Group, lookups=True)
class GroupFilter(BaseObjectTypeFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter(models.User, lookups=True)
class UserFilter(BaseObjectTypeFilterMixin):
    username: FilterLookup[str] | None = strawberry_django.filter_field()
    first_name: FilterLookup[str] | None = strawberry_django.filter_field()
    last_name: FilterLookup[str] | None = strawberry_django.filter_field()
    email: FilterLookup[str] | None = strawberry_django.filter_field()
    is_staff: FilterLookup[bool] | None = strawberry_django.filter_field()
    is_active: FilterLookup[bool] | None = strawberry_django.filter_field()
    date_joined: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()
    groups: Annotated['GroupFilter', strawberry.lazy('users.graphql.filters')] | None = strawberry_django.filter_field()
