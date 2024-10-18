from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from netbox.choices import *
from utilities.conversion import to_grams, to_meters

__all__ = (
    'DistanceMixin',
    'WeightMixin',
)


class WeightMixin(models.Model):
    weight = models.DecimalField(
        verbose_name=_('weight'),
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )
    weight_unit = models.CharField(
        verbose_name=_('weight unit'),
        max_length=50,
        choices=WeightUnitChoices,
        blank=True,
        null=True,
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
            raise ValidationError(_("Must specify a unit when setting a weight"))


class DistanceMixin(models.Model):
    distance = models.DecimalField(
        verbose_name=_('distance'),
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )
    distance_unit = models.CharField(
        verbose_name=_('distance unit'),
        max_length=50,
        choices=DistanceUnitChoices,
        blank=True,
        null=True,
    )
    # Stores the normalized distance (in meters) for database ordering
    _abs_distance = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Store the given distance (if any) in meters for use in database ordering
        if self.distance is not None and self.distance_unit:
            self._abs_distance = to_meters(self.distance, self.distance_unit)
        else:
            self._abs_distance = None

        # Clear distance_unit if no distance is defined
        if self.distance is None:
            self.distance_unit = None

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        # Validate distance and distance_unit
        if self.distance and not self.distance_unit:
            raise ValidationError(_("Must specify a unit when setting a distance"))
