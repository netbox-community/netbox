from utilities.templatetags.helpers import humanize_megabytes
from utilities.testing import TestCase


class TestConvertByteSize(TestCase):

    def test_humanize_megabytes_converts_megabytes(self):
        """Test that humanize_megabytes converts megabytes to the most suitable unit."""
        self.assertEqual(humanize_megabytes(1), "1.00 MB")

    def test_humanize_megabytes_converts_to_gigabytes(self):
        """Test that humanize_megabytes converts megabytes to gigabytes."""
        self.assertEqual(humanize_megabytes(1000), "1.00 GB")

    def test_humanize_megabytes_converts_to_terabytes(self):
        """Test that humanize_megabytes converts megabytes to terabytes."""
        self.assertEqual(humanize_megabytes(1000000), "1.00 TB")

    def test_humanize_megabytes_returns_empty_for_none(self):
        """Test that humanize_megabytes returns empty for None."""
        self.assertEqual(humanize_megabytes(None), '')

    def test_humanize_megabytes_without_unit(self):
        """Test that humanize_megabytes returns the value without unit."""
        self.assertEqual(humanize_megabytes(123456789), "123.46 TB")
