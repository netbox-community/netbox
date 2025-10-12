from unittest.mock import patch

from django.test import TestCase, override_settings

from utilities.templatetags.builtins.tags import static_with_params


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
