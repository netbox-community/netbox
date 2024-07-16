from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from utilities.data import ranges_to_string, string_to_ranges

from ..utils import parse_numeric_range

__all__ = (
    'NumericArrayField',
    'NumericRangeArrayField',
)


class NumericArrayField(SimpleArrayField):

    def clean(self, value):
        if value and not self.to_python(value):
            raise forms.ValidationError(
                _("Invalid list ({value}). Must be numeric and ranges must be in ascending order.").format(value=value)
            )
        return super().clean(value)

    def to_python(self, value):
        if not value:
            return []
        if isinstance(value, str):
            value = ','.join([str(n) for n in parse_numeric_range(value)])
        return super().to_python(value)


class NumericRangeArrayField(forms.CharField):
    """
    A field which allows for array of numeric ranges:
      Example: 1-5,7-20,30-50
    """
    def __init__(self, *args, help_text='', **kwargs):
        if not help_text:
            help_text = mark_safe(
                _("Specify one or more numeric ranges separated by commas. Example: " + "<code>1-5,20-30</code>")
            )
        super().__init__(*args, help_text=help_text, **kwargs)

    def clean(self, value):
        if value and not self.to_python(value):
            raise forms.ValidationError(
                _("Invalid ranges ({value}). Must be a range of integers in ascending order.").format(value=value)
            )
        return super().clean(value)

    def prepare_value(self, value):
        if isinstance(value, str):
            return value
        return ranges_to_string(value)

    def to_python(self, value):
        return string_to_ranges(value)
