import django_filters
from django import forms
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django_filters.constants import EMPTY_VALUES
from django_filters.utils import get_model_field
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field

from .forms.fields import BigIntegerField

__all__ = (
    'ContentTypeFilter',
    'MultiValueArrayFilter',
    'MultiValueBigNumberFilter',
    'MultiValueCharFilter',
    'MultiValueContentTypeFilter',
    'MultiValueDateFilter',
    'MultiValueDateTimeFilter',
    'MultiValueDecimalFilter',
    'MultiValueMACAddressFilter',
    'MultiValueNumberFilter',
    'MultiValueTimeFilter',
    'MultiValueTimeZoneFilter',
    'MultiValueWWNFilter',
    'NullableCharFieldFilter',
    'NumericArrayFilter',
    'TreeNodeMultipleChoiceFilter',
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
            field = field_class()
            return [
                # Only append non-empty values (this avoids e.g. trying to cast '' as an integer)
                field.to_python(v) for v in value if v
            ]

        def run_validators(self, value):
            for v in value:
                super().run_validators(v)

        def validate(self, value):
            for v in value:
                super().validate(v)

    return type(f'MultiValue{field_class.__name__}', (NewField,), dict())


#
# Filters
#

@extend_schema_field(OpenApiTypes.STR)
class MultiValueCharFilter(django_filters.MultipleChoiceFilter):
    field_class = multivalue_field_factory(forms.CharField)


@extend_schema_field(OpenApiTypes.DATE)
class MultiValueDateFilter(django_filters.MultipleChoiceFilter):
    field_class = multivalue_field_factory(forms.DateField)


@extend_schema_field(OpenApiTypes.DATETIME)
class MultiValueDateTimeFilter(django_filters.MultipleChoiceFilter):
    field_class = multivalue_field_factory(forms.DateTimeField)


@extend_schema_field(OpenApiTypes.INT32)
class MultiValueNumberFilter(django_filters.MultipleChoiceFilter):
    field_class = multivalue_field_factory(forms.IntegerField)


@extend_schema_field(OpenApiTypes.INT64)
class MultiValueBigNumberFilter(MultiValueNumberFilter):
    field_class = multivalue_field_factory(BigIntegerField)


@extend_schema_field(OpenApiTypes.DECIMAL)
class MultiValueDecimalFilter(django_filters.MultipleChoiceFilter):
    field_class = multivalue_field_factory(forms.DecimalField)


@extend_schema_field(OpenApiTypes.TIME)
class MultiValueTimeFilter(django_filters.MultipleChoiceFilter):
    field_class = multivalue_field_factory(forms.TimeField)


@extend_schema_field(OpenApiTypes.STR)
class MultiValueArrayFilter(django_filters.MultipleChoiceFilter):
    field_class = multivalue_field_factory(forms.CharField)

    def __init__(self, *args, lookup_expr='contains', **kwargs):
        # Set default lookup_expr to 'contains'
        super().__init__(*args, lookup_expr=lookup_expr, **kwargs)

    def get_filter_predicate(self, v):
        # If filtering for null values, ignore lookup_expr
        if v is None:
            return {self.field_name: None}
        return super().get_filter_predicate(v)


class InvalidValueFilterMixin:
    """
    Reject a value which the model field cannot accept (e.g. a malformed MAC address) during validation, rather than
    raising an exception when the query is built. (The REST API returns a 400 response for such values.) Only lookups
    which pass the value to the model field (e.g. "exact") are validated; partial-match lookups (e.g. "icontains")
    accept any string.
    """
    @property
    def field(self):
        field = super().field
        # The model is assigned only once the filter has been bound to a FilterSet instance
        if getattr(self, 'model', None) is not None and not getattr(self, '_model_field_validated', False):
            self._model_field_validated = True
            model_field = get_model_field(self.model, self.field_name)
            lookup = model_field.get_lookup(self.lookup_expr) if model_field is not None else None
            if lookup is not None and lookup.prepare_rhs:
                field.validators.append(self._get_validator(model_field))
        return field

    def _get_validator(self, model_field):
        null_value = self.null_value

        def validator(value):
            # The null choice value is translated to None when filtering
            if value == null_value:
                return
            try:
                model_field.get_prep_value(value)
            except (OSError, TypeError, ValueError):
                # Some values are rejected with an exception other than ValidationError (e.g. zoneinfo raises a
                # ValueError for a time zone key which is not a normalized path)
                raise ValidationError(_('Invalid value: {value}').format(value=value))

        return validator


@extend_schema_field(OpenApiTypes.STR)
class MultiValueMACAddressFilter(InvalidValueFilterMixin, MultiValueCharFilter):
    pass


@extend_schema_field(OpenApiTypes.STR)
class MultiValueTimeZoneFilter(InvalidValueFilterMixin, MultiValueCharFilter):
    pass


@extend_schema_field(OpenApiTypes.STR)
class MultiValueWWNFilter(InvalidValueFilterMixin, MultiValueCharFilter):
    pass


@extend_schema_field(OpenApiTypes.STR)
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
    field_class = forms.IntegerField

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.lookup_expr == 'isnull':
            # The "empty" lookup takes a boolean value, to which numeric constraints do not apply
            self.field_class = forms.NullBooleanField
            for param in ('min_value', 'max_value', 'step_size'):
                self.extra.pop(param, None)

    def filter(self, qs, value):
        if value is None:
            return qs
        if self.lookup_expr == 'isnull':
            return super().filter(qs, value)
        return super().filter(qs, [value])


class ContentTypeFilter(django_filters.CharFilter):
    """
    Allow specifying a ContentType by <app_label>.<model> (e.g. "dcim.site").
    """
    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        try:
            app_label, model = value.lower().split('.')
            content_type = ContentType.objects.get_by_natural_key(app_label, model)
        except (ValueError, ContentType.DoesNotExist):
            return qs.none()
        return qs.filter(
            **{
                f'{self.field_name}': content_type,
            }
        )


class MultiValueContentTypeFilter(MultiValueCharFilter):
    """
    A multi-value version of ContentTypeFilter.
    """
    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        content_types = []
        for key in value:
            try:
                app_label, model = key.lower().split('.')
                ct = ContentType.objects.get_by_natural_key(app_label, model)
                content_types.append(ct)
            except (ValueError, ContentType.DoesNotExist):
                continue

        return qs.filter(
            **{
                f'{self.field_name}__in': content_types,
            }
        )
