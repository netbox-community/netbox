
import strawberry_django

from netbox.graphql.types import BaseObjectType
from users.models import Group, Owner, OwnerGroup, User

from .filters import *

__all__ = (
    'GroupType',
    'OwnerGroupType',
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
    groups: list[GroupType]


@strawberry_django.type(
    OwnerGroup,
    fields=['id', 'name', 'description'],
    filters=OwnerGroupFilter,
    pagination=True
)
class OwnerGroupType(BaseObjectType):
    pass


@strawberry_django.type(
    Owner,
    fields=['id', 'group', 'name', 'description', 'user_groups', 'users'],
    filters=OwnerFilter,
    pagination=True
)
class OwnerType(BaseObjectType):
    group: OwnerGroupType | None
