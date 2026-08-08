import strawberry
from strawberry.types.unset import UNSET
from strawberry_django.pagination import _QS, apply

from netbox.config import get_config

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

    # Enforce MAX_PAGE_SIZE on the pagination limit
    max_page_size = get_config().MAX_PAGE_SIZE
    if max_page_size:
        # A limit is meaningless for a field which returns at most one object, and synthesizing one for a
        # prefetched to-one relation is actively harmful. strawberry-django deliberately leaves `pagination`
        # as None there so that the prefetch remains a plain `WHERE id IN (...)` query; making it non-None
        # switches the prefetch to a window function partitioned by the parent ID. Every partition then
        # holds exactly one row, so ROW_NUMBER() is 1 throughout and the row number filter discards nothing,
        # causing the join back to the parent table to return every row which shares the related object.
        # See strawberry-graphql/strawberry-django#719.
        returns_single_object = not (self.is_list or self.is_paginated or self.is_connection)

        if pagination is None:
            # Note that `pagination` is never None for a single-object field unless it is a prefetched
            # relation: strawberry-django populates it with an implicit limit of its own beforehand.
            if not returns_single_object:
                pagination = OffsetPaginationInput(limit=max_page_size)
        elif pagination.limit in (None, UNSET) or pagination.limit > max_page_size:
            pagination.limit = max_page_size
        elif pagination.limit <= 0:
            pagination.limit = max_page_size

    return apply(pagination, queryset, related_field_id=related_field_id)
