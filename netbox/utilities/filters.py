import django_filters
from django_filters.constants import EMPTY_VALUES
from copy import deepcopy
from dcim.forms import MACAddressField
from django import forms
from django.conf import settings
from django.db import models
from django_filters.utils import get_model_field, resolve_field

from extras.models import Tag
from utilities.constants import (
    FILTER_CHAR_BASED_LOOKUP_MAP, FILTER_NEGATION_LOOKUP_MAP, FILTER_TREENODE_NEGATION_LOOKUP_MAP,
    FILTER_NUMERIC_BASED_LOOKUP_MAP
)


def multivalue_field_factory(field_class):
    """
    Given a form field class, return a subclass capable of accepting multiple values. This allows us to OR on multiple
    filter values while maintaining the field's built-in validation. Example: GET /api/dcim/devices/?name=foo&name=bar
    """
    class NewField(field_class):
        widget = forms.SelectMultiple

        def to_python(self, value):
            if not value:
                return []
            return [
                # Only append non-empty values (this avoids e.g. trying to cast '' as an integer)
                super(field_class, self).to_python(v) for v in value if v
            ]

    return type('MultiValue{}'.format(field_class.__name__), (NewField,), dict())


#
# Filters
#

class MultiValueCharFilter(django_filters.MultipleChoiceFilter):
    field_class = multivalue_field_factory(forms.CharField)


class MultiValueDateFilter(django_filters.MultipleChoiceFilter):
    field_class = multivalue_field_factory(forms.DateField)


class MultiValueDateTimeFilter(django_filters.MultipleChoiceFilter):
    field_class = multivalue_field_factory(forms.DateTimeField)


class MultiValueNumberFilter(django_filters.MultipleChoiceFilter):
    field_class = multivalue_field_factory(forms.IntegerField)


class MultiValueTimeFilter(django_filters.MultipleChoiceFilter):
    field_class = multivalue_field_factory(forms.TimeField)


class MACAddressFilter(django_filters.CharFilter):
    field_class = MACAddressField


class MultiValueMACAddressFilter(django_filters.MultipleChoiceFilter):
    field_class = multivalue_field_factory(MACAddressField)


class TreeNodeMultipleChoiceFilter(django_filters.ModelMultipleChoiceFilter):
    """
    Filters for a set of Models, including all descendant models within a Tree.  Example: [<Region: R1>,<Region: R2>]
    """
    def get_filter_predicate(self, v):
        # Null value filtering
        if v is None:
            return {f"{self.field_name}__isnull": True}
        return super().get_filter_predicate(v)

    def filter(self, qs, value):
        value = [node.get_descendants(include_self=True) if not isinstance(node, str) else node for node in value]
        return super().filter(qs, value)


class NullableCharFieldFilter(django_filters.CharFilter):
    """
    Allow matching on null field values by passing a special string used to signify NULL.
    """
    def filter(self, qs, value):
        if value != settings.FILTERS_NULL_CHOICE_VALUE:
            return super().filter(qs, value)
        qs = self.get_method(qs)(**{'{}__isnull'.format(self.field_name): True})
        return qs.distinct() if self.distinct else qs


class TagFilter(django_filters.ModelMultipleChoiceFilter):
    """
    Match on one or more assigned tags. If multiple tags are specified (e.g. ?tag=foo&tag=bar), the queryset is filtered
    to objects matching all tags.
    """
    def __init__(self, *args, **kwargs):

        kwargs.setdefault('field_name', 'tags__slug')
        kwargs.setdefault('to_field_name', 'slug')
        kwargs.setdefault('conjoined', True)
        kwargs.setdefault('queryset', Tag.objects.all())

        super().__init__(*args, **kwargs)


class NumericArrayFilter(django_filters.NumberFilter):
    """
    Filter based on the presence of an integer within an ArrayField.
    """
    def filter(self, qs, value):
        if value:
            value = [value]
        return super().filter(qs, value)


class ContentTypeFilter(django_filters.CharFilter):
    """
    Allow specifying a ContentType by <app_label>.<model> (e.g. "dcim.site").
    """
    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        try:
            app_label, model = value.lower().split('.')
        except ValueError:
            return qs.none()
        return qs.filter(
            **{
                f'{self.field_name}__app_label': app_label,
                f'{self.field_name}__model': model
            }
        )


#
# FilterSets
#

