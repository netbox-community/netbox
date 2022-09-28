from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from ipam.models import ASN, RIR
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

    @classmethod
    def setUpTestData(cls):
        RIR.objects.create(name='RIR 1', slug='rir-1')

    @override_settings(CUSTOM_VALIDATORS={'ipam.asn': [min_validator]})
    def test_configuration(self):
        self.assertIn('ipam.asn', settings.CUSTOM_VALIDATORS)
        validator = settings.CUSTOM_VALIDATORS['ipam.asn'][0]
        self.assertIsInstance(validator, CustomValidator)

    @override_settings(CUSTOM_VALIDATORS={'ipam.asn': [min_validator]})
    def test_min(self):
        with self.assertRaises(ValidationError):
            ASN(asn=1, rir=RIR.objects.first()).clean()

    @override_settings(CUSTOM_VALIDATORS={'ipam.asn': [max_validator]})
    def test_max(self):
        with self.assertRaises(ValidationError):
            ASN(asn=65535, rir=RIR.objects.first()).clean()

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [min_length_validator]})
    def test_min_length(self):
        with self.assertRaises(ValidationError):
            Site(name='abc', slug='abc').clean()

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


class CustomValidatorConfigTest(TestCase):

    @override_settings(
        CUSTOM_VALIDATORS={
            'dcim.site': [
                {'name': {'min_length': 5}}
            ]
        }
    )
    def test_plain_data(self):
        """
        Test custom validator configuration using plain data (as opposed to a CustomValidator
        class)
        """
        with self.assertRaises(ValidationError):
            Site(name='abcd', slug='abcd').clean()
        Site(name='abcde', slug='abcde').clean()

    @override_settings(
        CUSTOM_VALIDATORS={
            'dcim.site': (
                'extras.tests.test_customvalidator.MyValidator',
            )
        }
    )
    def test_dotted_path(self):
        """
        Test custom validator configuration using a dotted path (string) reference to a
        CustomValidator class.
        """
        Site(name='foo', slug='foo').clean()
        with self.assertRaises(ValidationError):
            Site(name='bar', slug='bar').clean()
