import django_filters
from django import forms
from django.conf import settings
from django.db import models

from dcim.forms import MACAddressField
from extras.models import Tag


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
    def filter(self, qs, value):
        value = [node.get_descendants(include_self=True) for node in value]
        return super().filter(qs, value)


class NumericInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    """
    Filters for a set of numeric values. Example: id__in=100,200,300
    """
    pass


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


#
# FilterSets
#

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


#
# Update default filters
#

FILTER_DEFAULTS = django_filters.filterset.FILTER_FOR_DBFIELD_DEFAULTS
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
})
