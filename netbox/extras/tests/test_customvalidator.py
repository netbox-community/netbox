from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from dcim.models import Site
from extras.validators import CustomValidator


class MyValidator(CustomValidator):

    def validate(self, instance):
        if instance.name != 'foo':
            self.fail("Name must be foo!")


min_validator = CustomValidator({
    'asn': {
        'min': 65000
    }
})


max_validator = CustomValidator({
    'asn': {
        'max': 65100
    }
})


min_length_validator = CustomValidator({
    'name': {
        'min_length': 5
    }
})


max_length_validator = CustomValidator({
    'name': {
        'max_length': 10
    }
})


regex_validator = CustomValidator({
    'name': {
        'regex': r'\d{3}$'  # Ends with three digits
    }
})


required_validator = CustomValidator({
    'description': {
        'required': True
    }
})


prohibited_validator = CustomValidator({
    'description': {
        'prohibited': True
    }
})

custom_validator = MyValidator()


class CustomValidatorTest(TestCase):

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [min_validator]})
    def test_configuration(self):
        self.assertIn('dcim.site', settings.CUSTOM_VALIDATORS)
        validator = settings.CUSTOM_VALIDATORS['dcim.site'][0]
        self.assertIsInstance(validator, CustomValidator)

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [min_validator]})
    def test_min(self):
        with self.assertRaises(ValidationError):
            Site(name='abcdef123', slug='abcdefghijk', asn=1).clean()

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [max_validator]})
    def test_max(self):
        with self.assertRaises(ValidationError):
            Site(name='abcdef123', slug='abcdefghijk', asn=65535).clean()

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [min_length_validator]})
    def test_min_length(self):
        with self.assertRaises(ValidationError):
            Site(name='abc', slug='abc', asn=65000).clean()

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [max_length_validator]})
    def test_max_length(self):
        with self.assertRaises(ValidationError):
            Site(name='abcdefghijk', slug='abcdefghijk').clean()

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [regex_validator]})
    def test_regex(self):
        with self.assertRaises(ValidationError):
            Site(name='abcdefgh', slug='abcdefgh').clean()

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [required_validator]})
    def test_required(self):
        with self.assertRaises(ValidationError):
            Site(name='abcdefgh', slug='abcdefgh', description='').clean()

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [prohibited_validator]})
    def test_prohibited(self):
        with self.assertRaises(ValidationError):
            Site(name='abcdefgh', slug='abcdefgh', description='ABC').clean()

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [min_length_validator]})
    def test_valid(self):
        Site(name='abcdef123', slug='abcdef123').clean()

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [custom_validator]})
    def test_custom_invalid(self):
        with self.assertRaises(ValidationError):
            Site(name='abc', slug='abc').clean()

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [custom_validator]})
    def test_custom_valid(self):
        Site(name='foo', slug='foo').clean()
