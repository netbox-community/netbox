from django.core.validators import RegexValidator
from django.db import models

from utilities.ordering import naturalize
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


class NaturalOrderingField(models.CharField):
    """
    A field which stores a naturalized representation of its target field, to be used for ordering its parent model.

    :param target_field: Name of the field of the parent model to be naturalized
    :param naturalize_function: The function used to generate a naturalized value (optional)
    """
    description = "Stores a representation of its target field suitable for natural ordering"

    def __init__(self, target_field, naturalize_function=naturalize, *args, **kwargs):
        self.target_field = target_field
        self.naturalize_function = naturalize_function
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        """
        Generate a naturalized value from the target field
        """
        value = getattr(model_instance, self.target_field)
        return self.naturalize_function(value, max_length=self.max_length)

    def deconstruct(self):
        kwargs = super().deconstruct()[3]  # Pass kwargs from CharField
        kwargs['naturalize_function'] = self.naturalize_function
        return (
            self.name,
            'utilities.fields.NaturalOrderingField',
            ['target_field'],
            kwargs,
        )
