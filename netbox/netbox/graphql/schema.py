import strawberry
from strawberry_django.optimizer import DjangoOptimizerExtension
from strawberry.schema.config import StrawberryConfig
from circuits.graphql.schema import CircuitsQuery
from users.graphql.schema import UsersQuery
# from virtualization.graphql.schema import VirtualizationQuery
# from vpn.graphql.schema import VPNQuery
# from wireless.graphql.schema import WirelessQuery


@strawberry.type
class Query(CircuitsQuery, UsersQuery):
    pass

# class Query(
#     UsersQuery,
#     CircuitsQuery,
#     CoreQuery,
#     DCIMQuery,
#     ExtrasQuery,
#     IPAMQuery,
#     TenancyQuery,
#     VirtualizationQuery,
#     VPNQuery,
#     WirelessQuery,
#     *registry['plugins']['graphql_schemas'],  # Append plugin schemas
#     graphene.ObjectType
# ):
#     pass


schema = strawberry.Schema(
    query=Query,
    config=StrawberryConfig(auto_camel_case=False),
    extensions=[
        DjangoOptimizerExtension,
    ]
)
