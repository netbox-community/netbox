import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *


class UsersQuery(graphene.ObjectType):
    group = ObjectField(GroupType)
    groups = ObjectListField(GroupType)

    user = ObjectField(UserType)
    users = ObjectListField(UserType)
