import strawberry

from tenancy.choices import *

__all__ = (
    'ContactPriorityEnum',
)

ContactPriorityEnum = strawberry.enum(ContactPriorityChoices.as_enum(prefix='priority'))
