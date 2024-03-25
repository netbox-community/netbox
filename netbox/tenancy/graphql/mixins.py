from typing import Annotated, List

import strawberry
import strawberry_django


__all__ = (
    'ContactAssignmentsMixin',
)


@strawberry.type
class ContactAssignmentsMixin:

    @strawberry_django.field
    def assignments(self) -> List[Annotated["ContactAssignmentType", strawberry.lazy('tenancy.graphql.types')]]:
        return self.assignments.all()
