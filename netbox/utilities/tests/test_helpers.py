from django.test import TestCase, override_settings
from utilities.templatetags.helpers import humanize_disk_megabytes, humanize_ram_megabytes

class HumanizeHelpersTest(TestCase):

    def test_humanize_ram_megabytes_decimal(self):
        self.assertEqual(humanize_ram_megabytes(1000), '1.00 GB')
        self.assertEqual(humanize_ram_megabytes(2000), '2.00 GB')
        self.assertEqual(humanize_ram_megabytes(1000 * 1000), '1.00 TB')
        self.assertEqual(humanize_ram_megabytes(1000 * 1000 * 1000), '1.00 PB')
        self.assertEqual(humanize_ram_megabytes(999), '999 MB')

    @override_settings(RAM_BASE_UNIT=1024)
    def test_humanize_ram_megabytes_binary(self):
        self.assertEqual(humanize_ram_megabytes(1024), '1.00 GiB')
        self.assertEqual(humanize_ram_megabytes(2048), '2.00 GiB')
        self.assertEqual(humanize_ram_megabytes(1024 * 1024), '1.00 TiB')
        self.assertEqual(humanize_ram_megabytes(1024 * 1024 * 1024), '1.00 PiB')
        self.assertEqual(humanize_ram_megabytes(1023), '1023 MiB')

    def test_humanize_disk_megabytes_decimal(self):
        self.assertEqual(humanize_disk_megabytes(1000), '1.00 GB')
        self.assertEqual(humanize_disk_megabytes(2000), '2.00 GB')
        self.assertEqual(humanize_disk_megabytes(1000 * 1000), '1.00 TB')
        self.assertEqual(humanize_disk_megabytes(1000 * 1000 * 1000), '1.00 PB')
        self.assertEqual(humanize_disk_megabytes(999), '999 MB')

    @override_settings(DISK_BASE_UNIT=1024)
    def test_humanize_disk_megabytes_binary(self):
        self.assertEqual(humanize_disk_megabytes(1024), '1.00 GiB')
        self.assertEqual(humanize_disk_megabytes(2048), '2.00 GiB')
        self.assertEqual(humanize_disk_megabytes(1024 * 1024), '1.00 TiB')
        self.assertEqual(humanize_disk_megabytes(1024 * 1024 * 1024), '1.00 PiB')
        self.assertEqual(humanize_disk_megabytes(1023), '1023 MiB')
