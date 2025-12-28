from typing import List

import strawberry
import strawberry_django

from .types import *


@strawberry.type(name="Query")
class UsersQuery:
    group: GroupType = strawberry_django.field()
    group_list: List[GroupType] = strawberry_django.field()

    user: UserType = strawberry_django.field()
    user_list: List[UserType] = strawberry_django.field()

    owner_group: OwnerGroupType = strawberry_django.field()
    owner_group_list: List[OwnerGroupType] = strawberry_django.field()

    owner: OwnerType = strawberry_django.field()
    owner_list: List[OwnerType] = strawberry_django.field()
