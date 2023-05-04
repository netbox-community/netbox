import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *
from utilities.graphql_optimizer import gql_query_optimizer
from wireless import models


class WirelessQuery(graphene.ObjectType):
    wireless_lan = ObjectField(WirelessLANType)
    wireless_lan_list = ObjectListField(WirelessLANType)

    def resolve_wireless_lan_list(root, info, **kwargs):
        return gql_query_optimizer(models.WirelessLAN.objects.all(), info)

    wireless_lan_group = ObjectField(WirelessLANGroupType)
    wireless_lan_group_list = ObjectListField(WirelessLANGroupType)

    def resolve_wireless_lan_group_list(root, info, **kwargs):
        return gql_query_optimizer(models.WirelessLANGroup.objects.all(), info)

    wireless_link = ObjectField(WirelessLinkType)
    wireless_link_list = ObjectListField(WirelessLinkType)

    def resolve_wireless_link_list(root, info, **kwargs):
        return gql_query_optimizer(models.WirelessLink.objects.all(), info)
