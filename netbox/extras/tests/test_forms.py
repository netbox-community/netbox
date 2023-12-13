from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings

from circuits.forms import ProviderForm
from dcim.forms import SiteForm
from dcim.models import Site
from extras.choices import CustomFieldTypeChoices
from extras.forms import SavedFilterForm
from extras.models import CustomField, CustomFieldChoiceSet
from ipam.models import ASN, RIR
from utilities.testing import create_tags


class CustomFieldModelFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        obj_type = ContentType.objects.get_for_model(Site)
        choice_set = CustomFieldChoiceSet.objects.create(
            name='Choice Set 1',
            extra_choices=(('a', 'A'), ('b', 'B'), ('c', 'C'))
        )

        cf_text = CustomField.objects.create(name='text', type=CustomFieldTypeChoices.TYPE_TEXT)
        cf_text.content_types.set([obj_type])

        cf_longtext = CustomField.objects.create(name='longtext', type=CustomFieldTypeChoices.TYPE_LONGTEXT)
        cf_longtext.content_types.set([obj_type])

        cf_integer = CustomField.objects.create(name='integer', type=CustomFieldTypeChoices.TYPE_INTEGER)
        cf_integer.content_types.set([obj_type])

        cf_integer = CustomField.objects.create(name='decimal', type=CustomFieldTypeChoices.TYPE_DECIMAL)
        cf_integer.content_types.set([obj_type])

        cf_boolean = CustomField.objects.create(name='boolean', type=CustomFieldTypeChoices.TYPE_BOOLEAN)
        cf_boolean.content_types.set([obj_type])

        cf_date = CustomField.objects.create(name='date', type=CustomFieldTypeChoices.TYPE_DATE)
        cf_date.content_types.set([obj_type])

        cf_datetime = CustomField.objects.create(name='datetime', type=CustomFieldTypeChoices.TYPE_DATETIME)
        cf_datetime.content_types.set([obj_type])

        cf_url = CustomField.objects.create(name='url', type=CustomFieldTypeChoices.TYPE_URL)
        cf_url.content_types.set([obj_type])

        cf_json = CustomField.objects.create(name='json', type=CustomFieldTypeChoices.TYPE_JSON)
        cf_json.content_types.set([obj_type])

        cf_select = CustomField.objects.create(
            name='select',
            type=CustomFieldTypeChoices.TYPE_SELECT,
            choice_set=choice_set
        )
        cf_select.content_types.set([obj_type])

        cf_multiselect = CustomField.objects.create(
            name='multiselect',
            type=CustomFieldTypeChoices.TYPE_MULTISELECT,
            choice_set=choice_set
        )
        cf_multiselect.content_types.set([obj_type])

        cf_object = CustomField.objects.create(
            name='object',
            type=CustomFieldTypeChoices.TYPE_OBJECT,
            object_type=ContentType.objects.get_for_model(Site)
        )
        cf_object.content_types.set([obj_type])

        cf_multiobject = CustomField.objects.create(
            name='multiobject',
            type=CustomFieldTypeChoices.TYPE_MULTIOBJECT,
            object_type=ContentType.objects.get_for_model(Site)
        )
        cf_multiobject.content_types.set([obj_type])

    def test_empty_values(self):
        """
        Test that empty custom field values are stored as null
        """
        form = SiteForm({
            'name': 'Site 1',
            'slug': 'site-1',
            'status': 'active',
        })
        self.assertTrue(form.is_valid())
        instance = form.save()

        for field_type, _ in CustomFieldTypeChoices.CHOICES:
            self.assertIn(field_type, instance.custom_field_data)
            self.assertIsNone(instance.custom_field_data[field_type])


class SavedFilterFormTest(TestCase):

    def test_basic_submit(self):
        """
        Test form submission and validation
        """
        form = SavedFilterForm({
            'name': 'test-sf',
            'slug': 'test-sf',
            'content_types': [ContentType.objects.get_for_model(Site).pk],
            'weight': 100,
            'parameters': {
                "status": [
                    "active"
                ]
            }
        })
        self.assertTrue(form.is_valid())
        form.save()


class CustomValidationTest(TestCase):

    @override_settings(CUSTOM_VALIDATORS={
        'circuits.provider': [
            {'tags': {'required': True}}
        ]
    })
    def test_tags_validation(self):
        """
        Check that custom validation rules work for tag assignment.
        """
        data = {
            'name': 'Provider 1',
            'slug': 'provider-1',
        }
        form = ProviderForm(data)
        self.assertFalse(form.is_valid())

        tags = create_tags('Tag1', 'Tag2', 'Tag3')
        data['tags'] = [tag.pk for tag in tags]
        form = ProviderForm(data)
        self.assertTrue(form.is_valid())

    @override_settings(CUSTOM_VALIDATORS={
        'circuits.provider': [
            {'asns': {'required': True}}
        ]
    })
    def test_m2m_validation(self):
        """
        Check that custom validation rules work for many-to-many fields.
        """
        data = {
            'name': 'Provider 1',
            'slug': 'provider-1',
        }
        form = ProviderForm(data)
        self.assertFalse(form.is_valid())

        rir = RIR.objects.create(name='RIR 1', slug='rir-1')
        asns = ASN.objects.bulk_create((
            ASN(rir=rir, asn=65001),
            ASN(rir=rir, asn=65002),
            ASN(rir=rir, asn=65003),
        ))
        data['asns'] = [asn.pk for asn in asns]
        form = ProviderForm(data)
        self.assertTrue(form.is_valid())
