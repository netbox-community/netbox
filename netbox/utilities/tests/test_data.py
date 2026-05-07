from django.db.backends.postgresql.psycopg_any import NumericRange
from django.test import TestCase

from utilities.data import (
    check_ranges_overlap,
    deep_compare_dict,
    get_config_value_ci,
    ranges_to_string,
    ranges_to_string_list,
    string_to_ranges,
)


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

    def test_ranges_to_string_list(self):
        self.assertEqual(
            ranges_to_string_list([
                NumericRange(10, 20),    # 10-19
                NumericRange(30, 40),    # 30-39
                NumericRange(50, 51),    # 50-50
                NumericRange(100, 200),  # 100-199
            ]),
            ['10-19', '30-39', '50', '100-199']
        )

    def test_ranges_to_string(self):
        self.assertEqual(
            ranges_to_string([
                NumericRange(10, 20),    # 10-19
                NumericRange(30, 40),    # 30-39
                NumericRange(50, 51),    # 50-50
                NumericRange(100, 200),  # 100-199
            ]),
            '10-19,30-39,50,100-199'
        )

    def test_string_to_ranges(self):
        self.assertEqual(
            string_to_ranges('10-19, 30-39, 100-199'),
            [
                NumericRange(10, 20, bounds='[)'),    # 10-20
                NumericRange(30, 40, bounds='[)'),    # 30-40
                NumericRange(100, 200, bounds='[)'),  # 100-200
            ]
        )

        self.assertEqual(
            string_to_ranges('1-2, 5, 10-12'),
            [
                NumericRange(1, 3, bounds='[)'),    # 1-3
                NumericRange(5, 6, bounds='[)'),    # 5-6
                NumericRange(10, 13, bounds='[)'),  # 10-13
            ]
        )

        self.assertEqual(
            string_to_ranges('2-10, a-b'),
            None  # Fails to convert
        )


class DeepCompareDictTestCase(TestCase):

    def test_no_changes(self):
        source = {'a': 1, 'b': 'foo', 'c': {'x': 1, 'y': 2}}
        added, removed = deep_compare_dict(source, source)
        self.assertEqual(added, {})
        self.assertEqual(removed, {})

    def test_scalar_change(self):
        source = {'a': 1, 'b': 'foo'}
        dest = {'a': 2, 'b': 'foo'}
        added, removed = deep_compare_dict(source, dest)
        self.assertEqual(added, {'a': 2})
        self.assertEqual(removed, {'a': 1})

    def test_key_added(self):
        source = {'a': 1}
        dest = {'a': 1, 'b': 'new'}
        added, removed = deep_compare_dict(source, dest)
        self.assertEqual(added, {'b': 'new'})
        self.assertEqual(removed, {'b': None})

    def test_key_removed(self):
        source = {'a': 1, 'b': 'old'}
        dest = {'a': 1}
        added, removed = deep_compare_dict(source, dest)
        self.assertEqual(added, {'b': None})
        self.assertEqual(removed, {'b': 'old'})

    def test_nested_dict_partial_change(self):
        """Only changed sub-keys of a nested dict are included."""
        source = {'custom_fields': {'cf1': 'old', 'cf2': 'unchanged'}}
        dest = {'custom_fields': {'cf1': 'new', 'cf2': 'unchanged'}}
        added, removed = deep_compare_dict(source, dest)
        self.assertEqual(added, {'custom_fields': {'cf1': 'new'}})
        self.assertEqual(removed, {'custom_fields': {'cf1': 'old'}})

    def test_nested_dict_no_change(self):
        source = {'name': 'test', 'custom_fields': {'cf1': 'same'}}
        added, removed = deep_compare_dict(source, source)
        self.assertEqual(added, {})
        self.assertEqual(removed, {})

    def test_mixed_flat_and_nested(self):
        source = {'name': 'old', 'custom_fields': {'cf1': 'old', 'cf2': 'same'}}
        dest = {'name': 'new', 'custom_fields': {'cf1': 'new', 'cf2': 'same'}}
        added, removed = deep_compare_dict(source, dest)
        self.assertEqual(added, {'name': 'new', 'custom_fields': {'cf1': 'new'}})
        self.assertEqual(removed, {'name': 'old', 'custom_fields': {'cf1': 'old'}})

    def test_exclude(self):
        source = {'a': 1, 'last_updated': '2024-01-01'}
        dest = {'a': 2, 'last_updated': '2024-06-01'}
        added, removed = deep_compare_dict(source, dest, exclude=['last_updated'])
        self.assertEqual(added, {'a': 2})
        self.assertEqual(removed, {'a': 1})


class GetConfigValueCITestCase(TestCase):

    def test_exact_match(self):
        config = {'dcim.site': 'value1', 'dcim.Device': 'value2'}
        self.assertEqual(get_config_value_ci(config, 'dcim.site'), 'value1')
        self.assertEqual(get_config_value_ci(config, 'dcim.Device'), 'value2')

    def test_case_insensitive_match(self):
        config = {'dcim.Site': 'value1', 'ipam.IPAddress': 'value2'}
        self.assertEqual(get_config_value_ci(config, 'dcim.site'), 'value1')
        self.assertEqual(get_config_value_ci(config, 'ipam.ipaddress'), 'value2')

    def test_default_value(self):
        config = {'dcim.site': 'value1'}
        self.assertIsNone(get_config_value_ci(config, 'nonexistent'))
        self.assertEqual(get_config_value_ci(config, 'nonexistent', default=[]), [])

    def test_empty_dict(self):
        self.assertIsNone(get_config_value_ci({}, 'any.key'))
        self.assertEqual(get_config_value_ci({}, 'any.key', default=[]), [])
