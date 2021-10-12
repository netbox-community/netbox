import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *


class WirelessQuery(graphene.ObjectType):
    wirelesslan = ObjectField(WirelessLANType)
    wirelesslan_list = ObjectListField(WirelessLANType)
