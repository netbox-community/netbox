import django_filters
from django.forms import DateField, IntegerField, NullBooleanField

from .models import Tag
from .choices import *

__all__ = (
    'CustomFieldFilter',
    'TagFilter',
)

EXACT_FILTER_TYPES = (
    CustomFieldTypeChoices.TYPE_BOOLEAN,
    CustomFieldTypeChoices.TYPE_DATE,
    CustomFieldTypeChoices.TYPE_INTEGER,
    CustomFieldTypeChoices.TYPE_SELECT,
    CustomFieldTypeChoices.TYPE_MULTISELECT,
)


class CustomFieldFilter(django_filters.Filter):
    """
    Filter objects by the presence of a CustomFieldValue. The filter's name is used as the CustomField name.
    """
    def __init__(self, custom_field, *args, **kwargs):
        self.custom_field = custom_field

        if custom_field.type == CustomFieldTypeChoices.TYPE_INTEGER:
            self.field_class = IntegerField
        elif custom_field.type == CustomFieldTypeChoices.TYPE_BOOLEAN:
            self.field_class = NullBooleanField
        elif custom_field.type == CustomFieldTypeChoices.TYPE_DATE:
            self.field_class = DateField

        super().__init__(*args, **kwargs)

        self.field_name = f'custom_field_data__{self.field_name}'

        if custom_field.type == CustomFieldTypeChoices.TYPE_MULTISELECT:
            self.lookup_expr = 'has_key'
        elif custom_field.type not in EXACT_FILTER_TYPES:
            if custom_field.filter_logic == CustomFieldFilterLogicChoices.FILTER_LOOSE:
                self.lookup_expr = 'icontains'


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
