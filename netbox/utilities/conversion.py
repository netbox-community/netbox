from decimal import Decimal, InvalidOperation

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


def to_meters(length, unit) -> Decimal:
    """
    Convert the given length to meters, returning a Decimal value.
    """
    try:
        length = Decimal(length)
    except InvalidOperation:
        raise TypeError(_("Invalid value '{length}' for length (must be a number)").format(length=length))
    if length < 0:
        raise ValueError(_("Length must be a positive number"))

    if unit == CableLengthUnitChoices.UNIT_KILOMETER:
        return round(Decimal(length * 1000), 4)
    if unit == CableLengthUnitChoices.UNIT_METER:
        return round(Decimal(length), 4)
    if unit == CableLengthUnitChoices.UNIT_CENTIMETER:
        return round(Decimal(length / 100), 4)
    if unit == CableLengthUnitChoices.UNIT_MILE:
        return round(length * Decimal(1609.344), 4)
    if unit == CableLengthUnitChoices.UNIT_FOOT:
        return round(length * Decimal(0.3048), 4)
    if unit == CableLengthUnitChoices.UNIT_INCH:
        return round(length * Decimal(0.0254), 4)
    raise ValueError(
        _("Unknown unit {unit}. Must be one of the following: {valid_units}").format(
            unit=unit,
            valid_units=', '.join(CableLengthUnitChoices.values())
        )
    )
