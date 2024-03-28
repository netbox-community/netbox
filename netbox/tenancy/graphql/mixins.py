from typing import Annotated, List

import strawberry
import strawberry_django


__all__ = (
    'ContactAssignmentsMixin',
)


@strawberry.type
class ContactAssignmentsMixin:

    assignments: List[Annotated["ContactAssignmentType", strawberry.lazy('tenancy.graphql.types')]]
