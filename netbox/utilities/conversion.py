from decimal import Decimal, InvalidOperation

from django.utils.translation import gettext as _

from dcim.choices import CableLengthUnitChoices
from netbox.choices import (
    DiameterUnitChoices,
    FlowRateUnitChoices,
    PressureUnitChoices,
    TemperatureUnitChoices,
    WeightUnitChoices,
)

__all__ = (
    'to_celsius',
    'to_grams',
    'to_kilopascals',
    'to_liters_per_minute',
    'to_meters',
    'to_millimeters',
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


def to_liters_per_minute(flow_rate, unit) -> Decimal:
    """
    Convert the given flow rate to liters per minute, returning a Decimal value.
    """
    try:
        flow_rate = Decimal(flow_rate)
    except InvalidOperation:
        raise TypeError(_("Invalid value '{flow_rate}' for flow rate (must be a number)").format(flow_rate=flow_rate))
    if flow_rate < 0:
        raise ValueError(_("Flow rate must be a positive number"))

    if unit == FlowRateUnitChoices.UNIT_LITERS_PER_MINUTE:
        return round(Decimal(flow_rate), 4)
    if unit == FlowRateUnitChoices.UNIT_CUBIC_METERS_PER_HOUR:
        return round(flow_rate * Decimal(1000) / Decimal(60), 4)
    if unit == FlowRateUnitChoices.UNIT_GALLONS_PER_MINUTE:
        return round(flow_rate * Decimal('3.785411784'), 4)
    raise ValueError(
        _("Unknown unit {unit}. Must be one of the following: {valid_units}").format(
            unit=unit,
            valid_units=', '.join(FlowRateUnitChoices.values())
        )
    )


def to_kilopascals(pressure, unit) -> Decimal:
    """
    Convert the given pressure to kilopascals, returning a Decimal value.
    """
    try:
        pressure = Decimal(pressure)
    except InvalidOperation:
        raise TypeError(_("Invalid value '{pressure}' for pressure (must be a number)").format(pressure=pressure))
    if pressure < 0:
        raise ValueError(_("Pressure must be a positive number"))

    if unit == PressureUnitChoices.UNIT_KILOPASCAL:
        return round(Decimal(pressure), 4)
    if unit == PressureUnitChoices.UNIT_BAR:
        return round(pressure * Decimal(100), 4)
    if unit == PressureUnitChoices.UNIT_PSI:
        return round(pressure * Decimal('6.894757'), 4)
    raise ValueError(
        _("Unknown unit {unit}. Must be one of the following: {valid_units}").format(
            unit=unit,
            valid_units=', '.join(PressureUnitChoices.values())
        )
    )


def to_celsius(temperature, unit) -> Decimal:
    """
    Convert the given temperature to degrees Celsius, returning a Decimal value. Temperatures may be negative.
    """
    try:
        temperature = Decimal(temperature)
    except InvalidOperation:
        raise TypeError(
            _("Invalid value '{temperature}' for temperature (must be a number)").format(temperature=temperature)
        )

    if unit == TemperatureUnitChoices.UNIT_CELSIUS:
        return round(Decimal(temperature), 4)
    if unit == TemperatureUnitChoices.UNIT_FAHRENHEIT:
        return round((Decimal(temperature) - 32) * 5 / 9, 4)
    raise ValueError(
        _("Unknown unit {unit}. Must be one of the following: {valid_units}").format(
            unit=unit,
            valid_units=', '.join(TemperatureUnitChoices.values())
        )
    )


def to_millimeters(diameter, unit) -> Decimal:
    """
    Convert the given diameter to millimeters, returning a Decimal value.
    """
    try:
        diameter = Decimal(diameter)
    except InvalidOperation:
        raise TypeError(_("Invalid value '{diameter}' for diameter (must be a number)").format(diameter=diameter))
    if diameter < 0:
        raise ValueError(_("Diameter must be a positive number"))

    if unit == DiameterUnitChoices.UNIT_MILLIMETER:
        return round(Decimal(diameter), 4)
    if unit == DiameterUnitChoices.UNIT_CENTIMETER:
        return round(Decimal(diameter * 10), 4)
    if unit == DiameterUnitChoices.UNIT_INCH:
        return round(diameter * Decimal('25.4'), 4)
    raise ValueError(
        _("Unknown unit {unit}. Must be one of the following: {valid_units}").format(
            unit=unit,
            valid_units=', '.join(DiameterUnitChoices.values())
        )
    )
