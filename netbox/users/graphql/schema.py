import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *


class UsersQuery(graphene.ObjectType):
    group = ObjectField(GroupType)
    group_list = ObjectListField(GroupType)

    user = ObjectField(UserType)
    user_list = ObjectListField(UserType)
