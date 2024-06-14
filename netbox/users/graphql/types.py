from typing import List

import strawberry_django
from django.contrib.auth import get_user_model

from netbox.graphql.types import BaseObjectType
from users.models import Group
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
    get_user_model(),
    fields=[
        'id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined', 'groups',
    ],
    filters=UserFilter
)
class UserType(BaseObjectType):
    groups: List[GroupType]
