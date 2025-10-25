from typing import List

import strawberry_django

from netbox.graphql.types_v1 import BaseObjectTypeV1
from users.models import Group, Owner, OwnerGroup, User
from .filters_v1 import *

__all__ = (
    'GroupTypeV1',
    'OwnerGroupTypeV1',
    'OwnerTypeV1',
    'UserTypeV1',
)


@strawberry_django.type(
    Group,
    fields=['id', 'name'],
    filters=GroupFilterV1,
    pagination=True
)
class GroupTypeV1(BaseObjectTypeV1):
    pass


@strawberry_django.type(
    User,
    fields=[
        'id', 'username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined', 'groups',
    ],
    filters=UserFilterV1,
    pagination=True
)
class UserTypeV1(BaseObjectTypeV1):
    groups: List[GroupTypeV1]


@strawberry_django.type(
    OwnerGroup,
    fields=['id', 'name', 'description'],
    filters=OwnerGroupFilterV1,
    pagination=True
)
class OwnerGroupTypeV1(BaseObjectTypeV1):
    pass


@strawberry_django.type(
    Owner,
    fields=['id', 'group', 'name', 'description', 'user_groups', 'users'],
    filters=OwnerFilterV1,
    pagination=True
)
class OwnerTypeV1(BaseObjectTypeV1):
    group: OwnerGroupTypeV1 | None