class BaseFilterSet(django_filters.FilterSet):
    """
    A base filterset which provides common functionaly to all NetBox filtersets
    """
    FILTER_DEFAULTS = deepcopy(django_filters.filterset.FILTER_FOR_DBFIELD_DEFAULTS)
    FILTER_DEFAULTS.update({
        models.AutoField: {
            'filter_class': MultiValueNumberFilter
        },
        models.CharField: {
            'filter_class': MultiValueCharFilter
        },
        models.DateField: {
            'filter_class': MultiValueDateFilter
        },
        models.DateTimeField: {
            'filter_class': MultiValueDateTimeFilter
        },
        models.DecimalField: {
            'filter_class': MultiValueNumberFilter
        },
        models.EmailField: {
            'filter_class': MultiValueCharFilter
        },
        models.FloatField: {
            'filter_class': MultiValueNumberFilter
        },
        models.IntegerField: {
            'filter_class': MultiValueNumberFilter
        },
        models.PositiveIntegerField: {
            'filter_class': MultiValueNumberFilter
        },
        models.PositiveSmallIntegerField: {
            'filter_class': MultiValueNumberFilter
        },
        models.SlugField: {
            'filter_class': MultiValueCharFilter
        },
        models.SmallIntegerField: {
            'filter_class': MultiValueNumberFilter
        },
        models.TimeField: {
            'filter_class': MultiValueTimeFilter
        },
        models.URLField: {
            'filter_class': MultiValueCharFilter
        },
        MACAddressField: {
            'filter_class': MultiValueMACAddressFilter
        },
    })

    @staticmethod
    def _get_filter_lookup_dict(existing_filter):
        # Choose the lookup expression map based on the filter type
        if isinstance(existing_filter, (
            MultiValueDateFilter,
            MultiValueDateTimeFilter,
            MultiValueNumberFilter,
            MultiValueTimeFilter
        )):
            lookup_map = FILTER_NUMERIC_BASED_LOOKUP_MAP

        elif isinstance(existing_filter, (
            TreeNodeMultipleChoiceFilter,
        )):
            # TreeNodeMultipleChoiceFilter only support negation but must maintain the `in` lookup expression
            lookup_map = FILTER_TREENODE_NEGATION_LOOKUP_MAP

        elif isinstance(existing_filter, (
            django_filters.ModelChoiceFilter,
            django_filters.ModelMultipleChoiceFilter,
            TagFilter
        )) or existing_filter.extra.get('choices'):
            # These filter types support only negation
            lookup_map = FILTER_NEGATION_LOOKUP_MAP

        elif isinstance(existing_filter, (
            django_filters.filters.CharFilter,
            django_filters.MultipleChoiceFilter,
            MultiValueCharFilter,
            MultiValueMACAddressFilter
        )):
            lookup_map = FILTER_CHAR_BASED_LOOKUP_MAP

        else:
            lookup_map = None

        return lookup_map

    @classmethod
    def get_filters(cls):
        """
        Override filter generation to support dynamic lookup expressions for certain filter types.

        For specific filter types, new filters are created based on defined lookup expressions in
        the form `<field_name>__<lookup_expr>`
        """
        filters = super().get_filters()

        new_filters = {}
        for existing_filter_name, existing_filter in filters.items():
            # Loop over existing filters to extract metadata by which to create new filters

            # If the filter makes use of a custom filter method or lookup expression skip it
            # as we cannot sanely handle these cases in a generic mannor
            if existing_filter.method is not None or existing_filter.lookup_expr not in ['exact', 'in']:
                continue

            # Choose the lookup expression map based on the filter type
            lookup_map = cls._get_filter_lookup_dict(existing_filter)
            if lookup_map is None:
                # Do not augment this filter type with more lookup expressions
                continue

            # Get properties of the existing filter for later use
            field_name = existing_filter.field_name
            field = get_model_field(cls._meta.model, field_name)

            # Create new filters for each lookup expression in the map
            for lookup_name, lookup_expr in lookup_map.items():
                new_filter_name = '{}__{}'.format(existing_filter_name, lookup_name)

                try:
                    if existing_filter_name in cls.declared_filters:
                        # The filter field has been explicity defined on the filterset class so we must manually
                        # create the new filter with the same type because there is no guarantee the defined type
                        # is the same as the default type for the field
                        resolve_field(field, lookup_expr)  # Will raise FieldLookupError if the lookup is invalid
                        new_filter = type(existing_filter)(
                            field_name=field_name,
                            lookup_expr=lookup_expr,
                            label=existing_filter.label,
                            exclude=existing_filter.exclude,
                            distinct=existing_filter.distinct,
                            **existing_filter.extra
                        )
                    else:
                        # The filter field is listed in Meta.fields so we can safely rely on default behaviour
                        # Will raise FieldLookupError if the lookup is invalid
                        new_filter = cls.filter_for_field(field, field_name, lookup_expr)
                except django_filters.exceptions.FieldLookupError:
                    # The filter could not be created because the lookup expression is not supported on the field
                    continue

                if lookup_name.startswith('n'):
                    # This is a negation filter which requires a queryset.exclude() clause
                    # Of course setting the negation of the existing filter's exclude attribute handles both cases
                    new_filter.exclude = not existing_filter.exclude

                new_filters[new_filter_name] = new_filter

        filters.update(new_filters)
        return filters


class NameSlugSearchFilterSet(django_filters.FilterSet):
    """
    A base class for adding the search method to models which only expose the `name` and `slug` fields
    """
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(slug__icontains=value)
        )
