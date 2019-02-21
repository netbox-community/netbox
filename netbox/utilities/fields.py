from django.core.validators import RegexValidator
from django.db import models

from .forms import ColorSelect

ColorValidator = RegexValidator(
    regex='^[0-9a-f]{6}$',
    message='Enter a valid hexadecimal RGB color code.',
    code='invalid'
)


# Deprecated: Retained only to ensure successful migration from early releases
# Use models.CharField(null=True) instead
class NullableCharField(models.CharField):
    description = "Stores empty values as NULL rather than ''"

    def to_python(self, value):
        if isinstance(value, models.CharField):
            return value
        return value or ''

    def get_prep_value(self, value):
        return value or None


class ColorField(models.CharField):
    default_validators = [ColorValidator]
    description = "A hexadecimal RGB color code"

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 6
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = ColorSelect
        return super().formfield(**kwargs)
