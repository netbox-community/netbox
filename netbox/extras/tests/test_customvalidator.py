from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from dcim.models import Site
from extras.validators import CustomValidator


class MyValidator(CustomValidator):

    def validate(self, instance):
        if instance.name != 'foo':
            self.fail("Name must be foo!")


stock_validator = CustomValidator({
    'name': {
        'min_length': 5,
        'max_length': 10,
        'regex': r'\d{3}$',  # Ends with three digits
    },
    'asn': {
        'min': 65000,
        'max': 65100,
    }
})

custom_validator = MyValidator()


class CustomValidatorTest(TestCase):

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [stock_validator]})
    def test_configuration(self):
        self.assertIn('dcim.site', settings.CUSTOM_VALIDATORS)
        validator = settings.CUSTOM_VALIDATORS['dcim.site'][0]
        self.assertIsInstance(validator, CustomValidator)

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [stock_validator]})
    def test_min(self):
        with self.assertRaises(ValidationError):
            Site(name='abcdef123', slug='abcdefghijk', asn=1).clean()

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [stock_validator]})
    def test_max(self):
        with self.assertRaises(ValidationError):
            Site(name='abcdef123', slug='abcdefghijk', asn=65535).clean()

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [stock_validator]})
    def test_min_length(self):
        with self.assertRaises(ValidationError):
            Site(name='abc', slug='abc', asn=65000).clean()

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [stock_validator]})
    def test_max_length(self):
        with self.assertRaises(ValidationError):
            Site(name='abcdefghijk', slug='abcdefghijk', asn=65000).clean()

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [stock_validator]})
    def test_regex(self):
        with self.assertRaises(ValidationError):
            Site(name='abcdefgh', slug='abcdefgh', asn=65000).clean()

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [stock_validator]})
    def test_valid(self):
        Site(name='abcdef123', slug='abcdef123', asn=65000).clean()

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [custom_validator]})
    def test_custom_invalid(self):
        with self.assertRaises(ValidationError):
            Site(name='abc', slug='abc', asn=65000).clean()

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [custom_validator]})
    def test_custom_valid(self):
        Site(name='foo', slug='foo', asn=65000).clean()
