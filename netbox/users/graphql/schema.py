from typing import List
import strawberry
import strawberry_django

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from users import models
from .types import *


@strawberry.type
class UsersQuery:
    @strawberry.field
    def group(self, id: int) -> GroupType:
        return models.Group.objects.get(id=id)
    group_list: List[GroupType] = strawberry_django.field()

    @strawberry.field
    def user(self, id: int) -> UserType:
        return models.User.objects.get(id=id)
    user_list: List[UserType] = strawberry_django.field()
