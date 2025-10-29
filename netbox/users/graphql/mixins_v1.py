from typing import Annotated, TYPE_CHECKING

import strawberry

if TYPE_CHECKING:
    from users.graphql.types_v1 import OwnerTypeV1

__all__ = (
    'OwnerMixinV1',
)


@strawberry.type
class OwnerMixinV1:
    owner: Annotated['OwnerTypeV1', strawberry.lazy('users.graphql.types_v1')] | None
