from typing import List
import strawberry
import strawberry_django

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .types import *


@strawberry.type
class UsersQuery:
    group: GroupType = strawberry_django.field()
    group_list: List[GroupType] = strawberry_django.field()

    user: UserType = strawberry_django.field()
    user_list: List[UserType] = strawberry_django.field()
