from typing import List

import strawberry_django

from netbox.graphql.types import BaseObjectType
from users.models import Group, Owner, User
from .filters import *

__all__ = (
    'GroupType',
    'OwnerType',
    'UserType',
)


@strawberry_django.type(
    Group,
    fields=['id', 'name'],
    filters=GroupFilter,
    pagination=True
)
class GroupType(BaseObjectType):
    pass


@strawberry_django.type(
    User,
    fields=[
        'id', 'username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined', 'groups',
    ],
    filters=UserFilter,
    pagination=True
)
class UserType(BaseObjectType):
    groups: List[GroupType]


@strawberry_django.type(
    Owner,
    fields=['id', 'name', 'description', 'groups', 'users'],
    filters=OwnerFilter,
    pagination=True
)
class OwnerType(BaseObjectType):
    pass
