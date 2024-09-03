from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import TestCase, override_settings

from dcim.choices import SiteStatusChoices
from dcim.models import Site, Region
from extras.validators import CustomValidator
from ipam.models import ASN, RIR
from users.models import User
from utilities.exceptions import AbortRequest
from utilities.request import NetBoxFakeRequest


class MyValidator(CustomValidator):

    def validate(self, instance, request):
        if instance.name != 'foo':
            self.fail("Name must be foo!")


eq_validator = CustomValidator({
    'asn': {
        'eq': 100
    }
})


neq_validator = CustomValidator({
    'asn': {
        'neq': 100
    }
})


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


region_validator = CustomValidator({
    'region.name': {
        'eq': 'Bar',
    }
})


request_validator = CustomValidator({
    'request.user.username': {
        'eq': 'Bob'
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

    @override_settings(CUSTOM_VALIDATORS={'ipam.asn': [eq_validator]})
    def test_eq(self):
        ASN(asn=100, rir=RIR.objects.first()).clean()
        with self.assertRaises(ValidationError):
            ASN(asn=99, rir=RIR.objects.first()).clean()

    @override_settings(CUSTOM_VALIDATORS={'ipam.asn': [neq_validator]})
    def test_neq(self):
        ASN(asn=99, rir=RIR.objects.first()).clean()
        with self.assertRaises(ValidationError):
            ASN(asn=100, rir=RIR.objects.first()).clean()

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

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [region_validator]})
    def test_valid(self):
        region1 = Region(name='Foo', slug='foo')
        region1.save()
        region2 = Region(name='Bar', slug='bar')
        region2.save()

        # Invalid region
        with self.assertRaises(ValidationError):
            Site(name='abcdef123', slug='abcdef123', region=region1).clean()

        # Valid region
        Site(name='abcdef123', slug='abcdef123', region=region2).clean()

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [custom_validator]})
    def test_custom_invalid(self):
        with self.assertRaises(ValidationError):
            Site(name='abc', slug='abc').clean()

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [custom_validator]})
    def test_custom_valid(self):
        Site(name='foo', slug='foo').clean()

    @override_settings(CUSTOM_VALIDATORS={'dcim.site': [request_validator]})
    def test_request_validation(self):
        alice = User.objects.create(username='Alice')
        bob = User.objects.create(username='Bob')
        request = NetBoxFakeRequest({
            'META': {},
            'POST': {},
            'GET': {},
            'FILES': {},
            'user': alice,
            'path': '',
        })
        site = Site(name='abc', slug='abc')

        # Attempt to create the Site as Alice
        with self.assertRaises(ValidationError):
            request_validator(site, request)

        # Creating the Site as Bob should succeed
        request.user = bob
        request_validator(site, request)


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
                'extras.tests.test_customvalidators.MyValidator',
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


class ProtectionRulesConfigTest(TestCase):

    @override_settings(
        PROTECTION_RULES={
            'dcim.site': [
                {'status': {'eq': SiteStatusChoices.STATUS_DECOMMISSIONING}}
            ]
        }
    )
    def test_plain_data(self):
        """
        Test custom validator configuration using plain data (as opposed to a CustomValidator
        class)
        """
        # Create a site with a protected status
        site = Site(name='Site 1', slug='site-1', status=SiteStatusChoices.STATUS_ACTIVE)
        site.save()

        # Try to delete it
        with self.assertRaises(AbortRequest):
            with transaction.atomic():
                site.delete()

        # Change its status to an allowed value
        site.status = SiteStatusChoices.STATUS_DECOMMISSIONING
        site.save()

        # Deletion should now succeed
        site.delete()

    @override_settings(
        PROTECTION_RULES={
            'dcim.site': (
                'extras.tests.test_customvalidators.MyValidator',
            )
        }
    )
    def test_dotted_path(self):
        """
        Test custom validator configuration using a dotted path (string) reference to a
        CustomValidator class.
        """
        # Create a site with a protected name
        site = Site(name='bar', slug='bar')
        site.save()

        # Try to delete it
        with self.assertRaises(AbortRequest):
            with transaction.atomic():
                site.delete()

        # Change the name to an allowed value
        site.name = site.slug = 'foo'
        site.save()

        # Deletion should now succeed
        site.delete()
