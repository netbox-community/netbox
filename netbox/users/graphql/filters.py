import strawberry
import strawberry_django
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from strawberry import auto
from users import filtersets

__all__ = (
    'GroupFilter',
    'UserFilter',
)


@strawberry_django.filter(Group, lookups=True)
class GroupFilter(filtersets.GroupFilterSet):
    id: auto
    name: auto


@strawberry_django.filter(get_user_model(), lookups=True)
class UserFilter(filtersets.UserFilterSet):
    id: auto
    username: auto
    first_name: auto
    last_name: auto
    email: auto
    is_staff: auto
    is_active: auto
    is_superuser: auto
