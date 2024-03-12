from typing import List

import django_filters
import strawberry
import strawberry_django
from circuits import filtersets, models
from functools import partial, partialmethod, wraps
from strawberry import auto
from strawberry_django.filters import FilterLookup
from tenancy.graphql.filter_mixins import ContactModelFilterMixin, TenancyFilterMixin
from utilities.filters import *

from netbox.graphql.filter_mixins import NetBoxModelFilterMixin

__all__ = (
    'CircuitTerminationFilter',
    'CircuitFilter',
    'CircuitTypeFilter',
    'ProviderFilter',
    'ProviderAccountFilter',
    'ProviderNetworkFilter',
)

# def filter_by_filterset(self, queryset, key, cls, filterset):
#     breakpoint()
#     return filterset(data={key: getattr(cls, key)}, queryset=queryset).qs


def autotype_decorator(filterset):

    def wrapper(cls):
        cls.filterset = filterset
        fields = filterset.get_fields()
        print(f"fields: {fields}")
        for fieldname in fields.keys():
            if fieldname not in cls.__annotations__:
                cls.__annotations__[fieldname] = auto

        # fields = list(filterset.get_fields().keys())
        declared_filters = filterset.declared_filters
        print(f"declared_filters: {declared_filters}")
        print("")
        for fieldname, v in declared_filters.items():
            create_function = False
            attr_type = None
            print(f"{fieldname}: {v}")

            if isinstance(v, ContentTypeFilter):
                print("ContentTypeFilter")
            elif isinstance(v, MACAddressFilter):
                print("MACAddressFilter")
            elif isinstance(v, MultiValueArrayFilter):
                print("MultiValueArrayFilter")
            elif isinstance(v, MultiValueCharFilter):
                print("MultiValueCharFilter")
            elif isinstance(v, MultiValueDateFilter):
                print("MultiValueDateFilter")
            elif isinstance(v, MultiValueDateTimeFilter):
                print("MultiValueDateTimeFilter")
            elif isinstance(v, MultiValueDecimalFilter):
                print("MultiValueDecimalFilter")
            elif isinstance(v, MultiValueMACAddressFilter):
                print("MultiValueMACAddressFilter")
            elif isinstance(v, MultiValueNumberFilter):
                print("MultiValueNumberFilter")
            elif isinstance(v, MultiValueTimeFilter):
                print("MultiValueTimeFilter")
            elif isinstance(v, MultiValueWWNFilter):
                print("MultiValueWWNFilter")
            elif isinstance(v, NullableCharFieldFilter):
                print("NullableCharFieldFilter")
            elif isinstance(v, NumericArrayFilter):
                print("NumericArrayFilter")
            elif isinstance(v, TreeNodeMultipleChoiceFilter):
                print("TreeNodeMultipleChoiceFilter")

            elif issubclass(type(v), django_filters.CharFilter):
                print("CharFilter")
            elif issubclass(type(v), django_filters.UUIDFilter):
                print("UUIDFilter")
            elif issubclass(type(v), django_filters.BooleanFilter):
                print("BooleanFilter")
            elif issubclass(type(v), django_filters.ChoiceFilter):
                print("ChoiceFilter")
            elif issubclass(type(v), django_filters.TypedChoiceFilter):
                print("TypedChoiceFilter")
            elif issubclass(type(v), django_filters.DateFilter):
                print("DateFilter")
            elif issubclass(type(v), django_filters.TimeFilter):
                print("TimeFilter")
            elif issubclass(type(v), django_filters.DateTimeFilter):
                print("DateTimeFilter")
            elif issubclass(type(v), django_filters.IsoDateTimeFilter):
                print("IsoDateTimeFilter")
            elif issubclass(type(v), django_filters.DurationFilter):
                print("DurationFilter")
            elif issubclass(type(v), django_filters.ModelChoiceFilter):
                print("ModelChoiceFilter")
            elif issubclass(type(v), django_filters.ModelMultipleChoiceFilter):
                create_function = True
                attr_type = List[str] | None
                print("ModelMultipleChoiceFilter")
            elif issubclass(type(v), django_filters.NumberFilter):
                print("NumberFilter")
            elif issubclass(type(v), django_filters.NumericRangeFilter):
                print("NumericRangeFilter")
            elif issubclass(type(v), django_filters.RangeFilter):
                print("RangeFilter")
            elif issubclass(type(v), django_filters.DateRangeFilter):
                print("DateRangeFilter")
            elif issubclass(type(v), django_filters.DateFromToRangeFilter):
                print("DateFromToRangeFilter")
            elif issubclass(type(v), django_filters.DateTimeFromToRangeFilter):
                print("DateTimeFromToRangeFilter")
            elif issubclass(type(v), django_filters.IsoDateTimeFromToRangeFilter):
                print("IsoDateTimeFromToRangeFilter")
            elif issubclass(type(v), django_filters.TimeRangeFilter):
                print("TimeRangeFilter")
            elif issubclass(type(v), django_filters.AllValuesFilter):
                print("AllValuesFilter")
            elif issubclass(type(v), django_filters.AllValuesMultipleFilter):
                print("AllValuesMultipleFilter")
            elif issubclass(type(v), django_filters.LookupChoiceFilter):
                print("LookupChoiceFilter")
            elif issubclass(type(v), django_filters.BaseInFilter):
                print("BaseInFilter")
            elif issubclass(type(v), django_filters.BaseRangeFilter):
                print("BaseRangeFilter")
            elif issubclass(type(v), django_filters.OrderingFilter):
                print("OrderingFilter")
            elif issubclass(type(v), django_filters.TypedMultipleChoiceFilter):
                print("TypedMultipleChoiceFilter")
            elif issubclass(type(v), django_filters.MultipleChoiceFilter):
                print("MultipleChoiceFilter")
            else:
                print("unknown type!")

            if fieldname not in cls.__annotations__ and attr_type:
                print(f"adding {fieldname} to class")
                cls.__annotations__[fieldname] = attr_type

            fname = f"filter_{fieldname}"
            if create_function and not hasattr(cls, fname):
                print(f"creating function {fname}")
                filter_by_filterset = getattr(cls, 'filter_by_filterset')
                setattr(cls, fname, partialmethod(filter_by_filterset, key=fieldname))
                # setattr(cls, fname, partial(filter_by_filterset, key=fieldname, cls=cls, filterset=filterset))

        print("")
        return cls

    return wrapper


