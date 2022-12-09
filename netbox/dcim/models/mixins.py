from django.core.exceptions import ValidationError
from django.db import models
from dcim.choices import *
from utilities.utils import to_grams


class WeightMixin(models.Model):
    weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )
    weight_unit = models.CharField(
        max_length=50,
        choices=WeightUnitChoices,
        blank=True,
    )
    # Stores the normalized weight (in grams) for database ordering
    _abs_weight = models.PositiveBigIntegerField(
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):

        # Store the given weight (if any) in grams for use in database ordering
        if self.weight and self.weight_unit:
            self._abs_weight = to_grams(self.weight, self.weight_unit)
        else:
            self._abs_weight = None

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        # Validate weight and weight_unit
        if self.weight and not self.weight_unit:
            raise ValidationError("Must specify a unit when setting a weight")
