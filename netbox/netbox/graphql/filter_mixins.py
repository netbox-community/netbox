from functools import partial, partialmethod, wraps
from typing import List

import django_filters
import strawberry
import strawberry_django
from strawberry import auto
from ipam.fields import ASNField
from netbox.graphql.scalars import BigInt
from utilities.fields import ColorField, CounterCacheField
from utilities.filters import *


def map_strawberry_type(field):
    should_create_function = False
    attr_type = None

    # NetBox Filter types - put base classes after derived classes
    if isinstance(field, ContentTypeFilter):
        should_create_function = True
        attr_type = str | None
    elif isinstance(field, MultiValueArrayFilter):
        pass
    elif isinstance(field, MultiValueCharFilter):
        should_create_function = True
        attr_type = List[str] | None
    elif isinstance(field, MultiValueDateFilter):
        attr_type = auto
    elif isinstance(field, MultiValueDateTimeFilter):
        attr_type = auto
    elif isinstance(field, MultiValueDecimalFilter):
        pass
    elif isinstance(field, MultiValueMACAddressFilter):
        should_create_function = True
        attr_type = List[str] | None
    elif isinstance(field, MultiValueNumberFilter):
        should_create_function = True
        attr_type = List[str] | None
    elif isinstance(field, MultiValueTimeFilter):
        pass
    elif isinstance(field, MultiValueWWNFilter):
        should_create_function = True
        attr_type = List[str] | None
    elif isinstance(field, NullableCharFieldFilter):
        pass
    elif isinstance(field, NumericArrayFilter):
        should_create_function = True
        attr_type = int
    elif isinstance(field, TreeNodeMultipleChoiceFilter):
        should_create_function = True
        attr_type = List[str] | None

    # From django_filters - ordering of these matters as base classes must
    # come after derived classes so the base class doesn't get matched first
    # a pass for the check (no attr_type) means we don't currently handle
    # or use that type
    elif issubclass(type(field), django_filters.OrderingFilter):
        pass
    elif issubclass(type(field), django_filters.BaseRangeFilter):
        pass
    elif issubclass(type(field), django_filters.BaseInFilter):
        pass
    elif issubclass(type(field), django_filters.LookupChoiceFilter):
        pass
    elif issubclass(type(field), django_filters.AllValuesMultipleFilter):
        pass
    elif issubclass(type(field), django_filters.AllValuesFilter):
        pass
    elif issubclass(type(field), django_filters.TimeRangeFilter):
        pass
    elif issubclass(type(field), django_filters.IsoDateTimeFromToRangeFilter):
        should_create_function = True
        attr_type = str | None
    elif issubclass(type(field), django_filters.DateTimeFromToRangeFilter):
        should_create_function = True
        attr_type = str | None
    elif issubclass(type(field), django_filters.DateFromToRangeFilter):
        should_create_function = True
        attr_type = str | None
    elif issubclass(type(field), django_filters.DateRangeFilter):
        should_create_function = True
        attr_type = str | None
    elif issubclass(type(field), django_filters.RangeFilter):
        pass
    elif issubclass(type(field), django_filters.NumericRangeFilter):
        pass
    elif issubclass(type(field), django_filters.NumberFilter):
        should_create_function = True
        attr_type = int
    elif issubclass(type(field), django_filters.ModelMultipleChoiceFilter):
        should_create_function = True
        attr_type = List[str] | None
    elif issubclass(type(field), django_filters.ModelChoiceFilter):
        should_create_function = True
        attr_type = str | None
    elif issubclass(type(field), django_filters.DurationFilter):
        pass
    elif issubclass(type(field), django_filters.IsoDateTimeFilter):
        pass
    elif issubclass(type(field), django_filters.DateTimeFilter):
        attr_type = auto
    elif issubclass(type(field), django_filters.TimeFilter):
        attr_type = auto
    elif issubclass(type(field), django_filters.DateFilter):
        attr_type = auto
    elif issubclass(type(field), django_filters.TypedMultipleChoiceFilter):
        pass
    elif issubclass(type(field), django_filters.MultipleChoiceFilter):
        should_create_function = True
        attr_type = List[str] | None
    elif issubclass(type(field), django_filters.TypedChoiceFilter):
        pass
    elif issubclass(type(field), django_filters.ChoiceFilter):
        pass
    elif issubclass(type(field), django_filters.BooleanFilter):
        should_create_function = True
        attr_type = bool | None
    elif issubclass(type(field), django_filters.UUIDFilter):
        should_create_function = True
        attr_type = str | None
    elif issubclass(type(field), django_filters.CharFilter):
        # looks like only used by 'q'
        should_create_function = True
        attr_type = str | None

    return should_create_function, attr_type


def autotype_decorator(filterset):
    """
    Decorator used to auto creates a dataclass used by Strawberry based on a filterset.
    Must go after the Strawberry decorator as follows:

    @strawberry_django.filter(models.Example, lookups=True)
    @autotype_decorator(filtersets.ExampleFilterSet)
    class ExampleFilter(BaseFilterMixin):
        pass

    The Filter itself must be derived from BaseFilterMixin.  For items listed in meta.fields
    of the filterset, usually just a type specifier is generated, so for
    `fields = [created, ]` the dataclass would be:

    class ExampleFilter(BaseFilterMixin):
        created: auto

    For other filter fields a function needs to be created for Strawberry with the
    naming convention `filter_{fieldname}` which is auto detected and called by
    Strawberry, this function uses the filterset to handle the query.
    """
    def create_attribute_and_function(cls, fieldname, attr_type, should_create_function):
        if fieldname not in cls.__annotations__ and attr_type:
            cls.__annotations__[fieldname] = attr_type

        filter_name = f"filter_{fieldname}"
        if should_create_function and not hasattr(cls, filter_name):
            filter_by_filterset = getattr(cls, 'filter_by_filterset')
            setattr(cls, filter_name, partialmethod(filter_by_filterset, key=fieldname))

    def wrapper(cls):
        cls.filterset = filterset
        fields = filterset.get_fields()
        model = filterset._meta.model
        for fieldname in fields.keys():
            should_create_function = False
            attr_type = auto
            if fieldname not in cls.__annotations__:
                field = model._meta.get_field(fieldname)
                if isinstance(field, CounterCacheField):
                    should_create_function = True
                    attr_type = BigInt | None
                elif isinstance(field, ASNField):
                    should_create_function = True
                    attr_type = List[str] | None
                elif isinstance(field, ColorField):
                    should_create_function = True
                    attr_type = List[str] | None

                create_attribute_and_function(cls, fieldname, attr_type, should_create_function)

        declared_filters = filterset.declared_filters
        for fieldname, field in declared_filters.items():

            should_create_function, attr_type = map_strawberry_type(field)
            if attr_type is None:
                raise NotImplementedError(f"GraphQL Filter field unknown: {fieldname}: {field}")

            create_attribute_and_function(cls, fieldname, attr_type, should_create_function)

        return cls

    return wrapper


@strawberry.input
class BaseFilterMixin:

    def filter_by_filterset(self, queryset, key):
        return self.filterset(data={key: getattr(self, key)}, queryset=queryset).qs
