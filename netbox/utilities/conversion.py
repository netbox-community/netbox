from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from django.db.models import BigIntegerField, Case, DecimalField, F, Value, When
from django.db.models.functions import Cast, Floor
from django.utils.translation import gettext as _

from dcim.choices import CableLengthUnitChoices
from netbox.choices import (
    DiameterUnitChoices,
    FlowRateUnitChoices,
    WeightUnitChoices,
)

__all__ = (
    'DIAMETER_TO_MILLIMETERS',
    'FLOW_RATE_TO_LITERS_PER_MINUTE',
    'LENGTH_TO_METERS',
    'WEIGHT_TO_GRAMS',
    'normalized_unit_expression',
    'to_grams',
    'to_liters_per_minute',
    'to_meters',
    'to_millimeters',
)


#
# Conversion factors
#

# Each mapping gives the multiplier from a unit to its base unit as a Decimal literal. The to_*() helpers and the
# GeneratedField expressions built by normalized_unit_expression() both read these, so changing a factor (or adding
# a unit) requires a migration to drop and re-add the affected generated columns.
WEIGHT_TO_GRAMS = {
    WeightUnitChoices.UNIT_KILOGRAM: Decimal('1000'),
    WeightUnitChoices.UNIT_GRAM: Decimal('1'),
    WeightUnitChoices.UNIT_POUND: Decimal('453.592'),
    WeightUnitChoices.UNIT_OUNCE: Decimal('28.3495'),
}

# Shared by cable lengths and distances; DistanceUnitChoices is a subset of CableLengthUnitChoices
LENGTH_TO_METERS = {
    CableLengthUnitChoices.UNIT_KILOMETER: Decimal('1000'),
    CableLengthUnitChoices.UNIT_METER: Decimal('1'),
    CableLengthUnitChoices.UNIT_CENTIMETER: Decimal('0.01'),
    CableLengthUnitChoices.UNIT_MILE: Decimal('1609.344'),
    CableLengthUnitChoices.UNIT_FOOT: Decimal('0.3048'),
    CableLengthUnitChoices.UNIT_INCH: Decimal('0.0254'),
}

DIAMETER_TO_MILLIMETERS = {
    DiameterUnitChoices.UNIT_MILLIMETER: Decimal('1'),
    DiameterUnitChoices.UNIT_CENTIMETER: Decimal('10'),
    DiameterUnitChoices.UNIT_INCH: Decimal('25.4'),
}

FLOW_RATE_TO_LITERS_PER_MINUTE = {
    FlowRateUnitChoices.UNIT_LITERS_PER_MINUTE: Decimal('1'),
    FlowRateUnitChoices.UNIT_CUBIC_METERS_PER_HOUR: Decimal('16.66666666666666666666666667'),  # 1000 / 60
    FlowRateUnitChoices.UNIT_GALLONS_PER_MINUTE: Decimal('3.785411784'),
}


#
# Database expressions
#

def normalized_unit_expression(value_field, unit_field, factors, integer=False):
    """
    Return a database expression converting `value_field` to its base unit according to the value of `unit_field`,
    per the given mapping of unit to factor. Evaluates to NULL if either field is NULL or the unit is unrecognized.
    With `integer=True`, the result is truncated to a whole number (as to_grams() does) and cast to a bigint.
    """
    # Cast to numeric so that an integer source column cannot overflow integer arithmetic
    value = Cast(F(value_field), output_field=DecimalField())
    expression = Case(*[
        When(**{unit_field: unit}, then=value * Value(factor))
        for unit, factor in factors.items()
    ])
    if integer:
        expression = Cast(Floor(expression), output_field=BigIntegerField())
    return expression


#
# Python conversions
#

def _normalized_measurement(value, unit, factors, quantity, precision=4) -> Decimal:
    """
    Shared implementation for the unit-normalization helpers below. Coerce `value` to a non-negative
    Decimal, multiply by the factor for `unit`, and round the result to `precision` decimal places.
    `factors` maps each valid unit to its multiplier; `quantity` labels the value in error messages.
    Pass `precision=None` to return the unrounded result. Rounding is half away from zero, matching how
    PostgreSQL stores the same result in a generated numeric column.
    """
    try:
        value = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        raise TypeError(
            _("Invalid value '{value}' for {quantity} (must be a number)").format(value=value, quantity=quantity)
        )
    if value < 0:
        raise ValueError(_("Invalid value for {quantity}: must be a positive number").format(quantity=quantity))
    if unit not in factors:
        raise ValueError(
            _("Unknown unit {unit}. Must be one of the following: {valid_units}").format(
                unit=unit,
                valid_units=', '.join(factors)
            )
        )
    result = value * factors[unit]
    if precision is None:
        return result
    return result.quantize(Decimal(1).scaleb(-precision), rounding=ROUND_HALF_UP)


def to_grams(weight, unit) -> int:
    """
    Convert the given weight to integer grams.
    """
    # Rounding is suppressed so that the result is truncated exactly as the caller's int() expects; rounding
    # first could nudge a value across an integer boundary.
    return int(_normalized_measurement(weight, unit, WEIGHT_TO_GRAMS, _('weight'), precision=None))


def to_meters(length, unit) -> Decimal:
    """
    Convert the given length to meters, returning a Decimal value.
    """
    return _normalized_measurement(length, unit, LENGTH_TO_METERS, _('length'))


def to_millimeters(diameter, unit) -> Decimal:
    """
    Convert the given diameter to millimeters, returning a Decimal value.
    """
    return _normalized_measurement(diameter, unit, DIAMETER_TO_MILLIMETERS, _('diameter'))


def to_liters_per_minute(flow_rate, unit) -> Decimal:
    """
    Convert the given flow rate to liters per minute, returning a Decimal value.
    """
    return _normalized_measurement(flow_rate, unit, FLOW_RATE_TO_LITERS_PER_MINUTE, _('flow rate'))