"""
class autotype_decorator(object):
    def __init__(self, filterset):
        self.filterset = filterset
    def __call__(self, cls):
        class Wrapped(cls):
            '''
            cls.filterset = filterset
            fields = filterset.get_fields()
            print(fields)
            fields = list(filterset.get_fields().keys())
            declared_filters = filterset.declared_filters
            print(declared_filters)
            fields.extend(list(filterset.declared_filters.keys()))
            for field in fields:
                print(field)

            '''
            print(f"cls: {cls}")
            print(f"self: {self}")
            vars()['cid'] = strawberry.unset.UnsetType
            # setattr(cls, 'cid', strawberry.unset.UnsetType)
            pass

        setattr(Wrapped, 'cid', strawberry.unset.UnsetType)
        print(f"hasattr: {hasattr(Wrapped, 'cid')}")
        print(Wrapped)
        return Wrapped
"""


@strawberry_django.filter(models.CircuitTermination, lookups=True)
class CircuitTerminationFilter(filtersets.CircuitTerminationFilterSet):
    id: auto
    term_side: auto
    port_speed: auto
    upstream_speed: auto
    xconnect_id: auto
    description: auto
    cable_end: auto
    # q: auto
    circuit_id: auto
    site_id: auto
    site: auto
    # provider_network_id: auto


@strawberry_django.filter(models.Circuit, lookups=True)
@autotype_decorator(filtersets.CircuitFilterSet)
class CircuitFilter:
    # class CircuitFilter(NetBoxModelFilterMixin, TenancyFilterMixin, ContactModelFilterMixin):

    def filter_by_filterset(self, queryset, key):
        return self.filterset(data={key: getattr(self, key)}, queryset=queryset).qs

    pass
    """
    # vars()['cid'] = strawberry.unset.UnsetType
    # cid: auto
    description: auto
    install_date: auto
    termination_date: auto
    commit_rate: auto

    provider_id: List[str] | None
    provider: List[str] | None
    provider_account_id: List[str] | None
    provider_network_id: List[str] | None
    type_id: List[str] | None
    type: List[str] | None
    status: auto
    region_id: List[str] | None
    region: List[str] | None
    site_group_id: List[str] | None
    site_group: List[str] | None
    site_id: List[str] | None
    site: List[str] | None

    def filter_provider_id(self, queryset):
        return self.filter_by_filterset(queryset, 'provider_id')

    def filter_provider(self, queryset):
        return self.filter_by_filterset(queryset, 'provider')

    def filter_provider_account_id(self, queryset):
        return self.filter_by_filterset(queryset, 'provider_account_id')

    def filter_provider_network_id(self, queryset):
        return self.filter_by_filterset(queryset, 'provider_network_id')

    def filter_type_id(self, queryset):
        return self.filter_by_filterset(queryset, 'type_id')

    def filter_type(self, queryset):
        return self.filter_by_filterset(queryset, 'type')

    def filter_region_id(self, queryset):
        return self.filter_by_filterset(queryset, 'region_id')

    def filter_region(self, queryset):
        return self.filter_by_filterset(queryset, 'region')

    def filter_site_group_id(self, queryset):
        return self.filter_by_filterset(queryset, 'site_group_id')

    def filter_site_group(self, queryset):
        return self.filter_by_filterset(queryset, 'site_group')

    def filter_site_id(self, queryset):
        return self.filter_by_filterset(queryset, 'site_id')

    def filter_site(self, queryset):
        return self.filter_by_filterset(queryset, 'site')
    """


# @strawberry_django.filter(models.Circuit, lookups=True)
# class CircuitFilter(filtersets.CircuitFilterSet):
#     id: auto
#     cid: auto
#     description: auto
#     install_date: auto
#     termination_date: auto
#     commit_rate: auto
#     provider_id: auto
#     provider: auto
#     provider_account_id: auto
#     # provider_network_id: auto
#     type_id: auto
#     type: auto
#     status: auto
#     # region_id: auto
#     # region: auto
#     # site_group_id: auto
#     # site_group: auto
#     # site_id: auto
#     # site: auto


@strawberry_django.filter(models.CircuitType, lookups=True)
class CircuitTypeFilter(filtersets.CircuitTypeFilterSet):
    id: auto
    name: auto
    slug: auto
    description: auto


@strawberry_django.filter(models.Provider, lookups=True)
class ProviderFilter(filtersets.ProviderFilterSet):
    id: auto
    name: auto
    slug: auto
    # region_id: auto
    # region: auto
    # site_group_id: auto
    # site_group: auto
    # site_id: auto
    # site: auto
    # asn_id: auto


@strawberry_django.filter(models.ProviderAccount, lookups=True)
class ProviderAccountFilter(filtersets.ProviderAccountFilterSet):
    id: auto
    name: auto
    account: auto
    description: auto
    # provider_id: auto
    # provider: auto


@strawberry_django.filter(models.ProviderNetwork, lookups=True)
class ProviderNetworkFilter(filtersets.ProviderNetworkFilterSet):
    id: auto
    name: auto
    service_id: auto
    description: auto
    # provider_id: auto
    # provider: auto
