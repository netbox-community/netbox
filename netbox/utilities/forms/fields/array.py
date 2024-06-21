from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.db.backends.postgresql.psycopg_any import NumericRange
from django.utils.translation import gettext_lazy as _

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.help_text:
            self.help_text = _(
                "Specify one or more numeric ranges separated by commas "
                "Example: <code>1-5,20-30</code>"
            )

    def prepare_value(self, value):
        return ','.join([f"{val.lower}-{val.upper}" for val in value])

    def to_python(self, value):
        if not value:
            return ''
        ranges = value.split(",")
        values = []
        for dash_range in value.split(','):
            lower, upper = dash_range.split('-')
            values.append(NumericRange(int(lower), int(upper)))
        return values
