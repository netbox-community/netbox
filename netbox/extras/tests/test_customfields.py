from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from dcim.models import Site

from extras.models import (
    CustomField, CustomFieldValue, CustomFieldChoice, CF_TYPE_TEXT, CF_TYPE_INTEGER, CF_TYPE_BOOLEAN, CF_TYPE_DATE,
    CF_TYPE_SELECT,
)


class RackTestCase(TestCase):

    def setUp(self):

        Site.objects.bulk_create([
            Site(name='Site A', slug='site-a'),
            Site(name='Site B', slug='site-b'),
            Site(name='Site C', slug='site-c'),
        ])

    def test_simple_fields(self):

        DATA = (
            {'field_type': CF_TYPE_TEXT, 'field_value': 'Foobar!', 'empty_value': ''},
            {'field_type': CF_TYPE_INTEGER, 'field_value': 0, 'empty_value': None},
            {'field_type': CF_TYPE_INTEGER, 'field_value': 42, 'empty_value': None},
            {'field_type': CF_TYPE_BOOLEAN, 'field_value': True, 'empty_value': None},
            {'field_type': CF_TYPE_BOOLEAN, 'field_value': False, 'empty_value': None},
            {'field_type': CF_TYPE_DATE, 'field_value': date(2016, 6, 23), 'empty_value': None},
        )

        obj_type = ContentType.objects.get_for_model(Site)

        for data in DATA:

            # Create a custom field
            cf = CustomField(type=data['field_type'], name='my_field', required=False)
            cf.save()
            cf.obj_type = [obj_type]
            cf.save()

            # Assign a value to the first Site
            site = Site.objects.first()
            cfv = CustomFieldValue(field=cf, obj_type=obj_type, obj_id=site.id)
            cfv.value = data['field_value']
            cfv.save()

            # Retrieve the stored value
            cfv = CustomFieldValue.objects.filter(obj_type=obj_type, obj_id=site.pk).first()
            self.assertEqual(cfv.value, data['field_value'])

            # Delete the stored value
            cfv.value = data['empty_value']
            cfv.save()
            self.assertEqual(CustomFieldValue.objects.filter(obj_type=obj_type, obj_id=site.pk).count(), 0)

            # Delete the custom field
            cf.delete()

    def test_select_field(self):

        obj_type = ContentType.objects.get_for_model(Site)

        # Create a custom field
        cf = CustomField(type=CF_TYPE_SELECT, name='my_field', required=False)
        cf.save()
        cf.obj_type = [obj_type]
        cf.save()

        # Create some choices for the field
        CustomFieldChoice.objects.bulk_create([
            CustomFieldChoice(field=cf, value='Option A'),
            CustomFieldChoice(field=cf, value='Option B'),
            CustomFieldChoice(field=cf, value='Option C'),
        ])

        # Assign a value to the first Site
        site = Site.objects.first()
        cfv = CustomFieldValue(field=cf, obj_type=obj_type, obj_id=site.id)
        cfv.value = cf.choices.first()
        cfv.save()

        # Retrieve the stored value
        cfv = CustomFieldValue.objects.filter(obj_type=obj_type, obj_id=site.pk).first()
        self.assertEqual(str(cfv.value), 'Option A')

        # Delete the stored value
        cfv.value = None
        cfv.save()
        self.assertEqual(CustomFieldValue.objects.filter(obj_type=obj_type, obj_id=site.pk).count(), 0)

        # Delete the custom field
        cf.delete()
