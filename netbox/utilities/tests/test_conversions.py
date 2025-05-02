from decimal import Decimal

from dcim.choices import CableLengthUnitChoices
from netbox.choices import WeightUnitChoices
from utilities.conversion import to_grams, to_meters
from utilities.testing.base import TestCase


class ConversionsTest(TestCase):

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
