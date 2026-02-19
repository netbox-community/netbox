from typing import Annotated

import strawberry

__all__ = (
    'ContactAssignmentsMixin',
)


@strawberry.type
class ContactAssignmentsMixin:
    assignments: list[Annotated["ContactAssignmentType", strawberry.lazy('tenancy.graphql.types')]]  # noqa: F821
