from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from netbox.choices import *
from utilities.conversion import (
    to_celsius,
    to_grams,
    to_kilopascals,
    to_liters_per_minute,
    to_meters,
    to_millimeters,
)

__all__ = (
    'CoolingTemperatureMixin',
    'DiameterMixin',
    'DistanceMixin',
    'FlowRateMixin',
    'OwnerMixin',
    'PressureMixin',
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

    @property
    def abs_weight(self):
        # Public alias for _abs_weight; Django templates cannot access underscore-prefixed attributes.
        return self._abs_weight

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


class DiameterMixin(models.Model):
    diameter = models.DecimalField(
        verbose_name=_('diameter'),
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
    )
    diameter_unit = models.CharField(
        verbose_name=_('diameter unit'),
        max_length=50,
        choices=DiameterUnitChoices,
        blank=True,
        null=True,
    )
    # Stores the normalized diameter (in millimeters) for database ordering
    _abs_diameter = models.DecimalField(
        max_digits=13,
        decimal_places=4,
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    @property
    def abs_diameter(self):
        # Public alias for _abs_diameter; Django templates cannot access underscore-prefixed attributes.
        return self._abs_diameter

    def save(self, *args, **kwargs):
        # Store the given diameter (if any) in millimeters for use in database ordering
        if self.diameter is not None and self.diameter_unit:
            self._abs_diameter = to_millimeters(self.diameter, self.diameter_unit)
        else:
            self._abs_diameter = None

        # Clear diameter_unit if no diameter is defined
        if self.diameter is None:
            self.diameter_unit = None

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        # Validate diameter and diameter_unit
        if self.diameter is not None and not self.diameter_unit:
            raise ValidationError(_("Must specify a unit when setting a diameter"))


class FlowRateMixin(models.Model):
    flow_rate = models.DecimalField(
        verbose_name=_('flow rate'),
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    flow_rate_unit = models.CharField(
        verbose_name=_('flow rate unit'),
        max_length=50,
        choices=FlowRateUnitChoices,
        blank=True,
        null=True,
    )
    # Stores the normalized flow rate (in liters per minute) for database ordering
    _abs_flow_rate = models.DecimalField(
        max_digits=13,
        decimal_places=4,
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    @property
    def abs_flow_rate(self):
        # Public alias for _abs_flow_rate; Django templates cannot access underscore-prefixed attributes.
        return self._abs_flow_rate

    def save(self, *args, **kwargs):
        # Store the given flow rate (if any) in liters per minute for use in database ordering
        if self.flow_rate is not None and self.flow_rate_unit:
            self._abs_flow_rate = to_liters_per_minute(self.flow_rate, self.flow_rate_unit)
        else:
            self._abs_flow_rate = None

        # Clear flow_rate_unit if no flow rate is defined
        if self.flow_rate is None:
            self.flow_rate_unit = None

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        # Validate flow_rate and flow_rate_unit
        if self.flow_rate is not None and not self.flow_rate_unit:
            raise ValidationError(_("Must specify a unit when setting a flow rate"))


class PressureMixin(models.Model):
    pressure = models.DecimalField(
        verbose_name=_('pressure'),
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    pressure_unit = models.CharField(
        verbose_name=_('pressure unit'),
        max_length=50,
        choices=PressureUnitChoices,
        blank=True,
        null=True,
    )
    # Stores the normalized pressure (in kilopascals) for database ordering
    _abs_pressure = models.DecimalField(
        max_digits=13,
        decimal_places=4,
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    @property
    def abs_pressure(self):
        # Public alias for _abs_pressure; Django templates cannot access underscore-prefixed attributes.
        return self._abs_pressure

    def save(self, *args, **kwargs):
        # Store the given pressure (if any) in kilopascals for use in database ordering
        if self.pressure is not None and self.pressure_unit:
            self._abs_pressure = to_kilopascals(self.pressure, self.pressure_unit)
        else:
            self._abs_pressure = None

        # Clear pressure_unit if no pressure is defined
        if self.pressure is None:
            self.pressure_unit = None

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        # Validate pressure and pressure_unit
        if self.pressure is not None and not self.pressure_unit:
            raise ValidationError(_("Must specify a unit when setting a pressure"))


class CoolingTemperatureMixin(models.Model):
    """
    Adds supply/return temperatures sharing a single unit, with normalized (°C) fields for ordering.
    """
    supply_temperature = models.DecimalField(
        verbose_name=_('supply temperature'),
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_('Supply (cold) temperature')
    )
    return_temperature = models.DecimalField(
        verbose_name=_('return temperature'),
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_('Return (warm) temperature')
    )
    temperature_unit = models.CharField(
        verbose_name=_('temperature unit'),
        max_length=50,
        choices=TemperatureUnitChoices,
        blank=True,
        null=True,
    )
    # Stores the normalized temperatures (in degrees Celsius) for database ordering
    _abs_supply_temperature = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        blank=True,
        null=True
    )
    _abs_return_temperature = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    @property
    def abs_supply_temperature(self):
        # Public alias for _abs_supply_temperature; Django templates cannot access underscore-prefixed attributes.
        return self._abs_supply_temperature

    @property
    def abs_return_temperature(self):
        # Public alias for _abs_return_temperature; Django templates cannot access underscore-prefixed attributes.
        return self._abs_return_temperature

    def save(self, *args, **kwargs):
        # Store the given temperatures (if any) in degrees Celsius for use in database ordering
        if self.temperature_unit:
            self._abs_supply_temperature = (
                to_celsius(self.supply_temperature, self.temperature_unit)
                if self.supply_temperature is not None else None
            )
            self._abs_return_temperature = (
                to_celsius(self.return_temperature, self.temperature_unit)
                if self.return_temperature is not None else None
            )
        else:
            self._abs_supply_temperature = None
            self._abs_return_temperature = None

        # Clear temperature_unit if no temperatures are defined
        if self.supply_temperature is None and self.return_temperature is None:
            self.temperature_unit = None

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        # A temperature unit is required when a temperature is set
        if (self.supply_temperature is not None or self.return_temperature is not None) and not self.temperature_unit:
            raise ValidationError(_("Must specify a unit when setting a temperature"))


class DistanceMixin(models.Model):
    distance = models.DecimalField(
        verbose_name=_('distance'),
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
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
        max_digits=13,
        decimal_places=4,
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    @property
    def abs_distance(self):
        # Public alias for _abs_distance; Django templates cannot access underscore-prefixed attributes.
        return self._abs_distance

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
