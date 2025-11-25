import strawberry

from core.choices import *

__all__ = (
    'DataSourceStatusEnum',
    'ObjectChangeActionEnum',
)

DataSourceStatusEnum = strawberry.enum(DataSourceStatusChoices.as_enum(prefix='status'))
ObjectChangeActionEnum = strawberry.enum(ObjectChangeActionChoices.as_enum(prefix='action'))
