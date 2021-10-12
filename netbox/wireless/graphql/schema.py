import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *


class WirelessQuery(graphene.ObjectType):
    ssid = ObjectField(SSIDType)
    ssid_list = ObjectListField(SSIDType)
