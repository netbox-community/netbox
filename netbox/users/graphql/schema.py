from typing import List

import strawberry
import strawberry_django

from users import models
from .types import *


@strawberry.type
class UsersQuery:
    @strawberry.field
    def group(self, id: int) -> GroupType:
        return models.Group.objects.get(pk=id)
    group_list: List[GroupType] = strawberry_django.field()

    @strawberry.field
    def user(self, id: int) -> UserType:
        return models.User.objects.get(pk=id)
    user_list: List[UserType] = strawberry_django.field()
