from typing import List
import strawberry

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .types import *


@strawberry.type
class UsersQuery:
    group: GroupType = strawberry.django.field()
    group_list: List[GroupType] = strawberry.django.field()

    user: UserType = strawberry.django.field()
    user_list: List[UserType] = strawberry.django.field()
