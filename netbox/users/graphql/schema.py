import graphene

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *
from utilities.graphql_optimizer import gql_query_optimizer


class UsersQuery(graphene.ObjectType):
    group = ObjectField(GroupType)
    group_list = ObjectListField(GroupType)

    def resolve_group_list(root, info, **kwargs):
        return gql_query_optimizer(Group.objects.all(), info)

    user = ObjectField(UserType)
    user_list = ObjectListField(UserType)

    def resolve_user_list(root, info, **kwargs):
        return gql_query_optimizer(get_user_model().objects.all(), info)
