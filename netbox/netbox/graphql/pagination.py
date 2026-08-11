import strawberry
from django.db import DEFAULT_DB_ALIAS
from django.db.models.functions import DenseRank
from strawberry.types.unset import UNSET
from strawberry_django.pagination import _QS, _PaginationWindow, _resolve_limit, apply

from netbox.config import get_config

__all__ = (
    'OffsetPaginationInfo',
    'OffsetPaginationInput',
    'apply_distinct_window_pagination',
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


def apply_distinct_window_pagination(
    queryset: _QS,
    *,
    related_field_id: str,
    offset: int = 0,
    limit: int | None = UNSET,
) -> _QS:
    """
    Replacement for strawberry-django's `apply_window_pagination()` for a queryset which has `DISTINCT`
    enabled, as is the case when a list field is filtered across a to-many relation with `DISTINCT: true`.

    SQL evaluates window functions before `DISTINCT`, so the `ROW_NUMBER()` annotation which
    strawberry-django uses to paginate a prefetched relation assigns a unique value to each of the
    duplicate rows produced by the join, and `DISTINCT` can never collapse them. `DENSE_RANK()` instead
    assigns the same rank to every row which compares equal under the window ordering, leaving the
    duplicate rows identical so that `DISTINCT` deduplicates them as intended. And because the rank is
    incremented only once per distinct row, the rows are numbered as if the duplicates were never there,
    keeping the pagination limit meaningful.
    """
    limit = _resolve_limit(limit)

    order_by = [
        expr
        for expr, _ in queryset.query.get_compiler(
            using=queryset._db or DEFAULT_DB_ALIAS
        ).get_order_by()
    ]
    # Order by the primary key as well, to ensure that two rows representing *different* objects can
    # never be assigned the same rank (and hence be counted only once against the limit).
    order_by.append('pk')

    # Note that we omit the `_strawberry_total_count` annotation which strawberry-django adds, as it
    # cannot be made accurate here: window functions are evaluated before `DISTINCT`, so it would count
    # the duplicate rows. strawberry-django's `get_total_count()` already disregards the annotation for
    # a queryset with `DISTINCT` enabled and falls back to `count()`, so computing it would be wasted
    # work: an extra window aggregate over every joined row.
    queryset = queryset.annotate(
        _strawberry_row_number=_PaginationWindow(
            DenseRank(),
            partition_by=related_field_id,
            order_by=order_by,
        ),
    )

    if offset:
        queryset = queryset.filter(_strawberry_row_number__gt=offset)
    if limit is not None and limit >= 0:
        queryset = queryset.filter(_strawberry_row_number__lte=offset + limit)

    return queryset


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

    # A prefetched relation is paginated with a window function, which is incompatible with the
    # `DISTINCT` applied by the filter layer. Fall back to our own implementation in that case.
    if pagination is not None and related_field_id is not None and queryset.query.distinct:
        return apply_distinct_window_pagination(
            queryset,
            related_field_id=related_field_id,
            offset=pagination.offset,
            limit=pagination.limit,
        )

    return apply(pagination, queryset, related_field_id=related_field_id)
