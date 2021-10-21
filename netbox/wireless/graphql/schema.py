import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *


class WirelessQuery(graphene.ObjectType):
    wireless_lan = ObjectField(WirelessLANType)
    wireless_lan_list = ObjectListField(WirelessLANType)

    wireless_lan_group = ObjectField(WirelessLANGroupType)
    wireless_lan_group_list = ObjectListField(WirelessLANGroupType)

    wireless_link = ObjectField(WirelessLinkType)
    wireless_link_list = ObjectListField(WirelessLinkType)
