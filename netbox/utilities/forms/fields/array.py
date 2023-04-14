from django import forms
from django.contrib.postgres.forms import SimpleArrayField

from ..utils import parse_numeric_range

__all__ = (
    'NumericArrayField',
)


class NumericArrayField(SimpleArrayField):

    def clean(self, value):
        if value and not self.to_python(value):
            raise forms.ValidationError(f'Invalid list ({value}). '
                                        f'Must be numeric and ranges must be in ascending order')
        return super().clean(value)

    def to_python(self, value):
        if not value:
            return []
        if isinstance(value, str):
            value = ','.join([str(n) for n in parse_numeric_range(value)])
        return super().to_python(value)
