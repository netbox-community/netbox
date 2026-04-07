from unittest.mock import patch

from django.template.loader import render_to_string
from django.test import TestCase, override_settings

from utilities.templatetags.builtins.tags import badge, static_with_params
from utilities.templatetags.helpers import _humanize_capacity, humanize_speed


class StaticWithParamsTest(TestCase):
    """
    Test the static_with_params template tag functionality.
    """

    def test_static_with_params_basic(self):
        """Test basic parameter appending to static URL."""
        result = static_with_params('test.js', v='1.0.0')
        self.assertIn('test.js', result)
        self.assertIn('v=1.0.0', result)

    @override_settings(STATIC_URL='https://cdn.example.com/static/')
    def test_static_with_params_existing_query_params(self):
        """Test appending parameters to URL that already has query parameters."""
        # Mock the static() function to return a URL with existing query parameters
        with patch('utilities.templatetags.builtins.tags.static') as mock_static:
            mock_static.return_value = 'https://cdn.example.com/static/test.js?existing=param'

            result = static_with_params('test.js', v='1.0.0')

            # Should contain both existing and new parameters
            self.assertIn('existing=param', result)
            self.assertIn('v=1.0.0', result)
            # Should not have double question marks
            self.assertEqual(result.count('?'), 1)

    @override_settings(STATIC_URL='https://cdn.example.com/static/')
    def test_static_with_params_duplicate_parameter_warning(self):
        """Test that a warning is logged when parameters conflict."""
        with patch('utilities.templatetags.builtins.tags.static') as mock_static:
            mock_static.return_value = 'https://cdn.example.com/static/test.js?v=old_version'

            with self.assertLogs('netbox.utilities.templatetags.tags', level='WARNING') as cm:
                result = static_with_params('test.js', v='new_version')

                # Check that warning was logged
                self.assertIn("Parameter 'v' already exists", cm.output[0])

                # Check that new parameter value is used
                self.assertIn('v=new_version', result)
                self.assertNotIn('v=old_version', result)


class BadgeTest(TestCase):
    """
    Test the badge template tag functionality.
    """

    def test_badge_with_hex_color_and_url(self):
        html = render_to_string('builtins/badge.html', badge('Role', hex_color='ff0000', url='/dcim/device-roles/1/'))

        self.assertIn('href="/dcim/device-roles/1/"', html)
        self.assertIn('background-color: #ff0000', html)
        self.assertIn('color: #ffffff', html)
        self.assertIn('>Role<', html)


class HumanizeCapacityTest(TestCase):
    """
    Test the _humanize_capacity function for correct SI/IEC unit label selection.
    """

    # Tests with divisor=1000 (SI/decimal units)

    def test_si_megabytes(self):
        self.assertEqual(_humanize_capacity(500, divisor=1000), '500 MB')

    def test_si_gigabytes(self):
        self.assertEqual(_humanize_capacity(2000, divisor=1000), '2.00 GB')

    def test_si_terabytes(self):
        self.assertEqual(_humanize_capacity(2000000, divisor=1000), '2.00 TB')

    def test_si_petabytes(self):
        self.assertEqual(_humanize_capacity(2000000000, divisor=1000), '2.00 PB')

    # Tests with divisor=1024 (IEC/binary units)

    def test_iec_megabytes(self):
        self.assertEqual(_humanize_capacity(500, divisor=1024), '500 MiB')

    def test_iec_gigabytes(self):
        self.assertEqual(_humanize_capacity(2048, divisor=1024), '2.00 GiB')

    def test_iec_terabytes(self):
        self.assertEqual(_humanize_capacity(2097152, divisor=1024), '2.00 TiB')

    def test_iec_petabytes(self):
        self.assertEqual(_humanize_capacity(2147483648, divisor=1024), '2.00 PiB')

    # Edge cases

    def test_empty_value(self):
        self.assertEqual(_humanize_capacity(0, divisor=1000), '')
        self.assertEqual(_humanize_capacity(None, divisor=1000), '')

    def test_default_divisor_is_1000(self):
        self.assertEqual(_humanize_capacity(2000), '2.00 GB')


class HumanizeSpeedTest(TestCase):
    """
    Test the humanize_speed filter for correct unit selection and decimal formatting.
    """

    # Falsy / empty inputs

    def test_none(self):
        self.assertEqual(humanize_speed(None), '')

    def test_zero(self):
        self.assertEqual(humanize_speed(0), '')

    def test_empty_string(self):
        self.assertEqual(humanize_speed(''), '')

    # Kbps (below 1000)

    def test_kbps(self):
        self.assertEqual(humanize_speed(100), '100 Kbps')

    def test_kbps_low(self):
        self.assertEqual(humanize_speed(1), '1 Kbps')

    # Mbps (1,000 – 999,999)

    def test_mbps_whole(self):
        self.assertEqual(humanize_speed(100_000), '100 Mbps')

    def test_mbps_decimal(self):
        self.assertEqual(humanize_speed(1_544), '1.544 Mbps')

    def test_mbps_10(self):
        self.assertEqual(humanize_speed(10_000), '10 Mbps')

    # Gbps (1,000,000 – 999,999,999)

    def test_gbps_whole(self):
        self.assertEqual(humanize_speed(1_000_000), '1 Gbps')

    def test_gbps_decimal(self):
        self.assertEqual(humanize_speed(2_500_000), '2.5 Gbps')

    def test_gbps_10(self):
        self.assertEqual(humanize_speed(10_000_000), '10 Gbps')

    def test_gbps_25(self):
        self.assertEqual(humanize_speed(25_000_000), '25 Gbps')

    def test_gbps_40(self):
        self.assertEqual(humanize_speed(40_000_000), '40 Gbps')

    def test_gbps_100(self):
        self.assertEqual(humanize_speed(100_000_000), '100 Gbps')

    def test_gbps_400(self):
        self.assertEqual(humanize_speed(400_000_000), '400 Gbps')

    def test_gbps_800(self):
        self.assertEqual(humanize_speed(800_000_000), '800 Gbps')

    # Tbps (1,000,000,000+)

    def test_tbps_whole(self):
        self.assertEqual(humanize_speed(1_000_000_000), '1 Tbps')

    def test_tbps_decimal(self):
        self.assertEqual(humanize_speed(1_600_000_000), '1.6 Tbps')

    # Edge cases

    def test_string_input(self):
        """Ensure string values are cast to int correctly."""
        self.assertEqual(humanize_speed('2500000'), '2.5 Gbps')

    def test_non_round_remainder_preserved(self):
        """Ensure fractional parts with interior zeros are preserved."""
        self.assertEqual(humanize_speed(1_001_000), '1.001 Gbps')

    def test_trailing_zeros_stripped(self):
        """Ensure trailing fractional zeros are stripped (5.500 → 5.5)."""
        self.assertEqual(humanize_speed(5_500_000), '5.5 Gbps')
