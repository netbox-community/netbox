from decimal import Decimal

from django.utils.translation import gettext as _

from dcim.choices import CableLengthUnitChoices
from netbox.choices import WeightUnitChoices

__all__ = (
    'to_grams',
    'to_meters',
)


def to_grams(weight, unit) -> int:
    """
    Convert the given weight to integer grams.
    """
    try:
        if weight < 0:
            raise ValueError(_("Weight must be a positive number"))
    except TypeError:
        raise TypeError(_("Invalid value '{weight}' for weight (must be a number)").format(weight=weight))

    if unit == WeightUnitChoices.UNIT_KILOGRAM:
        return int(weight * 1000)
    if unit == WeightUnitChoices.UNIT_GRAM:
        return int(weight)
    if unit == WeightUnitChoices.UNIT_POUND:
        return int(weight * Decimal(453.592))
    if unit == WeightUnitChoices.UNIT_OUNCE:
        return int(weight * Decimal(28.3495))
    raise ValueError(
        _("Unknown unit {unit}. Must be one of the following: {valid_units}").format(
            unit=unit,
            valid_units=', '.join(WeightUnitChoices.values())
        )
    )


def to_meters(length, unit):
    """
    Convert the given length to meters.
    """
    try:
        if length < 0:
            raise ValueError(_("Length must be a positive number"))
    except TypeError:
        raise TypeError(_("Invalid value '{length}' for length (must be a number)").format(length=length))

    if unit == CableLengthUnitChoices.UNIT_KILOMETER:
        return length * 1000
    if unit == CableLengthUnitChoices.UNIT_METER:
        return length
    if unit == CableLengthUnitChoices.UNIT_CENTIMETER:
        return length / 100
    if unit == CableLengthUnitChoices.UNIT_MILE:
        return length * Decimal(1609.344)
    if unit == CableLengthUnitChoices.UNIT_FOOT:
        return length * Decimal(0.3048)
    if unit == CableLengthUnitChoices.UNIT_INCH:
        return length * Decimal(0.0254)
    raise ValueError(
        _("Unknown unit {unit}. Must be one of the following: {valid_units}").format(
            unit=unit,
            valid_units=', '.join(CableLengthUnitChoices.values())
        )
    )
