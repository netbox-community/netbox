from decimal import Decimal

from dcim.choices import CableLengthUnitChoices
from netbox.choices import (
    DiameterUnitChoices,
    FlowRateUnitChoices,
    WeightUnitChoices,
)
from utilities.conversion import (
    to_grams,
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
