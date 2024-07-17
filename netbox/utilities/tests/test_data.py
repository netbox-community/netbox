from django.db.backends.postgresql.psycopg_any import NumericRange
from django.test import TestCase

from utilities.data import check_ranges_overlap, ranges_to_string, string_to_ranges


class RangeFunctionsTestCase(TestCase):

    def test_check_ranges_overlap(self):
        # Non-overlapping ranges
        self.assertFalse(
            check_ranges_overlap([
                NumericRange(9, 19, bounds='(]'),   # 10-19
                NumericRange(19, 30, bounds='(]'),  # 20-29
            ])
        )
        self.assertFalse(
            check_ranges_overlap([
                NumericRange(10, 19, bounds='[]'),  # 10-19
                NumericRange(20, 29, bounds='[]'),  # 20-29
            ])
        )
        self.assertFalse(
            check_ranges_overlap([
                NumericRange(10, 20, bounds='[)'),  # 10-19
                NumericRange(20, 30, bounds='[)'),  # 20-29
            ])
        )

        # Overlapping ranges
        self.assertTrue(
            check_ranges_overlap([
                NumericRange(9, 20, bounds='(]'),   # 10-20
                NumericRange(19, 30, bounds='(]'),  # 20-30
            ])
        )
        self.assertTrue(
            check_ranges_overlap([
                NumericRange(10, 20, bounds='[]'),  # 10-20
                NumericRange(20, 30, bounds='[]'),  # 20-30
            ])
        )
        self.assertTrue(
            check_ranges_overlap([
                NumericRange(10, 21, bounds='[)'),  # 10-20
                NumericRange(20, 31, bounds='[)'),  # 10-30
            ])
        )

    def test_ranges_to_string(self):
        self.assertEqual(
            ranges_to_string([
                NumericRange(10, 20),    # 10-19
                NumericRange(30, 40),    # 30-39
                NumericRange(100, 200),  # 100-199
            ]),
            '10-19,30-39,100-199'
        )

    def test_string_to_ranges(self):
        self.assertEqual(
            string_to_ranges('10-19, 30-39, 100-199'),
            [
                NumericRange(10, 19, bounds='[]'),    # 10-19
                NumericRange(30, 39, bounds='[]'),    # 30-39
                NumericRange(100, 199, bounds='[]'),  # 100-199
            ]
        )
