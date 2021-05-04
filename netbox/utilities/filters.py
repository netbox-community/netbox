import django_filters
from django import forms
from django.conf import settings
from django_filters.constants import EMPTY_VALUES

from dcim.forms import MACAddressField


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
