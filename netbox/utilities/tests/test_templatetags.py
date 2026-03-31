from unittest.mock import patch

from django.test import TestCase, override_settings

from utilities.templatetags.builtins.tags import static_with_params
from utilities.templatetags.helpers import _humanize_capacity


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
