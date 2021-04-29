import django_filters
from django.forms import DateField, IntegerField, NullBooleanField

from .choices import *

__all__ = (
    'CustomFieldFilter',
)

EXACT_FILTER_TYPES = (
    CustomFieldTypeChoices.TYPE_BOOLEAN,
    CustomFieldTypeChoices.TYPE_DATE,
    CustomFieldTypeChoices.TYPE_INTEGER,
    CustomFieldTypeChoices.TYPE_SELECT,
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

        if custom_field.type not in EXACT_FILTER_TYPES:
            if custom_field.filter_logic == CustomFieldFilterLogicChoices.FILTER_LOOSE:
                self.lookup_expr = 'icontains'
