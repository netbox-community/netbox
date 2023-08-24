import strawberry
from strawberry_django.optimizer import DjangoOptimizerExtension
from strawberry.schema.config import StrawberryConfig
from circuits.graphql.schema import CircuitsQuery
from users.graphql.schema import UsersQuery


@strawberry.type
class Query(CircuitsQuery, UsersQuery):
    pass


schema = strawberry.Schema(
    query=Query,
    config=StrawberryConfig(auto_camel_case=False),
    extensions=[
        DjangoOptimizerExtension,
    ]
)
