import graphene

from circuits.graphql.schema import CircuitsQuery


class Query(
    CircuitsQuery,
    graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query, auto_camelcase=False)
