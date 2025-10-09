from enum import Enum
from typing import TypeVar, Tuple, Generic

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

__all__ = (
    'ArrayLookup',
    'FloatArrayLookup',
    'FloatLookup',
    'IntegerArrayLookup',
    'IntegerLookup',
    'IntegerRangeArrayLookup',
    'JSONFilter',
    'StringArrayLookup',
    'TreeNodeFilter',
)

T = TypeVar('T')
SKIP_MSG = 'Filter will be skipped on `null` value'


@strawberry.input(one_of=True, description='Lookup for JSON field. Only one of the lookup fields can be set.')
class JSONLookup:
    string_lookup: FilterLookup[str] | None = strawberry_django.filter_field()
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


@strawberry.input(one_of=True, description='Lookup for Integer fields. Only one of the lookup fields can be set.')
class IntegerLookup:
    filter_lookup: FilterLookup[int] | None = strawberry_django.filter_field()
    range_lookup: RangeLookup[int] | None = strawberry_django.filter_field()
    comparison_lookup: ComparisonFilterLookup[int] | None = strawberry_django.filter_field()

    def get_filter(self):
        for field in self.__strawberry_definition__.fields:
            value = getattr(self, field.name, None)
            if value is not strawberry.UNSET:
                return value
        return None

    @strawberry_django.filter_field
    def filter(self, info: Info, queryset: QuerySet, prefix: DirectiveValue[str] = '') -> Tuple[QuerySet, Q]:
        filters = self.get_filter()

        if not filters:
            return queryset, Q()

        return process_filters(filters=filters, queryset=queryset, info=info, prefix=prefix)


@strawberry.input(one_of=True, description='Lookup for Float fields. Only one of the lookup fields can be set.')
class FloatLookup:
    filter_lookup: FilterLookup[float] | None = strawberry_django.filter_field()
    range_lookup: RangeLookup[float] | None = strawberry_django.filter_field()
    comparison_lookup: ComparisonFilterLookup[float] | None = strawberry_django.filter_field()

    def get_filter(self):
        for field in self.__strawberry_definition__.fields:
            value = getattr(self, field.name, None)
            if value is not strawberry.UNSET:
                return value
        return None

    @strawberry_django.filter_field
    def filter(self, info: Info, queryset: QuerySet, prefix: DirectiveValue[str] = '') -> Tuple[QuerySet, Q]:
        filters = self.get_filter()

        if not filters:
            return queryset, Q()

        return process_filters(filters=filters, queryset=queryset, info=info, prefix=prefix)


@strawberry.input
class JSONFilter:
    """
    Class for JSON field lookups with paths
    """

    path: str
    lookup: JSONLookup

    @strawberry_django.filter_field
    def filter(self, info: Info, queryset: QuerySet, prefix: DirectiveValue[str] = '') -> Tuple[QuerySet, Q]:
        filters = self.lookup.get_filter()

        if not filters:
            return queryset, Q()

        json_path = f'{prefix}{self.path}__'
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
    def filter(self, info: Info, queryset: QuerySet, prefix: DirectiveValue[str] = '') -> Tuple[QuerySet, Q]:
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
        elif isinstance(model_field, ForeignKey):
            return queryset, Q(**{f'{model_field_name}__{k}': v for k, v in q_filter.children})
        elif isinstance(model_field, ManyToOneRel):
            return queryset, Q(**{f'{model_field_name}__in': related_model.objects.filter(q_filter)})
        else:
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
    elif filter_value.match_type == TreeNodeMatch.DESCENDANTS:
        return Q(tree_id=node.tree_id, lft__gt=node.lft, rght__lt=node.rght)
    elif filter_value.match_type == TreeNodeMatch.SELF_AND_DESCENDANTS:
        return Q(tree_id=node.tree_id, lft__gte=node.lft, rght__lte=node.rght)
    elif filter_value.match_type == TreeNodeMatch.CHILDREN:
        return Q(tree_id=node.tree_id, level=node.level + 1, lft__gt=node.lft, rght__lt=node.rght)
    elif filter_value.match_type == TreeNodeMatch.SIBLINGS:
        return Q(tree_id=node.tree_id, level=node.level, parent=node.parent) & ~Q(id=node.id)
    elif filter_value.match_type == TreeNodeMatch.ANCESTORS:
        return Q(tree_id=node.tree_id, lft__lt=node.lft, rght__gt=node.rght)
    elif filter_value.match_type == TreeNodeMatch.PARENT:
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
    def filter(self, info: Info, queryset: QuerySet, prefix: str = '') -> Tuple[QuerySet, Q]:
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
