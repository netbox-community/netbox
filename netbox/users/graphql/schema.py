import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .types import *


@strawberry.type(name="Query")
class UsersQuery:
    group: GroupType = strawberry_django.field()
    group_list: OffsetPaginated[GroupType] = strawberry_django.offset_paginated()

    user: UserType = strawberry_django.field()
    user_list: OffsetPaginated[UserType] = strawberry_django.offset_paginated()
