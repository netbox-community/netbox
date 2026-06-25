from decimal import Decimal

from dcim.choices import CableLengthUnitChoices
from netbox.choices import (
    DiameterUnitChoices,
    FlowRateUnitChoices,
    PressureUnitChoices,
    TemperatureUnitChoices,
    WeightUnitChoices,
)
from utilities.conversion import (
    to_celsius,
    to_grams,
    to_kilopascals,
    to_liters_per_minute,
    to_meters,
    to_millimeters,
)
from utilities.testing.base import TestCase


class ConversionsTestCase(TestCase):

    def test_to_grams(self):
        self.assertEqual(
            to_grams(1, WeightUnitChoices.UNIT_KILOGRAM),
            1000
        )
        self.assertEqual(
            to_grams(1, WeightUnitChoices.UNIT_GRAM),
            1
        )
        self.assertEqual(
            to_grams(1, WeightUnitChoices.UNIT_POUND),
            453
        )
        self.assertEqual(
            to_grams(1, WeightUnitChoices.UNIT_OUNCE),
            28
        )

    def test_to_meters(self):
        self.assertEqual(
            to_meters(1.5, CableLengthUnitChoices.UNIT_KILOMETER),
            Decimal('1500')
        )
        self.assertEqual(
            to_meters(1, CableLengthUnitChoices.UNIT_METER),
            Decimal('1')
        )
        self.assertEqual(
            to_meters(1, CableLengthUnitChoices.UNIT_CENTIMETER),
            Decimal('0.01')
        )
        self.assertEqual(
            to_meters(1, CableLengthUnitChoices.UNIT_MILE),
            Decimal('1609.344')
        )
        self.assertEqual(
            to_meters(1, CableLengthUnitChoices.UNIT_FOOT),
            Decimal('0.3048')
        )
        self.assertEqual(
            to_meters(1, CableLengthUnitChoices.UNIT_INCH),
            Decimal('0.0254')
        )

    def test_to_celsius(self):
        self.assertEqual(
            to_celsius(20, TemperatureUnitChoices.UNIT_CELSIUS),
            Decimal('20')
        )
        self.assertEqual(
            to_celsius(68, TemperatureUnitChoices.UNIT_FAHRENHEIT),
            Decimal('20')
        )
        self.assertEqual(
            to_celsius(-4, TemperatureUnitChoices.UNIT_FAHRENHEIT),
            Decimal('-20')
        )
        with self.assertRaises(ValueError):
            to_celsius(20, 'invalid')

    def test_to_millimeters(self):
        self.assertEqual(
            to_millimeters(1, DiameterUnitChoices.UNIT_MILLIMETER),
            Decimal('1')
        )
        self.assertEqual(
            to_millimeters(1, DiameterUnitChoices.UNIT_CENTIMETER),
            Decimal('10')
        )
        self.assertEqual(
            to_millimeters(1, DiameterUnitChoices.UNIT_INCH),
            Decimal('25.4')
        )
        with self.assertRaises(ValueError):
            to_millimeters(1, 'invalid')

    def test_to_liters_per_minute(self):
        self.assertEqual(
            to_liters_per_minute(10, FlowRateUnitChoices.UNIT_LITERS_PER_MINUTE),
            Decimal('10')
        )
        self.assertAlmostEqual(
            to_liters_per_minute(6, FlowRateUnitChoices.UNIT_CUBIC_METERS_PER_HOUR),
            Decimal('100'),
            places=4
        )
        self.assertAlmostEqual(
            to_liters_per_minute(10, FlowRateUnitChoices.UNIT_GALLONS_PER_MINUTE),
            Decimal('37.8541'),
            places=4
        )
        with self.assertRaises(ValueError):
            to_liters_per_minute(10, 'invalid')

    def test_to_kilopascals(self):
        self.assertEqual(
            to_kilopascals(1, PressureUnitChoices.UNIT_KILOPASCAL),
            Decimal('1')
        )
        self.assertEqual(
            to_kilopascals(1, PressureUnitChoices.UNIT_BAR),
            Decimal('100')
        )
        self.assertAlmostEqual(
            to_kilopascals(30, PressureUnitChoices.UNIT_PSI),
            Decimal('206.8427'),
            places=4
        )
        with self.assertRaises(ValueError):
            to_kilopascals(30, 'invalid')
