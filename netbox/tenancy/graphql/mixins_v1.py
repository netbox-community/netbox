from typing import Annotated, List

import strawberry

__all__ = (
    'ContactAssignmentsMixinV1',
)


@strawberry.type
class ContactAssignmentsMixinV1:
    assignments: List[Annotated["ContactAssignmentTypeV1", strawberry.lazy('tenancy.graphql.types_v1')]]  # noqa: F821
