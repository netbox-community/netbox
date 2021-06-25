import graphene

from circuits.graphql.schema import CircuitsQuery
from ipam.graphql.schema import IPAMQuery


class Query(
    CircuitsQuery,
    IPAMQuery,
    graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query, auto_camelcase=False)
