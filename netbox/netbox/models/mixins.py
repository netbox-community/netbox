from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from netbox.choices import *
from utilities.conversion import LENGTH_TO_METERS, WEIGHT_TO_GRAMS, normalized_unit_expression
from utilities.fields import NonNegativeGeneratedField

__all__ = (
    'DistanceMixin',
    'OwnerMixin',
    'WeightMixin',
)


class OwnerMixin(models.Model):
    """
    Adds a ForeignKey to users.Owner to indicate an object's owner.
    """
    owner = models.ForeignKey(
        to='users.Owner',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True
    )

    class Meta:
        abstract = True


class WeightMixin(models.Model):
    weight = models.DecimalField(
        verbose_name=_('weight'),
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    weight_unit = models.CharField(
        verbose_name=_('weight unit'),
        max_length=50,
        choices=WeightUnitChoices,
        blank=True,
        null=True,
    )
    # Normalized weight (in grams), computed by the database for ordering
    _abs_weight = NonNegativeGeneratedField(
        expression=normalized_unit_expression('weight', 'weight_unit', WEIGHT_TO_GRAMS, integer=True),
        output_field=models.BigIntegerField(blank=True, null=True),
        db_persist=True,
        null=True,
    )

    class Meta:
        abstract = True

    @property
    def abs_weight(self):
        # Public alias for _abs_weight; Django templates cannot access underscore-prefixed attributes.
        return self._abs_weight

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
        null=True,
        validators=[MinValueValidator(0)],
    )
    distance_unit = models.CharField(
        verbose_name=_('distance unit'),
        max_length=50,
        choices=DistanceUnitChoices,
        blank=True,
        null=True,
    )
    # Normalized distance (in meters), computed by the database for ordering
    _abs_distance = NonNegativeGeneratedField(
        expression=normalized_unit_expression('distance', 'distance_unit', LENGTH_TO_METERS),
        output_field=models.DecimalField(max_digits=14, decimal_places=4, blank=True, null=True),
        db_persist=True,
        null=True,
    )

    class Meta:
        abstract = True

    @property
    def abs_distance(self):
        # Public alias for _abs_distance; Django templates cannot access underscore-prefixed attributes.
        return self._abs_distance

    def save(self, *args, **kwargs):
        # Clear distance_unit if no distance is defined
        if self.distance is None:
            self.distance_unit = None

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        # Validate distance and distance_unit
        if self.distance and not self.distance_unit:
            raise ValidationError(_("Must specify a unit when setting a distance"))
