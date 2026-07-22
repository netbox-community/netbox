

from netbox.graphql.types import BaseObjectType, register_type
from users.models import Group, Owner, OwnerGroup, User

from .filters import *

__all__ = (
    'GroupType',
    'OwnerGroupType',
    'OwnerType',
    'UserType',
)


@register_type(
    Group,
    fields=['id', 'name'],
    filters=GroupFilter,
    pagination=True
)
class GroupType(BaseObjectType):
    pass


@register_type(
    User,
    fields=[
        'id', 'username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined', 'groups',
    ],
    filters=UserFilter,
    pagination=True
)
class UserType(BaseObjectType):
    groups: list[GroupType]


@register_type(
    OwnerGroup,
    fields=['id', 'name', 'description'],
    filters=OwnerGroupFilter,
    pagination=True
)
class OwnerGroupType(BaseObjectType):
    pass


@register_type(
    Owner,
    fields=['id', 'group', 'name', 'description', 'user_groups', 'users'],
    filters=OwnerFilter,
    pagination=True
)
class OwnerType(BaseObjectType):
    group: OwnerGroupType | None
