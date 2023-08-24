import strawberry
from strawberry_django.optimizer import DjangoOptimizerExtension
from strawberry.schema.config import StrawberryConfig
from users.graphql.schema import UsersQuery


@strawberry.type
class Query(UsersQuery):
    pass


schema = strawberry.Schema(
    query=Query,
    config=StrawberryConfig(auto_camel_case=False),
    extensions=[
        DjangoOptimizerExtension,
    ]
)
