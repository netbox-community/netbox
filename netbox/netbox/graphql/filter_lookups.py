import re
from enum import Enum
from typing import Generic, TypeVar

import strawberry
import strawberry_django
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q, QuerySet
from django.db.models.fields.related import ForeignKey, ManyToManyField, ManyToManyRel, ManyToOneRel
from strawberry import ID
from strawberry.directive import DirectiveValue
from strawberry.types import Info
from strawberry_django import (
    ComparisonFilterLookup,
    DateFilterLookup,
    DatetimeFilterLookup,
    FilterLookup,
    RangeLookup,
    TimeFilterLookup,
    process_filters,
)

from netbox.graphql.scalars import BigInt

# ------------------------------------------------------------------
# JSON path validation (VM-323)
# ------------------------------------------------------------------

# Each segment of a JSON path may only contain alphanumerics, hyphens, and
# underscores.  Hyphens are included because JSON keys commonly use them.
_JSON_PATH_SEGMENT_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_-]*$')

# Django ORM lookup operator names that must not appear as JSON path segments.
# An attacker supplying path="key__regex" would otherwise suffix the ORM
# lookup with a regex operator, turning it into a per-character boolean oracle.
_ORM_OPERATOR_NAMES = frozenset({
    'exact', 'iexact', 'contains', 'icontains', 'in', 'gt', 'gte', 'lt', 'lte',
    'startswith', 'istartswith', 'endswith', 'iendswith', 'range', 'date',
    'year', 'iso_year', 'month', 'day', 'week', 'week_day', 'iso_week_day',
    'quarter', 'time', 'hour', 'minute', 'second', 'isnull', 'regex', 'iregex',
    'has_key', 'has_any_keys', 'has_keys', 'contained_by', 'overlap',
})


def _validate_json_path(path: str) -> str:
    """
    Validate and return a safe JSON traversal path for use in ORM lookups.

    The path may be a single key or a ``__``-separated sequence for nested
    traversal.  Each segment must consist only of alphanumerics, hyphens, and
    underscores, and must not be a Django ORM operator keyword (which would
    otherwise permit regex-oracle or operator-injection attacks).

    Returns the sanitised path string.  Raises ``ValueError`` on any violation.
    """
    path = path.strip('_')
    if not path:
        raise ValueError("JSON path cannot be empty")

    for segment in path.split('__'):
        if not segment:
            raise ValueError("JSON path contains consecutive or trailing '__'")
        if not _JSON_PATH_SEGMENT_RE.match(segment):
            raise ValueError(f"Invalid JSON path segment: {segment!r}")
        if segment.lower() in _ORM_OPERATOR_NAMES:
            raise ValueError(f"JSON path segment is a reserved ORM operator: {segment!r}")

    return path


__all__ = (
    'ArrayLookup',
    'BigIntegerLookup',
    'FloatArrayLookup',
    'FloatLookup',
    'IntegerArrayLookup',
    'IntegerLookup',
    'IntegerRangeArrayLookup',
    'JSONFilter',
    'JSONLookup',
    'JSONStringLookup',
    'StringArrayLookup',
    'TreeNodeFilter',
)

T = TypeVar('T')
SKIP_MSG = 'Filter will be skipped on `null` value'


@strawberry.input(description='String lookups for JSON field values. Regex excluded to prevent oracle attacks.')
class JSONStringLookup:
    """
    Restricted string-filter type for use inside JSONLookup.

    ``StrFilterLookup`` includes ``regex`` and ``i_regex`` operators, which
    combined with JSONFilter.path form a per-character boolean oracle over any
    JSONField the querying user can read.  This type omits those operators.
    """
    exact: str | None = strawberry_django.filter_field()
    i_exact: str | None = strawberry_django.filter_field()
    contains: str | None = strawberry_django.filter_field()
    i_contains: str | None = strawberry_django.filter_field()
    starts_with: str | None = strawberry_django.filter_field()
    i_starts_with: str | None = strawberry_django.filter_field()
    ends_with: str | None = strawberry_django.filter_field()
    i_ends_with: str | None = strawberry_django.filter_field()
    in_: list[str] | None = strawberry_django.filter_field()
    isnull: bool | None = strawberry_django.filter_field()
    # regex / i_regex intentionally omitted (oracle prevention, VM-323)


