from django.db import models
from timezone_field import TimeZoneField


SKIP_FIELDS = (
    TimeZoneField,
)

EXEMPT_ATTRS = (
    'choices',
    'help_text',
    'verbose_name',
)

_deconstruct = models.Field.deconstruct


def custom_deconstruct(field):
    """
    Imitate the behavior of the stock deconstruct() method, but ignore the field attributes listed above.
    """
    name, path, args, kwargs = _deconstruct(field)

    # Remove any ignored attributes
    if field.__class__ not in SKIP_FIELDS:
        for attr in EXEMPT_ATTRS:
            kwargs.pop(attr, None)

    return name, path, args, kwargs
