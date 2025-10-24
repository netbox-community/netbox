from typing import Annotated, TYPE_CHECKING

import strawberry

if TYPE_CHECKING:
    from users.graphql.types import OwnerType

__all__ = (
    'OwnerMixin',
)


@strawberry.type
class OwnerMixin:
    owner: Annotated['OwnerType', strawberry.lazy('users.graphql.types')] | None
