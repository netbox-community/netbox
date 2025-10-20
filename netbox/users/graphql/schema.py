from typing import List

import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .types import *


@strawberry.type(name="Query")
class UsersQueryOld:
    group: GroupType = strawberry_django.field()
    group_list: List[GroupType] = strawberry_django.field()

    user: UserType = strawberry_django.field()
    user_list: List[UserType] = strawberry_django.field()


@strawberry.type(name="Query")
class UsersQuery:
    group: GroupType = strawberry_django.field()
    group_list: OffsetPaginated[GroupType] = strawberry_django.offset_paginated()

    user: UserType = strawberry_django.field()
    user_list: OffsetPaginated[UserType] = strawberry_django.offset_paginated()
