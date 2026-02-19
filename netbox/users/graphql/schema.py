import strawberry
import strawberry_django

from .types import *


@strawberry.type(name="Query")
class UsersQuery:
    group: GroupType = strawberry_django.field()
    group_list: list[GroupType] = strawberry_django.field()

    user: UserType = strawberry_django.field()
    user_list: list[UserType] = strawberry_django.field()

    owner_group: OwnerGroupType = strawberry_django.field()
    owner_group_list: list[OwnerGroupType] = strawberry_django.field()

    owner: OwnerType = strawberry_django.field()
    owner_list: list[OwnerType] = strawberry_django.field()
