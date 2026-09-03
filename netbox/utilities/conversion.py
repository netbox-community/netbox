from decimal import Decimal, InvalidOperation

from django.utils.translation import gettext as _

from dcim.choices import CableLengthUnitChoices
from netbox.choices import (
    DiameterUnitChoices,
    FlowRateUnitChoices,
    WeightUnitChoices,
)

__all__ = (
    'to_grams',
    'to_liters_per_minute',
    'to_meters',
    'to_millimeters',
)


def _normalized_measurement(value, unit, converters, quantity, precision=4) -> Decimal:
    """
    Shared implementation for the unit-normalization helpers below. Coerce `value` to a non-negative
    Decimal, apply the matching per-unit converter, and round the result to `precision` decimal places.
    `converters` maps each valid unit to a callable receiving the Decimal value; `quantity` labels the
    value in error messages. Pass `precision=None` to return the unrounded result.
    """
    try:
        value = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        raise TypeError(
            _("Invalid value '{value}' for {quantity} (must be a number)").format(value=value, quantity=quantity)
        )
    if value < 0:
        raise ValueError(_("Invalid value for {quantity}: must be a positive number").format(quantity=quantity))
    if unit not in converters:
        raise ValueError(
            _("Unknown unit {unit}. Must be one of the following: {valid_units}").format(
                unit=unit,
                valid_units=', '.join(converters)
            )
        )
    result = converters[unit](value)
    return result if precision is None else round(result, precision)


def to_grams(weight, unit) -> int:
    """
    Convert the given weight to integer grams.
    """
    # Rounding is suppressed so that the result is truncated exactly as the caller's int() expects; rounding
    # first could nudge a value across an integer boundary.
    return int(_normalized_measurement(weight, unit, {
        WeightUnitChoices.UNIT_KILOGRAM: lambda v: v * 1000,
        WeightUnitChoices.UNIT_GRAM: lambda v: v,
        WeightUnitChoices.UNIT_POUND: lambda v: v * Decimal(453.592),
        WeightUnitChoices.UNIT_OUNCE: lambda v: v * Decimal(28.3495),
    }, _('weight'), precision=None))


def to_meters(length, unit) -> Decimal:
    """
    Convert the given length to meters, returning a Decimal value.
    """
    return _normalized_measurement(length, unit, {
        CableLengthUnitChoices.UNIT_KILOMETER: lambda v: v * 1000,
        CableLengthUnitChoices.UNIT_METER: lambda v: v,
        CableLengthUnitChoices.UNIT_CENTIMETER: lambda v: v / 100,
        CableLengthUnitChoices.UNIT_MILE: lambda v: v * Decimal(1609.344),
        CableLengthUnitChoices.UNIT_FOOT: lambda v: v * Decimal(0.3048),
        CableLengthUnitChoices.UNIT_INCH: lambda v: v * Decimal(0.0254),
    }, _('length'))


def to_millimeters(diameter, unit) -> Decimal:
    """
    Convert the given diameter to millimeters, returning a Decimal value.
    """
    return _normalized_measurement(diameter, unit, {
        DiameterUnitChoices.UNIT_MILLIMETER: lambda v: v,
        DiameterUnitChoices.UNIT_CENTIMETER: lambda v: v * 10,
        DiameterUnitChoices.UNIT_INCH: lambda v: v * Decimal('25.4'),
    }, _('diameter'))


def to_liters_per_minute(flow_rate, unit) -> Decimal:
    """
    Convert the given flow rate to liters per minute, returning a Decimal value.
    """
    return _normalized_measurement(flow_rate, unit, {
        FlowRateUnitChoices.UNIT_LITERS_PER_MINUTE: lambda v: v,
        FlowRateUnitChoices.UNIT_CUBIC_METERS_PER_HOUR: lambda v: v * Decimal(1000) / Decimal(60),
        FlowRateUnitChoices.UNIT_GALLONS_PER_MINUTE: lambda v: v * Decimal('3.785411784'),
    }, _('flow rate'))
