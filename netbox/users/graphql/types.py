from django.contrib.auth.models import Group, User
from graphene_django import DjangoObjectType

from users import filtersets
from utilities.querysets import RestrictedQuerySet

__all__ = (
    'GroupType',
    'UserType',
)


class GroupType(DjangoObjectType):

    class Meta:
        model = Group
        fields = ('id', 'name')
        filterset_class = filtersets.GroupFilterSet

    @classmethod
    def get_queryset(cls, queryset, info):
        return RestrictedQuerySet(model=Group)


class UserType(DjangoObjectType):

    class Meta:
        model = User
        fields = (
            'id', 'username', 'password', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined',
            'groups',
        )
        filterset_class = filtersets.UserFilterSet

    @classmethod
    def get_queryset(cls, queryset, info):
        return RestrictedQuerySet(model=User)
