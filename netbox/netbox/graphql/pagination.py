import strawberry
from strawberry.types.unset import UNSET
from strawberry_django.pagination import _QS, apply

__all__ = (
    'OffsetPaginationInfo',
    'OffsetPaginationInput',
    'apply_pagination',
)


@strawberry.type
class OffsetPaginationInfo:
    offset: int = 0
    limit: int | None = UNSET
    start: int | None = UNSET


@strawberry.input
class OffsetPaginationInput(OffsetPaginationInfo):
    """
    Customized implementation of OffsetPaginationInput to support cursor-based pagination.
    """
    pass


def apply_pagination(
    self,
    queryset: _QS,
    pagination: OffsetPaginationInput | None = None,
    *,
    related_field_id: str | None = None,
) -> _QS:
    """
    Replacement for the `apply_pagination()` method on StrawberryDjangoField to support cursor-based pagination.
    """
    if pagination is not None and pagination.start not in (None, UNSET):
        if pagination.offset:
            raise ValueError('Cannot specify both `start` and `offset` in pagination.')
        if pagination.start < 0:
            raise ValueError('`start` must be greater than or equal to zero.')

        # Filter the queryset to include only records with a primary key greater than or equal to the start value,
        # and force ordering by primary key to ensure consistent pagination across all records.
        queryset = queryset.filter(pk__gte=pagination.start).order_by('pk')

        # Ignore `offset` when `start` is set
        pagination.offset = 0

    return apply(pagination, queryset, related_field_id=related_field_id)
