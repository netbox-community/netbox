from typing import List

import strawberry
import strawberry_django

from .types_v1 import *


@strawberry.type(name="Query")
class UsersQueryV1:
    group: GroupTypeV1 = strawberry_django.field()
    group_list: List[GroupTypeV1] = strawberry_django.field()

    user: UserTypeV1 = strawberry_django.field()
    user_list: List[UserTypeV1] = strawberry_django.field()
