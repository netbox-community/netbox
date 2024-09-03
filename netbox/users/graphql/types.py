from typing import List

import strawberry_django

from netbox.graphql.types import BaseObjectType
from users.models import Group, User
from .filters import *

__all__ = (
    'GroupType',
    'UserType',
)


@strawberry_django.type(
    Group,
    fields=['id', 'name'],
    filters=GroupFilter
)
class GroupType(BaseObjectType):
    pass


@strawberry_django.type(
    User,
    fields=[
        'id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined', 'groups',
    ],
    filters=UserFilter
)
class UserType(BaseObjectType):
    groups: List[GroupType]
