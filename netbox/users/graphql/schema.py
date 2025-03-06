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
