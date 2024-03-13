from functools import partial, partialmethod, wraps
from typing import List

import django_filters
import strawberry
import strawberry_django
from strawberry import auto
from utilities.fields import ColorField
from utilities.filters import *


def autotype_decorator(filterset):

    def wrapper(cls):
        print(f"cls: {cls}")
        cls.filterset = filterset
        fields = filterset.get_fields()
        model = filterset._meta.model
        for fieldname in fields.keys():
            attr_type = auto
            if fieldname not in cls.__annotations__:
                field = model._meta.get_field(fieldname)
                if isinstance(field, ColorField):
                    attr_type = List[str] | None

                cls.__annotations__[fieldname] = attr_type

        declared_filters = filterset.declared_filters
        for fieldname, v in declared_filters.items():
            create_function = False
            attr_type = None

            # NetBox Filter types - put base classes after derived classes
            if isinstance(v, ContentTypeFilter):
                create_function = True
                attr_type = str | None
            elif isinstance(v, MACAddressFilter):
                print(f"{fieldname}: {v}")
                print("MACAddressFilter")
            elif isinstance(v, MultiValueArrayFilter):
                print(f"{fieldname}: {v}")
                print("MultiValueArrayFilter")
            elif isinstance(v, MultiValueCharFilter):
                create_function = True
                attr_type = List[str] | None
            elif isinstance(v, MultiValueDateFilter):
                attr_type = auto
            elif isinstance(v, MultiValueDateTimeFilter):
                attr_type = auto
            elif isinstance(v, MultiValueDecimalFilter):
                print(f"{fieldname}: {v}")
                print("MultiValueDecimalFilter")
            elif isinstance(v, MultiValueMACAddressFilter):
                create_function = True
                attr_type = List[str] | None
            elif isinstance(v, MultiValueNumberFilter):
                create_function = True
                attr_type = List[str] | None
            elif isinstance(v, MultiValueTimeFilter):
                print(f"{fieldname}: {v}")
                print("MultiValueTimeFilter")
            elif isinstance(v, MultiValueWWNFilter):
                create_function = True
                attr_type = List[str] | None
            elif isinstance(v, NullableCharFieldFilter):
                print(f"{fieldname}: {v}")
                print("NullableCharFieldFilter")
            elif isinstance(v, NumericArrayFilter):
                print(f"{fieldname}: {v}")
                print("NumericArrayFilter")
            elif isinstance(v, TreeNodeMultipleChoiceFilter):
                create_function = True
                attr_type = List[str] | None

            # From django_filters - ordering of these matters as base classes must
            # come after derived classes so the base class doesn't get matched first
            elif issubclass(type(v), django_filters.OrderingFilter):
                print(f"{fieldname}: {v}")
                print("OrderingFilter")
            elif issubclass(type(v), django_filters.BaseRangeFilter):
                print(f"{fieldname}: {v}")
                print("BaseRangeFilter")
            elif issubclass(type(v), django_filters.BaseInFilter):
                print(f"{fieldname}: {v}")
                print("BaseInFilter")
            elif issubclass(type(v), django_filters.LookupChoiceFilter):
                print(f"{fieldname}: {v}")
                print("LookupChoiceFilter")
            elif issubclass(type(v), django_filters.AllValuesMultipleFilter):
                print(f"{fieldname}: {v}")
                print("AllValuesMultipleFilter")
            elif issubclass(type(v), django_filters.AllValuesFilter):
                print(f"{fieldname}: {v}")
                print("AllValuesFilter")
            elif issubclass(type(v), django_filters.TimeRangeFilter):
                print(f"{fieldname}: {v}")
                print("TimeRangeFilter")
            elif issubclass(type(v), django_filters.IsoDateTimeFromToRangeFilter):
                create_function = True
                attr_type = str | None
            elif issubclass(type(v), django_filters.DateTimeFromToRangeFilter):
                create_function = True
                attr_type = str | None
            elif issubclass(type(v), django_filters.DateFromToRangeFilter):
                create_function = True
                attr_type = str | None
            elif issubclass(type(v), django_filters.DateRangeFilter):
                create_function = True
                attr_type = str | None
            elif issubclass(type(v), django_filters.RangeFilter):
                print(f"{fieldname}: {v}")
                print("RangeFilter")
            elif issubclass(type(v), django_filters.NumericRangeFilter):
                print(f"{fieldname}: {v}")
                print("NumericRangeFilter")
            elif issubclass(type(v), django_filters.NumberFilter):
                print(f"{fieldname}: {v}")
                print("NumberFilter")
            elif issubclass(type(v), django_filters.ModelMultipleChoiceFilter):
                create_function = True
                attr_type = List[str] | None
            elif issubclass(type(v), django_filters.ModelChoiceFilter):
                create_function = True
                attr_type = str | None
            elif issubclass(type(v), django_filters.DurationFilter):
                print(f"{fieldname}: {v}")
                print("DurationFilter")
            elif issubclass(type(v), django_filters.IsoDateTimeFilter):
                print(f"{fieldname}: {v}")
                print("IsoDateTimeFilter")
            elif issubclass(type(v), django_filters.DateTimeFilter):
                attr_type = auto
            elif issubclass(type(v), django_filters.TimeFilter):
                attr_type = auto
            elif issubclass(type(v), django_filters.DateFilter):
                attr_type = auto
            elif issubclass(type(v), django_filters.TypedMultipleChoiceFilter):
                print(f"{fieldname}: {v}")
                print("TypedMultipleChoiceFilter")
            elif issubclass(type(v), django_filters.MultipleChoiceFilter):
                create_function = True
                attr_type = List[str] | None
            elif issubclass(type(v), django_filters.TypedChoiceFilter):
                print(f"{fieldname}: {v}")
                print("TypedChoiceFilter")
            elif issubclass(type(v), django_filters.ChoiceFilter):
                print(f"{fieldname}: {v}")
                print("ChoiceFilter")
            elif issubclass(type(v), django_filters.BooleanFilter):
                create_function = True
                attr_type = bool | None
            elif issubclass(type(v), django_filters.UUIDFilter):
                create_function = True
                attr_type = str | None
            elif issubclass(type(v), django_filters.CharFilter):
                # looks like only used by 'q'
                create_function = True
                attr_type = str | None
            else:
                print(f"{fieldname}: {v}")
                print("unknown type!")

            if fieldname not in cls.__annotations__ and attr_type:
                cls.__annotations__[fieldname] = attr_type

            fname = f"filter_{fieldname}"
            if create_function and not hasattr(cls, fname):
                filter_by_filterset = getattr(cls, 'filter_by_filterset')
                setattr(cls, fname, partialmethod(filter_by_filterset, key=fieldname))

        return cls

    return wrapper