@strawberry.input(one_of=True, description='Lookup for JSON field. Only one of the lookup fields can be set.')
class JSONLookup:
    string_lookup: JSONStringLookup | None = strawberry_django.filter_field()
    int_range_lookup: RangeLookup[int] | None = strawberry_django.filter_field()
    int_comparison_lookup: ComparisonFilterLookup[int] | None = strawberry_django.filter_field()
    float_range_lookup: RangeLookup[float] | None = strawberry_django.filter_field()
    float_comparison_lookup: ComparisonFilterLookup[float] | None = strawberry_django.filter_field()
    date_lookup: DateFilterLookup[str] | None = strawberry_django.filter_field()
    datetime_lookup: DatetimeFilterLookup[str] | None = strawberry_django.filter_field()
    time_lookup: TimeFilterLookup[str] | None = strawberry_django.filter_field()
    boolean_lookup: FilterLookup[bool] | None = strawberry_django.filter_field()

    def get_filter(self):
        for field in self.__strawberry_definition__.fields:
            value = getattr(self, field.name, None)
            if value is not strawberry.UNSET:
                return value
        return None


class _NumericLookupMixin:
    """Shared filter logic for numeric lookup input types (Integer, BigInteger, Float)."""

    def get_filter(self):
        for field in self.__strawberry_definition__.fields:
            value = getattr(self, field.name, None)
            if value is not strawberry.UNSET:
                return value
        return None

    @strawberry_django.filter_field
    def filter(self, info: Info, queryset: QuerySet, prefix: DirectiveValue[str] = '') -> tuple[QuerySet, Q]:
        filters = self.get_filter()

        if not filters:
            return queryset, Q()

        if isinstance(filters, RangeLookup):
            prefix = f'{prefix}range__'

        return process_filters(filters=filters, queryset=queryset, info=info, prefix=prefix)


@strawberry.input(one_of=True, description='Lookup for Integer fields. Only one of the lookup fields can be set.')
class IntegerLookup(_NumericLookupMixin):
    filter_lookup: FilterLookup[int] | None = strawberry_django.filter_field()
    range_lookup: RangeLookup[int] | None = strawberry_django.filter_field()
    comparison_lookup: ComparisonFilterLookup[int] | None = strawberry_django.filter_field()


@strawberry.input(one_of=True, description='Lookup for BigInteger fields. Only one of the lookup fields can be set.')
class BigIntegerLookup(_NumericLookupMixin):
    filter_lookup: FilterLookup[BigInt] | None = strawberry_django.filter_field()
    range_lookup: RangeLookup[BigInt] | None = strawberry_django.filter_field()
    comparison_lookup: ComparisonFilterLookup[BigInt] | None = strawberry_django.filter_field()


@strawberry.input(one_of=True, description='Lookup for Float fields. Only one of the lookup fields can be set.')
class FloatLookup(_NumericLookupMixin):
    filter_lookup: FilterLookup[float] | None = strawberry_django.filter_field()
    range_lookup: RangeLookup[float] | None = strawberry_django.filter_field()
    comparison_lookup: ComparisonFilterLookup[float] | None = strawberry_django.filter_field()


@strawberry.input
class JSONFilter:
    """
    Class for JSON field lookups with paths
    """

    path: str
    lookup: JSONLookup

    @strawberry_django.filter_field
    def filter(self, info: Info, queryset: QuerySet, prefix: DirectiveValue[str] = '') -> tuple[QuerySet, Q]:
        filters = self.lookup.get_filter()

        if not filters:
            return queryset, Q()

        try:
            safe_path = _validate_json_path(self.path)
        except ValueError:
            # Invalid path — return no results rather than propagating user input
            # into the ORM lookup.
            return queryset, Q(pk__in=[])

        json_path = f'{prefix}{safe_path}__'
        return process_filters(filters=filters, queryset=queryset, info=info, prefix=json_path)


@strawberry.enum
class TreeNodeMatch(Enum):
    EXACT = 'exact'  # Just the node itself
    DESCENDANTS = 'descendants'  # Node and all descendants
    SELF_AND_DESCENDANTS = 'self_and_descendants'  # Node and all descendants
    CHILDREN = 'children'  # Just immediate children
    SIBLINGS = 'siblings'  # Nodes with same parent
    ANCESTORS = 'ancestors'  # All parent nodes
    PARENT = 'parent'  # Just immediate parent


