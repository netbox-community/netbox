from netbox.utils import convert_byte_size
from utilities.testing import TestCase


class TestConvertByteSize(TestCase):
    def test_convert_byte_size_returns_original_value_for_small_numbers(self):
        self.assertEqual(convert_byte_size(500, "kilo"), 500)

    def test_convert_byte_size_converts_kilobytes_to_bytes(self):
        self.assertEqual(convert_byte_size(1024, "kilo"), 1024)

    def test_convert_byte_size_converts_megabytes_to_bytes(self):
        self.assertEqual(convert_byte_size(1048576, "mega"), 1)

    def test_convert_byte_size_converts_gigabytes_to_bytes(self):
        self.assertEqual(convert_byte_size(1073741824, "giga"), 1)

    def test_convert_byte_size_converts_terabytes_to_bytes(self):
        self.assertEqual(convert_byte_size(1099511627776, "tera"), 1)

    def test_convert_byte_size_returns_zero_for_none(self):
        self.assertEqual(convert_byte_size(None, "mega"), 0)

    def test_convert_byte_size_without_unit(self):
        self.assertEqual(round(convert_byte_size(123456789), 2), 117.74)