@strawberry.input
class BaseFilterMixin:

    def filter_by_filterset(self, queryset, key):
        return self.filterset(data={key: getattr(self, key)}, queryset=queryset).qs


@strawberry.input
class ChangeLoggedModelFilterMixin(BaseFilterMixin):
    created: auto
    last_updated: auto
    created_by_request: str | None
    updated_by_request: str | None
    modified_by_request: str | None

    def filter_created_by_request(self, queryset):
        return self.filter_by_filterset(queryset, 'created_by_request')

    def filter_updated_by_request(self, queryset):
        return self.filter_by_filterset(queryset, 'updated_by_request')

    def filter_modified_by_request(self, queryset):
        return self.filter_by_filterset(queryset, 'modified_by_request')


@strawberry.input
class NetBoxModelFilterMixin(ChangeLoggedModelFilterMixin):
    q: str | None
    tag: List[str] | None

    def filter_q(self, queryset):
        # return self.search(queryset, None, self.q)
        return self.filter_by_filterset(queryset, 'q')

    def filter_tag(self, queryset, info):
        # return self.filterset(data={'tag': self.tag}, queryset=queryset).qs
        # return self.filterset(data={'tag': getattr(self, 'tag')}, queryset=queryset).qs
        return self.filter_by_filterset(queryset, 'tag')
