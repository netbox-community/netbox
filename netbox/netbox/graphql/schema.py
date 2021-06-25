import graphene

from circuits.graphql.schema import CircuitsQuery
from extras.graphql.schema import ExtrasQuery
from ipam.graphql.schema import IPAMQuery


class Query(
    CircuitsQuery,
    ExtrasQuery,
    IPAMQuery,
    graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query, auto_camelcase=False)