@strawberry.input
class TreeNodeFilter:
    id: ID
    match_type: TreeNodeMatch

    @strawberry_django.filter_field
    def filter(self, info: Info, queryset: QuerySet, prefix: DirectiveValue[str] = '') -> tuple[QuerySet, Q]:
        model_field_name = prefix.removesuffix('__').removesuffix('_id')
        model_field = None
        try:
            model_field = queryset.model._meta.get_field(model_field_name)
        except FieldDoesNotExist:
            try:
                model_field = queryset.model._meta.get_field(f'{model_field_name}s')
            except FieldDoesNotExist:
                return queryset, Q(pk__in=[])

        if hasattr(model_field, 'related_model'):
            related_model = model_field.related_model
        else:
            return queryset, Q(pk__in=[])

        # Generate base Q filter for the related model without prefix
        q_filter = generate_tree_node_q_filter(related_model, self)

        # Handle different relationship types
        if isinstance(model_field, (ManyToManyField, ManyToManyRel)):
            return queryset, Q(**{f'{model_field_name}__in': related_model.objects.filter(q_filter)})
        if isinstance(model_field, ForeignKey):
            return queryset, Q(**{f'{model_field_name}__{k}': v for k, v in q_filter.children})
        if isinstance(model_field, ManyToOneRel):
            return queryset, Q(**{f'{model_field_name}__in': related_model.objects.filter(q_filter)})
        return queryset, Q(**{f'{model_field_name}__{k}': v for k, v in q_filter.children})


def generate_tree_node_q_filter(model_class, filter_value: TreeNodeFilter) -> Q:
    """
    Generate appropriate Q filter for MPTT tree filtering based on match type
    """
    try:
        node = model_class.objects.get(id=filter_value.id)
    except model_class.DoesNotExist:
        return Q(pk__in=[])

    if filter_value.match_type == TreeNodeMatch.EXACT:
        return Q(id=filter_value.id)
    if filter_value.match_type == TreeNodeMatch.DESCENDANTS:
        return Q(tree_id=node.tree_id, lft__gt=node.lft, rght__lt=node.rght)
    if filter_value.match_type == TreeNodeMatch.SELF_AND_DESCENDANTS:
        return Q(tree_id=node.tree_id, lft__gte=node.lft, rght__lte=node.rght)
    if filter_value.match_type == TreeNodeMatch.CHILDREN:
        return Q(tree_id=node.tree_id, level=node.level + 1, lft__gt=node.lft, rght__lt=node.rght)
    if filter_value.match_type == TreeNodeMatch.SIBLINGS:
        return Q(tree_id=node.tree_id, level=node.level, parent=node.parent) & ~Q(id=node.id)
    if filter_value.match_type == TreeNodeMatch.ANCESTORS:
        return Q(tree_id=node.tree_id, lft__lt=node.lft, rght__gt=node.rght)
    if filter_value.match_type == TreeNodeMatch.PARENT:
        return Q(id=node.parent_id) if node.parent_id else Q(pk__in=[])
    return Q()


@strawberry.input(one_of=True, description='Lookup for Array fields. Only one of the lookup fields can be set.')
class ArrayLookup(Generic[T]):
    """
    Class for Array field lookups
    """

    contains: list[T] | None = strawberry_django.filter_field(description='Contains the value')
    contained_by: list[T] | None = strawberry_django.filter_field(description='Contained by the value')
    overlap: list[T] | None = strawberry_django.filter_field(description='Overlaps with the value')
    length: int | None = strawberry_django.filter_field(description='Length of the array')


@strawberry.input(one_of=True, description='Lookup for Array fields. Only one of the lookup fields can be set.')
class IntegerArrayLookup(ArrayLookup[int]):
    pass


@strawberry.input(one_of=True, description='Lookup for Array fields. Only one of the lookup fields can be set.')
class FloatArrayLookup(ArrayLookup[float]):
    pass


@strawberry.input(one_of=True, description='Lookup for Array fields. Only one of the lookup fields can be set.')
class StringArrayLookup(ArrayLookup[str]):
    pass


@strawberry.input(one_of=True, description='Lookups for an ArrayField(RangeField). Only one may be set.')
class RangeArrayValueLookup(Generic[T]):
    """
    class for Array field of Range fields lookups
    """

    contains: T | None = strawberry.field(
        default=strawberry.UNSET, description='Return rows where any stored range contains this value.'
    )

    @strawberry_django.filter_field
    def filter(self, info: Info, queryset: QuerySet, prefix: str = '') -> tuple[QuerySet, Q]:
        """
        Map GraphQL: { <field>: { contains: <T> } } To Django ORM: <field>__range_contains=<T>
        """
        if self.contains is strawberry.UNSET or self.contains is None:
            return queryset, Q()

        # Build '<prefix>range_contains' so it works for nested paths too
        return queryset, Q(**{f'{prefix}range_contains': self.contains})


@strawberry.input(one_of=True, description='Lookups for an ArrayField(IntegerRangeField). Only one may be set.')
class IntegerRangeArrayLookup(RangeArrayValueLookup[int]):
    pass
