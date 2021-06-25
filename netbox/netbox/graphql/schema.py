import graphene

from circuits.graphql.schema import CircuitsQuery
from extras.graphql.schema import ExtrasQuery
from ipam.graphql.schema import IPAMQuery
from tenancy.graphql.schema import TenancyQuery
from virtualization.graphql.schema import VirtualizationQuery


class Query(
    CircuitsQuery,
    ExtrasQuery,
    IPAMQuery,
    TenancyQuery,
    VirtualizationQuery,
    graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query, auto_camelcase=False)
