from django.test import TestCase

from core.forms import ConfigRevisionForm


class ConfigRevisionFormTestCase(TestCase):

    def test_code_fields_render_monospace(self):
        """
        Config parameters that hold markup or code (banners, JSON) must render their
        textareas in a monospace font. See #8974 and #22889.
        """
        form = ConfigRevisionForm()
        monospace_fields = (
            'BANNER_LOGIN',
            'BANNER_MAINTENANCE',
            'BANNER_TOP',
            'BANNER_BOTTOM',
            'CUSTOM_VALIDATORS',
            'PROTECTION_RULES',
        )
        for name in monospace_fields:
            with self.subTest(field=name):
                css_classes = form[name].field.widget.attrs.get('class', '').split()
                self.assertIn('font-monospace', css_classes)
