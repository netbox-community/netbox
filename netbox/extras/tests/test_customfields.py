import datetime
import json
import uuid
from collections import defaultdict
from contextlib import contextmanager
from decimal import Decimal
from unittest.mock import patch

import django_filters
from django.core.exceptions import ValidationError
from django.db import DEFAULT_DB_ALIAS, connection, connections, transaction
from django.db.models import QuerySet
from django.db.models.signals import pre_delete
from django.test import RequestFactory, override_settings, tag
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status

from core.choices import ObjectChangeActionChoices
from core.models import Job, ObjectChange, ObjectType
from dcim.filtersets import SiteFilterSet
from dcim.forms import SiteImportForm
from dcim.models import Manufacturer, Rack, Site
from dcim.tables import SiteTable
from extras.choices import *
from extras.constants import CUSTOMFIELD_JOB_TIMEOUT
from extras.filters import MissingKeyAwareFilterMixin, missing_key_aware_filter_factory
from extras.jobs import (
    CustomFieldProvisioningJob,
    CustomFieldPurgeJob,
    provision_custom_field,
    purge_custom_field,
)
from extras.models import CustomField, CustomFieldChoiceSet
from ipam.models import VLAN
from netbox.choices import CSVDelimiterChoices, ImportFormatChoices
from netbox.context import query_cache
from netbox.context_managers import event_tracking
from netbox.tables.columns import CustomFieldColumn
from utilities.exceptions import AbortRequest
from utilities.filters import MultiValueCharFilter, MultiValueMACAddressFilter
from utilities.testing import APITestCase, TestCase
from virtualization.models import VirtualMachine


def get_primary_table_queries(queries, model):
    """Return the SQL of captured queries that read from the model's table as the primary relation."""
    table = connection.ops.quote_name(model._meta.db_table)
    return [q['sql'] for q in queries if f'FROM {table}' in q['sql']]


class CustomFieldTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):

        Site.objects.bulk_create([
            Site(name='Site A', slug='site-a'),
            Site(name='Site B', slug='site-b'),
            Site(name='Site C', slug='site-c'),
        ])

        cls.object_type = ObjectType.objects.get_for_model(Site)

    def test_invalid_name(self):
        """
        Try creating a CustomField with an invalid name.
        """
        with self.assertRaises(ValidationError):
            # Invalid character
            CustomField(name='?', type=CustomFieldTypeChoices.TYPE_TEXT).full_clean()
        with self.assertRaises(ValidationError):
            # Double underscores not permitted
            CustomField(name='foo__bar', type=CustomFieldTypeChoices.TYPE_TEXT).full_clean()

    def test_text_field(self):
        value = 'Foobar!'

        # Create a custom field & check that no initial data is written
        cf = CustomField.objects.create(
            name='text_field',
            type=CustomFieldTypeChoices.TYPE_TEXT,
            required=False
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertNotIn(cf.name, instance.custom_field_data)

        # Assign a value and check that it is saved
        instance.custom_field_data[cf.name] = value
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.custom_field_data[cf.name], value)

        # Delete the stored value and check that it is now null
        instance.custom_field_data.pop(cf.name)
        instance.save()
        instance.refresh_from_db()
        self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_nulls_first_ordering(self):
        """
        Verify that CustomFieldColumn.order() places null values first or last according to the
        custom field's nulls_first attribute.
        """
        cf = CustomField.objects.create(
            name='order_field',
            type=CustomFieldTypeChoices.TYPE_INTEGER,
            required=False
        )
        cf.object_types.set([self.object_type])

        # Assign values to two of the three sites, leaving the third null
        site_a = Site.objects.get(name='Site A')
        site_a.custom_field_data[cf.name] = 1
        site_a.save()
        site_b = Site.objects.get(name='Site B')
        site_b.custom_field_data[cf.name] = 2
        site_b.save()
        site_c = Site.objects.get(name='Site C')  # no value (null)

        column = CustomFieldColumn(cf)

        # nulls_first=True (default): null value sorts before populated values when ascending
        cf.nulls_first = True
        queryset, _ = column.order(Site.objects.all(), is_descending=False)
        self.assertEqual(list(queryset), [site_c, site_a, site_b])

        # nulls_first=False: null value sorts after populated values when ascending
        cf.nulls_first = False
        queryset, _ = column.order(Site.objects.all(), is_descending=False)
        self.assertEqual(list(queryset), [site_a, site_b, site_c])

        # Null placement is independent of sort direction: nulls_first=True keeps the null value
        # first even when sorting descending
        cf.nulls_first = True
        queryset, _ = column.order(Site.objects.all(), is_descending=True)
        self.assertEqual(list(queryset), [site_c, site_b, site_a])

        # nulls_first=False keeps the null value last even when sorting descending
        cf.nulls_first = False
        queryset, _ = column.order(Site.objects.all(), is_descending=True)
        self.assertEqual(list(queryset), [site_b, site_a, site_c])

    def test_longtext_field(self):
        value = 'A' * 256

        # Create a custom field & check that no initial data is written
        cf = CustomField.objects.create(
            name='longtext_field',
            type=CustomFieldTypeChoices.TYPE_LONGTEXT,
            required=False
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertNotIn(cf.name, instance.custom_field_data)

        # Assign a value and check that it is saved
        instance.custom_field_data[cf.name] = value
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.custom_field_data[cf.name], value)

        # Delete the stored value and check that it is now null
        instance.custom_field_data.pop(cf.name)
        instance.save()
        instance.refresh_from_db()
        self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_integer_field(self):

        # Create a custom field & check that no initial data is written
        cf = CustomField.objects.create(
            name='integer_field',
            type=CustomFieldTypeChoices.TYPE_INTEGER,
            required=False
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertNotIn(cf.name, instance.custom_field_data)

        for value in (123456, 0, -123456):

            # Assign a value and check that it is saved
            instance.custom_field_data[cf.name] = value
            instance.save()
            instance.refresh_from_db()
            self.assertEqual(instance.custom_field_data[cf.name], value)

            # Delete the stored value and check that it is now null
            instance.custom_field_data.pop(cf.name)
            instance.save()
            instance.refresh_from_db()
            self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_decimal_field(self):

        # Create a custom field & check that no initial data is written
        cf = CustomField.objects.create(
            name='decimal_field',
            type=CustomFieldTypeChoices.TYPE_DECIMAL,
            required=False
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertNotIn(cf.name, instance.custom_field_data)

        for value in (123456.54, 0, -123456.78):

            # Assign a value and check that it is saved
            instance.custom_field_data[cf.name] = value
            instance.save()
            instance.refresh_from_db()
            self.assertEqual(instance.custom_field_data[cf.name], value)

            # Delete the stored value and check that it is now null
            instance.custom_field_data.pop(cf.name)
            instance.save()
            instance.refresh_from_db()
            self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_boolean_field(self):

        # Create a custom field & check that no initial data is written
        cf = CustomField.objects.create(
            name='boolean_field',
            type=CustomFieldTypeChoices.TYPE_INTEGER,
            required=False
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertNotIn(cf.name, instance.custom_field_data)

        for value in (True, False):

            # Assign a value and check that it is saved
            instance.custom_field_data[cf.name] = value
            instance.save()
            instance.refresh_from_db()
            self.assertEqual(instance.custom_field_data[cf.name], value)

            # Delete the stored value and check that it is now null
            instance.custom_field_data.pop(cf.name)
            instance.save()
            instance.refresh_from_db()
            self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_date_field(self):
        value = datetime.date(2016, 6, 23)

        # Create a custom field & check that no initial data is written
        cf = CustomField.objects.create(
            name='date_field',
            type=CustomFieldTypeChoices.TYPE_DATE,
            required=False
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertNotIn(cf.name, instance.custom_field_data)

        # Assign a value and check that it is saved
        instance.custom_field_data[cf.name] = cf.serialize(value)
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.cf[cf.name], value)

        # Delete the stored value and check that it is now null
        instance.custom_field_data.pop(cf.name)
        instance.save()
        instance.refresh_from_db()
        self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_datetime_field(self):
        value = datetime.datetime(2016, 6, 23, 9, 45, 0)

        # Create a custom field & check that no initial data is written
        cf = CustomField.objects.create(
            name='date_field',
            type=CustomFieldTypeChoices.TYPE_DATETIME,
            required=False
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertNotIn(cf.name, instance.custom_field_data)

        # Assign a value and check that it is saved
        instance.custom_field_data[cf.name] = cf.serialize(value)
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.cf[cf.name], value)

        # Delete the stored value and check that it is now null
        instance.custom_field_data.pop(cf.name)
        instance.save()
        instance.refresh_from_db()
        self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_url_field(self):
        value = 'http://example.com/'

        # Create a custom field & check that no initial data is written
        cf = CustomField.objects.create(
            name='url_field',
            type=CustomFieldTypeChoices.TYPE_URL,
            required=False
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertNotIn(cf.name, instance.custom_field_data)

        # Assign a value and check that it is saved
        instance.custom_field_data[cf.name] = value
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.custom_field_data[cf.name], value)

        # Delete the stored value and check that it is now null
        instance.custom_field_data.pop(cf.name)
        instance.save()
        instance.refresh_from_db()
        self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_json_field(self):
        value = '{"foo": 1, "bar": 2}'

        # Create a custom field & check that no initial data is written
        cf = CustomField.objects.create(
            name='json_field',
            type=CustomFieldTypeChoices.TYPE_JSON,
            required=False
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertNotIn(cf.name, instance.custom_field_data)

        # Assign a value and check that it is saved
        instance.custom_field_data[cf.name] = value
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.custom_field_data[cf.name], value)

        # Delete the stored value and check that it is now null
        instance.custom_field_data.pop(cf.name)
        instance.save()
        instance.refresh_from_db()
        self.assertIsNone(instance.custom_field_data.get(cf.name))

    @tag('regression')
    def test_json_field_falsy_defaults(self):
        """Test that falsy JSON default values are properly handled"""
        falsy_test_cases = [
            ({}, 'empty_dict'),
            ([], 'empty_array'),
            (0, 'zero'),
            (False, 'false_bool'),
            ("", 'empty_string'),
        ]

        for default, suffix in falsy_test_cases:
            with self.subTest(default=default, suffix=suffix):
                cf = CustomField.objects.create(
                    name=f'json_falsy_{suffix}',
                    type=CustomFieldTypeChoices.TYPE_JSON,
                    default=default,
                    required=False
                )
                cf.object_types.set([self.object_type])

                instance = Site.objects.create(name=f'Test Site {suffix}', slug=f'test-site-{suffix}')

                self.assertIsNotNone(instance.custom_field_data)
                self.assertIn(cf.name, instance.custom_field_data)

                instance.refresh_from_db()
                stored = instance.custom_field_data[cf.name]
                self.assertEqual(stored, default)

    @tag('regression')
    def test_json_field_falsy_to_form_field(self):
        """Test form field generation preserves falsy defaults"""
        falsy_test_cases = (
            ({}, json.dumps({}), 'empty_dict'),
            ([], json.dumps([]), 'empty_array'),
            (0, json.dumps(0), 'zero'),
            (False, json.dumps(False), 'false_bool'),
            ("", '""', 'empty_string'),
        )

        for default, expected, suffix in falsy_test_cases:
            with self.subTest(default=default, expected=expected, suffix=suffix):
                cf = CustomField.objects.create(
                    name=f'json_falsy_{suffix}',
                    type=CustomFieldTypeChoices.TYPE_JSON,
                    default=default,
                    required=False
                )
                cf.object_types.set([self.object_type])

                form_field = cf.to_form_field(set_initial=True)
                self.assertEqual(form_field.initial, expected)

    def test_select_field(self):
        CHOICES = (
            ('a', 'Option A'),
            ('b', 'Option B'),
            ('c', 'Option C'),
        )
        value = 'a'

        # Create a set of custom field choices
        choice_set = CustomFieldChoiceSet.objects.create(
            name='Custom Field Choice Set 1',
            extra_choices=CHOICES
        )

        # Create a custom field & check that no initial data is written
        cf = CustomField.objects.create(
            name='select_field',
            type=CustomFieldTypeChoices.TYPE_SELECT,
            required=False,
            choice_set=choice_set
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertNotIn(cf.name, instance.custom_field_data)

        # Assign a value and check that it is saved
        instance.custom_field_data[cf.name] = value
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.custom_field_data[cf.name], value)

        # Delete the stored value and check that it is now null
        instance.custom_field_data.pop(cf.name)
        instance.save()
        instance.refresh_from_db()
        self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_multiselect_field(self):
        CHOICES = (
            ('a', 'Option A'),
            ('b', 'Option B'),
            ('c', 'Option C'),
        )
        value = ['a', 'b']

        # Create a set of custom field choices
        choice_set = CustomFieldChoiceSet.objects.create(
            name='Custom Field Choice Set 1',
            extra_choices=CHOICES
        )

        # Create a custom field & check that no initial data is written
        cf = CustomField.objects.create(
            name='multiselect_field',
            type=CustomFieldTypeChoices.TYPE_MULTISELECT,
            required=False,
            choice_set=choice_set
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertNotIn(cf.name, instance.custom_field_data)

        # Assign a value and check that it is saved
        instance.custom_field_data[cf.name] = value
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.custom_field_data[cf.name], value)

        # Delete the stored value and check that it is now null
        instance.custom_field_data.pop(cf.name)
        instance.save()
        instance.refresh_from_db()
        self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_choice_set_colors(self):
        choice_set = CustomFieldChoiceSet(
            name='Test Choice Set',
            extra_choices=(
                ('a', 'Option A'),
                ('b', 'Option B'),
            ),
            choice_colors={
                'a': CustomFieldChoiceColorChoices.RED,
                'b': CustomFieldChoiceColorChoices.GREEN,
            },
        )
        choice_set.full_clean()

        self.assertEqual(
            choice_set.colors,
            {
                'a': CustomFieldChoiceColorChoices.RED,
                'b': CustomFieldChoiceColorChoices.GREEN,
            },
        )

    def test_choice_set_invalid_color_mapping_value(self):
        choice_set = CustomFieldChoiceSet(
            name='Test Choice Set',
            extra_choices=(
                ('a', 'Option A'),
                ('b', 'Option B'),
            ),
            choice_colors={'c': CustomFieldChoiceColorChoices.RED},
        )

        with self.assertRaises(ValidationError) as cm:
            choice_set.full_clean()

        self.assertIn('choice_colors', cm.exception.message_dict)

    def test_choice_set_invalid_color_value(self):
        choice_set = CustomFieldChoiceSet(
            name='Test Choice Set',
            extra_choices=(
                ('a', 'Option A'),
                ('b', 'Option B'),
            ),
            choice_colors={'a': 'magenta'},
        )

        with self.assertRaises(ValidationError) as cm:
            choice_set.full_clean()

        self.assertIn('choice_colors', cm.exception.message_dict)

    def test_choice_set_invalid_color_mapping_structure(self):
        choice_set = CustomFieldChoiceSet(
            name='Test Choice Set',
            extra_choices=(
                ('a', 'Option A'),
                ('b', 'Option B'),
            ),
            choice_colors=['a:red'],
        )

        with self.assertRaises(ValidationError) as cm:
            choice_set.full_clean()

        self.assertIn('choice_colors', cm.exception.message_dict)

    @tag('regression')
    def test_choice_set_with_base_choices_validates_without_error(self):
        """Regression test for #22325: base-only choice sets must validate."""
        for base in ('IATA', 'ISO_3166', 'UN_LOCODE'):
            with self.subTest(base=base):
                choice_set = CustomFieldChoiceSet(name=f'Test {base}', base_choices=base, order_alphabetically=True)
                choice_set.full_clean()  # must not raise
                choice_set.save()        # must not raise (extra_choices is None)

    def test_remove_selected_choice(self):
        """
        Removing a ChoiceSet choice that is referenced by an object should raise
        a ValidationError exception.
        """
        CHOICES = (
            ('a', 'Option A'),
            ('b', 'Option B'),
            ('c', 'Option C'),
            ('d', 'Option D'),
        )

        # Create a set of custom field choices
        choice_set = CustomFieldChoiceSet.objects.create(
            name='Custom Field Choice Set 1',
            extra_choices=CHOICES
        )

        # Create a select custom field
        cf = CustomField.objects.create(
            name='select_field',
            type=CustomFieldTypeChoices.TYPE_SELECT,
            required=False,
            choice_set=choice_set
        )
        cf.object_types.set([self.object_type])

        # Create a multi-select custom field
        cf_multiselect = CustomField.objects.create(
            name='multiselect_field',
            type=CustomFieldTypeChoices.TYPE_MULTISELECT,
            required=False,
            choice_set=choice_set
        )
        cf_multiselect.object_types.set([self.object_type])

        # Assign a choice for both custom fields on an object
        instance = Site.objects.first()
        instance.custom_field_data[cf.name] = 'a'
        instance.custom_field_data[cf_multiselect.name] = ['b', 'c']
        instance.save()

        # Attempting to delete a selected choice should fail
        with self.assertRaises(ValidationError):
            choice_set.extra_choices = (
                ('b', 'Option B'),
                ('c', 'Option C'),
                ('d', 'Option D'),
            )
            choice_set.full_clean()

        # Attempting to delete either of the multi-select choices should fail
        with self.assertRaises(ValidationError):
            choice_set.extra_choices = (
                ('a', 'Option A'),
                ('b', 'Option B'),
                ('d', 'Option D'),
            )
            choice_set.full_clean()

        # Removing a non-selected choice should succeed
        choice_set.extra_choices = (
            ('a', 'Option A'),
            ('b', 'Option B'),
            ('c', 'Option C'),
        )
        choice_set.full_clean()

    def test_object_field(self):
        value = VLAN.objects.create(name='VLAN 1', vid=1).pk

        # Create a custom field & check that no initial data is written
        cf = CustomField.objects.create(
            name='object_field',
            type=CustomFieldTypeChoices.TYPE_OBJECT,
            related_object_type=ObjectType.objects.get_for_model(VLAN),
            required=False
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertNotIn(cf.name, instance.custom_field_data)

        # Assign a value and check that it is saved
        instance.custom_field_data[cf.name] = value
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.custom_field_data[cf.name], value)

        # Delete the stored value and check that it is now null
        instance.custom_field_data.pop(cf.name)
        instance.save()
        instance.refresh_from_db()
        self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_multiobject_field(self):
        vlans = (
            VLAN(name='VLAN 1', vid=1),
            VLAN(name='VLAN 2', vid=2),
            VLAN(name='VLAN 3', vid=3),
        )
        VLAN.objects.bulk_create(vlans)
        value = [vlan.pk for vlan in vlans]

        # Create a custom field & check that no initial data is written
        cf = CustomField.objects.create(
            name='object_field',
            type=CustomFieldTypeChoices.TYPE_MULTIOBJECT,
            related_object_type=ObjectType.objects.get_for_model(VLAN),
            required=False
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertNotIn(cf.name, instance.custom_field_data)

        # Assign a value and check that it is saved
        instance.custom_field_data[cf.name] = value
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.custom_field_data[cf.name], value)

        # Delete the stored value and check that it is now null
        instance.custom_field_data.pop(cf.name)
        instance.save()
        instance.refresh_from_db()
        self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_rename_customfield(self):
        obj_type = ObjectType.objects.get_for_model(Site)
        FIELD_DATA = 'abc'

        # Create a custom field
        cf = CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='field1')
        cf.save()
        cf.object_types.set([obj_type])

        # Assign custom field data to an object
        site = Site.objects.create(
            name='Site 1',
            slug='site-1',
            custom_field_data={'field1': FIELD_DATA}
        )
        site.refresh_from_db()
        self.assertEqual(site.custom_field_data['field1'], FIELD_DATA)

        # Rename the custom field
        cf.name = 'field2'
        cf.save()

        # Check that custom field data on the object has been updated
        site.refresh_from_db()
        self.assertNotIn('field1', site.custom_field_data)
        self.assertEqual(site.custom_field_data['field2'], FIELD_DATA)

    @override_settings(BULK_UPDATE_CHUNK_SIZE=2)
    def test_batched_object_data_updates(self):
        """
        Provisioning, renaming, and removing custom field data is applied in batches. Use a small
        batch size to ensure the data on every object is updated across multiple batches.

        BULK_UPDATE_CHUNK_SIZE doubles as the threshold above which an update is handed to a
        background job, so overriding it this low also puts provisioning and removal onto the
        deferred path; the jobs are run here in place of the worker which would ordinarily do so.
        """
        # The existing sites (created in setUpTestData) span multiple batches of size 2
        site_count = Site.objects.count()
        self.assertGreater(site_count, 2)

        # Provisioning: a default value is populated onto every existing object
        cf = CustomField.objects.create(
            name='batched_field',
            type=CustomFieldTypeChoices.TYPE_TEXT,
            default='foo'
        )
        cf.object_types.set([self.object_type])
        self.assertTrue(provision_custom_field(cf.pk, [self.object_type.pk]))
        self.assertEqual(
            Site.objects.filter(custom_field_data__batched_field='foo').count(),
            site_count
        )

        # Renaming: the key is renamed on every existing object, preserving its value. This is
        # always applied inline, so no job is involved.
        cf.refresh_from_db()
        cf.name = 'renamed_field'
        cf.save()
        self.assertEqual(
            Site.objects.filter(custom_field_data__renamed_field='foo').count(),
            site_count
        )
        self.assertEqual(
            Site.objects.filter(custom_field_data__has_key='batched_field').count(),
            0
        )

        # Removal: deleting the field strips the key from every existing object
        cf.delete()
        self.assertTrue(purge_custom_field(cf.pk))
        self.assertEqual(
            Site.objects.filter(custom_field_data__has_key='renamed_field').count(),
            0
        )

    def test_provisioning_writes_nothing_without_a_default(self):
        """
        A field with no default has no value to record, so creating one must not touch any object.
        """
        cf = CustomField.objects.create(
            name='unset_field',
            type=CustomFieldTypeChoices.TYPE_TEXT
        )

        with CaptureQueriesContext(connection) as queries:
            cf.object_types.set([self.object_type])

        # No object data is written at all -- the cost of adding a field no longer scales with the
        # number of objects it applies to
        self.assertFalse([
            q['sql'] for q in queries.captured_queries
            if q['sql'].lstrip().upper().startswith('UPDATE "DCIM_SITE"'.upper())
        ])

        self.assertEqual(Site.objects.filter(custom_field_data__has_key='unset_field').count(), 0)
        for site in Site.objects.all():
            self.assertEqual(site.custom_field_data, {})
            self.assertIsNone(site.cf['unset_field'])

    def test_provisioning_applies_a_default_immediately(self):
        """
        A default value, by contrast, must be recorded on every existing object as soon as the
        field is created -- it has to be filterable straight away, so it cannot be deferred.
        """
        cf = CustomField.objects.create(
            name='defaulted_field',
            type=CustomFieldTypeChoices.TYPE_TEXT,
            default='bar'
        )
        cf.object_types.set([self.object_type])

        self.assertEqual(
            Site.objects.filter(custom_field_data__defaulted_field='bar').count(),
            Site.objects.count()
        )

    def test_rename_touches_only_objects_holding_a_value(self):
        """
        Renaming rewrites the key only where a value is actually stored. This is what keeps a
        rename cheap now that objects are no longer provisioned with a placeholder each.
        """
        cf = CustomField.objects.create(
            name='sparse_field',
            type=CustomFieldTypeChoices.TYPE_TEXT
        )
        cf.object_types.set([self.object_type])

        site = Site.objects.first()
        site.custom_field_data['sparse_field'] = 'value'
        site.save()

        cf.name = 'sparse_renamed'
        cf.save()

        self.assertEqual(
            list(
                Site.objects.filter(custom_field_data__has_key='sparse_renamed')
                .values_list('pk', flat=True)
            ),
            [site.pk]
        )
        self.assertEqual(Site.objects.filter(custom_field_data__has_key='sparse_field').count(), 0)
        site.refresh_from_db()
        self.assertEqual(site.custom_field_data['sparse_renamed'], 'value')

    def test_removal_from_object_type_purges_data(self):
        """
        Unassigning a field from an object type removes its data from those objects.
        """
        cf = CustomField.objects.create(
            name='unassigned_field',
            type=CustomFieldTypeChoices.TYPE_TEXT,
            default='baz'
        )
        cf.object_types.set([self.object_type])
        self.assertEqual(
            Site.objects.filter(custom_field_data__has_key='unassigned_field').count(),
            Site.objects.count()
        )

        cf.object_types.remove(self.object_type)

        self.assertEqual(
            Site.objects.filter(custom_field_data__has_key='unassigned_field').count(),
            0
        )

    def test_clearing_object_types_purges_data(self):
        """
        clear() unassigns every object type at once and reports no pk_set, so it must be handled
        before the fact. Its data is removed just as remove()'s is.
        """
        cf = CustomField.objects.create(
            name='cleared_field',
            type=CustomFieldTypeChoices.TYPE_TEXT,
            default='baz'
        )
        cf.object_types.set([self.object_type])
        self.assertEqual(
            Site.objects.filter(custom_field_data__has_key='cleared_field').count(),
            Site.objects.count()
        )

        cf.object_types.clear()

        self.assertEqual(
            Site.objects.filter(custom_field_data__has_key='cleared_field').count(),
            0
        )

    def test_batch_update_excludes_rows_which_no_longer_match(self):
        """
        A caller's filters must constrain the UPDATE as well as the selection of each batch.
        rename_object_data() builds a jsonb_set() expression which evaluates to NULL for a row not
        holding the key being renamed, so a row which loses it between the two statements would
        otherwise have its entire custom_field_data column nulled out.
        """
        cf = CustomField.objects.create(
            name='drifting_field',
            type=CustomFieldTypeChoices.TYPE_TEXT
        )
        cf.object_types.set([self.object_type])

        sites = list(Site.objects.order_by('pk'))
        holder, bystander = sites[0], sites[-1]
        Site.objects.filter(pk=holder.pk).update(custom_field_data={'drifting_field': 'value'})
        Site.objects.filter(pk=bystander.pk).update(custom_field_data={'other': 'untouched'})

        # Simulate a concurrent write: the batch selection yields a pk which no longer satisfies
        # the has_key filter by the time the UPDATE is issued.
        select_pks = QuerySet.values_list
        injected = []

        def inject_stale_pk(self, *args, **kwargs):
            result = select_pks(self, *args, **kwargs)
            if self.model is Site and args == ('pk',) and kwargs.get('flat') and not injected:
                injected.append(bystander.pk)
                return [*result, bystander.pk]
            return result

        with patch.object(QuerySet, 'values_list', inject_stale_pk):
            cf.name = 'drifted_field'
            cf.save()

        self.assertEqual(injected, [bystander.pk], "the stale pk was never injected")

        # The renamed value landed, and the bystander was left entirely alone
        holder.refresh_from_db()
        self.assertEqual(holder.custom_field_data, {'drifted_field': 'value'})
        bystander.refresh_from_db()
        self.assertEqual(bystander.custom_field_data, {'other': 'untouched'})

    @staticmethod
    def order_sites_by(*aliases):
        """
        Order a SiteTable by the given column aliases and return the underlying QuerySet.
        """
        table = SiteTable(Site.objects.all())
        table.order_by = aliases
        return table.data.data

    def test_table_ordering_breaks_ties_by_primary_key(self):
        """
        Rows tying on the sort value -- every object holding no value ties on both sort keys --
        must still be totally ordered, or paginated results may skip or repeat rows between
        page requests.
        """
        cf = CustomField.objects.create(
            name='sort_field',
            type=CustomFieldTypeChoices.TYPE_INTEGER
        )
        cf.object_types.set([self.object_type])

        # None of these hold a value for the field, so all of them tie
        Site.objects.bulk_create([
            Site(name=f'Tied Site {i}', slug=f'tied-site-{i}') for i in range(1, 11)
        ])

        for alias in ('cf_sort_field', '-cf_sort_field'):
            ordered = self.order_sites_by(alias)
            self.assertEqual(
                ordered.query.order_by[-1],
                'pk',
                "the primary key must be applied as the final sort key"
            )

            # Paging through the results must yield each object exactly once
            expected = [site.pk for site in ordered]
            paginated = []
            for offset in range(0, len(expected), 4):
                paginated.extend(site.pk for site in ordered[offset:offset + 4])
            self.assertEqual(paginated, expected)

    def test_table_ordering_tolerates_a_repeated_sort_alias(self):
        """
        The sort parameter is read with getlist(), so the same custom field column can appear in
        the ordering more than once, applying the same annotation to the queryset twice.
        """
        cf = CustomField.objects.create(
            name='sort_field',
            type=CustomFieldTypeChoices.TYPE_INTEGER
        )
        cf.object_types.set([self.object_type])

        table = SiteTable(Site.objects.all())
        table.order_by = ['cf_sort_field', '-cf_sort_field']

        self.assertEqual(len(list(table.rows)), Site.objects.count())

    def test_default_value_validation(self):
        choiceset = CustomFieldChoiceSet.objects.create(
            name="Test Choice Set",
            extra_choices=(
                ('choice1', 'Choice 1'),
                ('choice2', 'Choice 2'),
            )
        )
        site = Site.objects.create(name='Site 1', slug='site-1')
        object_type = ObjectType.objects.get_for_model(Site)

        # Text
        CustomField(name='test', type='text', required=True, default="Default text").full_clean()

        # Integer
        CustomField(name='test', type='integer', required=True, default=1).full_clean()
        with self.assertRaises(ValidationError):
            CustomField(name='test', type='integer', required=True, default='xxx').full_clean()

        # Boolean
        CustomField(name='test', type='boolean', required=True, default=True).full_clean()
        with self.assertRaises(ValidationError):
            CustomField(name='test', type='boolean', required=True, default='xxx').full_clean()

        # Date
        CustomField(name='test', type='date', required=True, default="2023-02-25").full_clean()
        with self.assertRaises(ValidationError):
            CustomField(name='test', type='date', required=True, default='xxx').full_clean()

        # Datetime
        CustomField(name='test', type='datetime', required=True, default="2023-02-25 02:02:02").full_clean()
        with self.assertRaises(ValidationError):
            CustomField(name='test', type='datetime', required=True, default='xxx').full_clean()

        # URL
        CustomField(name='test', type='url', required=True, default="https://www.netbox.dev").full_clean()

        # JSON
        CustomField(name='test', type='json', required=True, default='{"test": "object"}').full_clean()

        # Selection
        CustomField(name='test', type='select', required=True, choice_set=choiceset, default='choice1').full_clean()
        with self.assertRaises(ValidationError):
            CustomField(name='test', type='select', required=True, choice_set=choiceset, default='xxx').full_clean()

        # Multi-select
        CustomField(
            name='test',
            type='multiselect',
            required=True,
            choice_set=choiceset,
            default=['choice1']  # Single default choice
        ).full_clean()
        CustomField(
            name='test',
            type='multiselect',
            required=True,
            choice_set=choiceset,
            default=['choice1', 'choice2']  # Multiple default choices
        ).full_clean()
        with self.assertRaises(ValidationError):
            CustomField(
                name='test',
                type='multiselect',
                required=True,
                choice_set=choiceset,
                default=['xxx']
            ).full_clean()

        # Object
        CustomField(
            name='test',
            type='object',
            required=True,
            related_object_type=object_type,
            default=site.pk
        ).full_clean()
        with (self.assertRaises(ValidationError)):
            CustomField(
                name='test',
                type='object',
                required=True,
                related_object_type=object_type,
                default="xxx"
            ).full_clean()

        # Multi-object
        CustomField(
            name='test',
            type='multiobject',
            required=True,
            related_object_type=object_type,
            default=[site.pk]
        ).full_clean()
        with self.assertRaises(ValidationError):
            CustomField(
                name='test',
                type='multiobject',
                required=True,
                related_object_type=object_type,
                default=["xxx"]
            ).full_clean()

    def test_validation_schema_only_for_json_type(self):
        schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
            },
        }

        # Valid: schema on a JSON field
        CustomField(name='test', type=CustomFieldTypeChoices.TYPE_JSON, validation_schema=schema).full_clean()

        # Invalid: schema on a non-JSON field
        with self.assertRaises(ValidationError):
            CustomField(name='test', type=CustomFieldTypeChoices.TYPE_TEXT, validation_schema=schema).full_clean()
        with self.assertRaises(ValidationError):
            CustomField(name='test', type=CustomFieldTypeChoices.TYPE_INTEGER, validation_schema=schema).full_clean()

    def test_json_schema_default_validation(self):
        schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
            },
            'required': ['name'],
        }

        # Valid default
        CustomField(
            name='test', type=CustomFieldTypeChoices.TYPE_JSON,
            validation_schema=schema, default={'name': 'test'}
        ).full_clean()

        # Invalid default (missing required 'name')
        with self.assertRaises(ValidationError):
            CustomField(
                name='test', type=CustomFieldTypeChoices.TYPE_JSON,
                validation_schema=schema, default={'age': 25}
            ).full_clean()


class CustomFieldManagerTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        object_type = ObjectType.objects.get_for_model(Site)
        custom_field = CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='text_field', default='foo')
        custom_field.save()
        custom_field.object_types.set([object_type])

    def test_get_for_model(self):
        self.assertEqual(len(CustomField.objects.get_for_model(Site)), 1)
        self.assertEqual(len(CustomField.objects.get_for_model(VirtualMachine)), 0)

    def test_get_for_model_caches_models_with_no_custom_fields(self):
        """
        A model with no custom fields assigned must be served from the request cache like any other.
        An empty list is falsy, so testing the cached value for truthiness would treat it as a miss
        and re-query on every call.
        """
        token = query_cache.set(defaultdict(dict))
        self.addCleanup(query_cache.reset, token)

        # Site has one custom field assigned, VirtualMachine none
        for model in (Site, VirtualMachine):
            CustomField.objects.get_for_model(model)  # Prime the cache
            with self.assertNumQueries(0):
                CustomField.objects.get_for_model(model)

    def test_get_defaults_for_model_is_cached(self):
        """
        Every save of a custom-field-bearing object resolves the model's defaults, so the lookup
        must be served from the request cache rather than re-queried each time. As above, a model
        with no defaults caches an empty dict, which must not be mistaken for a miss.
        """
        token = query_cache.set(defaultdict(dict))
        self.addCleanup(query_cache.reset, token)

        # Site has a field with a default, VirtualMachine none
        for model in (Site, VirtualMachine):
            CustomField.objects.get_defaults_for_model(model)
            with self.assertNumQueries(0):
                CustomField.objects.get_defaults_for_model(model)

    def test_get_defaults_for_model_shares_the_field_cache(self):
        """
        The two lookups differ only in the statuses they select, so resolving a model's defaults must
        be served from the fields get_for_model() has already fetched rather than re-querying them.
        """
        token = query_cache.set(defaultdict(dict))
        self.addCleanup(query_cache.reset, token)

        CustomField.objects.get_for_model(Site)  # Prime the field cache

        with self.assertNumQueries(0):
            self.assertEqual(CustomField.objects.get_defaults_for_model(Site), {'text_field': 'foo'})

    def test_get_defaults_for_model_returns_a_copy(self):
        """
        Callers assign the returned dict directly to an object's custom field data and then mutate
        it in place, so each must receive its own copy. Sharing the cached dict -- or the list held
        by a multiple-value field's default -- would let one object's value alter another's.
        """
        custom_field = CustomField(type=CustomFieldTypeChoices.TYPE_JSON, name='json_field', default=['foo'])
        custom_field.save()
        custom_field.object_types.set([ObjectType.objects.get_for_model(Site)])

        token = query_cache.set(defaultdict(dict))
        self.addCleanup(query_cache.reset, token)

        defaults = CustomField.objects.get_defaults_for_model(Site)
        defaults['text_field'] = 'bar'
        defaults['json_field'].append('bar')

        self.assertEqual(
            CustomField.objects.get_defaults_for_model(Site),
            {'text_field': 'foo', 'json_field': ['foo']}
        )

    def test_creating_a_field_clears_the_cache(self):
        """
        The cache spans a whole request -- and a whole script or job run -- so a field created
        partway through one must not be hidden by what was read before it. get_defaults_for_model()
        is the lookup which matters most here: Device and Module component instantiation resolves
        the defaults of every component model it creates.
        """
        token = query_cache.set(defaultdict(dict))
        self.addCleanup(query_cache.reset, token)

        CustomField.objects.get_for_model(VirtualMachine)  # Prime the cache while none is assigned

        cf = CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='vm_field', default='bar')
        cf.save()
        cf.object_types.set([ObjectType.objects.get_for_model(VirtualMachine)])

        self.assertEqual([f.pk for f in CustomField.objects.get_for_model(VirtualMachine)], [cf.pk])
        self.assertEqual(CustomField.objects.get_defaults_for_model(VirtualMachine), {'vm_field': 'bar'})

    def test_assigning_an_object_type_clears_the_cache(self):
        token = query_cache.set(defaultdict(dict))
        self.addCleanup(query_cache.reset, token)

        CustomField.objects.get_for_model(VirtualMachine)  # Prime the cache while none is assigned

        cf = CustomField.objects.get(name='text_field')
        cf.object_types.add(ObjectType.objects.get_for_model(VirtualMachine))

        self.assertEqual([f.pk for f in CustomField.objects.get_for_model(VirtualMachine)], [cf.pk])

    def test_unassigning_an_object_type_clears_the_cache(self):
        token = query_cache.set(defaultdict(dict))
        self.addCleanup(query_cache.reset, token)

        CustomField.objects.get_for_model(Site)  # Prime the cache while the field is assigned

        cf = CustomField.objects.get(name='text_field')
        cf.object_types.remove(ObjectType.objects.get_for_model(Site))

        self.assertEqual(CustomField.objects.get_for_model(Site), [])
        self.assertEqual(CustomField.objects.get_defaults_for_model(Site), {})

    def test_changing_a_default_clears_the_cache(self):
        """
        A field's default reaches the objects created after it is changed, so a change made partway
        through a request must not be served from the value cached before it.
        """
        token = query_cache.set(defaultdict(dict))
        self.addCleanup(query_cache.reset, token)

        self.assertEqual(CustomField.objects.get_defaults_for_model(Site), {'text_field': 'foo'})

        cf = CustomField.objects.get(name='text_field')
        cf.default = 'bar'
        cf.save()

        self.assertEqual(CustomField.objects.get_defaults_for_model(Site), {'text_field': 'bar'})

    def test_repeated_saves_do_not_requery_custom_fields(self):
        """
        A bulk import creates thousands of objects within one request; resolving the defaults afresh
        for each would add a query per object (see CustomFieldsMixin.save()).
        """
        token = query_cache.set(defaultdict(dict))
        self.addCleanup(query_cache.reset, token)

        Site.objects.create(name='Site 1', slug='site-1')  # Prime the caches

        with CaptureQueriesContext(connection) as ctx:
            for i in range(2, 5):
                Site.objects.create(name=f'Site {i}', slug=f'site-{i}')

        custom_field_queries = [q for q in ctx.captured_queries if 'extras_customfield' in q['sql']]
        self.assertEqual(custom_field_queries, [])
        self.assertEqual(Site.objects.filter(custom_field_data__text_field='foo').count(), 4)


class CustomFieldAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        object_type = ObjectType.objects.get_for_model(Site)

        # Create some VLANs
        vlans = (
            VLAN(name='VLAN 1', vid=1),
            VLAN(name='VLAN 2', vid=2),
            VLAN(name='VLAN 3', vid=3),
            VLAN(name='VLAN 4', vid=4),
            VLAN(name='VLAN 5', vid=5),
        )
        VLAN.objects.bulk_create(vlans)

        # Create a set of custom field choices
        choice_set = CustomFieldChoiceSet.objects.create(
            name='Custom Field Choice Set 1',
            extra_choices=(('foo', 'Foo'), ('bar', 'Bar'), ('baz', 'Baz'))
        )

        custom_fields = (
            CustomField(
                type=CustomFieldTypeChoices.TYPE_TEXT,
                name='text_field',
                default='foo'
            ),
            CustomField(
                type=CustomFieldTypeChoices.TYPE_LONGTEXT,
                name='longtext_field',
                default='ABC'
            ),
            CustomField(
                type=CustomFieldTypeChoices.TYPE_INTEGER,
                name='integer_field',
                default=123
            ),
            CustomField(
                type=CustomFieldTypeChoices.TYPE_DECIMAL,
                name='decimal_field',
                default=123.45
            ),
            CustomField(
                type=CustomFieldTypeChoices.TYPE_BOOLEAN,
                name='boolean_field',
                default=False
            ),
            CustomField(
                type=CustomFieldTypeChoices.TYPE_DATE,
                name='date_field',
                default='2020-01-01'
            ),
            CustomField(
                type=CustomFieldTypeChoices.TYPE_DATETIME,
                name='datetime_field',
                default='2020-01-01T01:23:45'
            ),
            CustomField(
                type=CustomFieldTypeChoices.TYPE_URL,
                name='url_field',
                default='http://example.com/1'
            ),
            CustomField(
                type=CustomFieldTypeChoices.TYPE_JSON,
                name='json_field',
                default='{"x": "y"}'
            ),
            CustomField(
                type=CustomFieldTypeChoices.TYPE_SELECT,
                name='select_field',
                default='foo',
                choice_set=choice_set
            ),
            CustomField(
                type=CustomFieldTypeChoices.TYPE_MULTISELECT,
                name='multiselect_field',
                default=['foo'],
                choice_set=choice_set,
            ),
            CustomField(
                type=CustomFieldTypeChoices.TYPE_OBJECT,
                name='object_field',
                related_object_type=ObjectType.objects.get_for_model(VLAN),
                default=vlans[0].pk,
            ),
            CustomField(
                type=CustomFieldTypeChoices.TYPE_MULTIOBJECT,
                name='multiobject_field',
                related_object_type=ObjectType.objects.get_for_model(VLAN),
                default=[vlans[0].pk, vlans[1].pk],
            ),
        )
        for cf in custom_fields:
            cf.save()
            cf.object_types.set([object_type])

        # Create some sites *after* creating the custom fields. This ensures that
        # default values are not set for the assigned objects.
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        # Assign custom field values for site 2
        sites[1].custom_field_data = {
            custom_fields[0].name: 'bar',
            custom_fields[1].name: 'DEF',
            custom_fields[2].name: 456,
            custom_fields[3].name: Decimal('456.78'),
            custom_fields[4].name: True,
            custom_fields[5].name: '2020-01-02',
            custom_fields[6].name: '2020-01-02 12:00:00',
            custom_fields[7].name: 'http://example.com/2',
            custom_fields[8].name: '{"foo": 1, "bar": 2}',
            custom_fields[9].name: 'bar',
            custom_fields[10].name: ['bar', 'baz'],
            custom_fields[11].name: vlans[1].pk,
            custom_fields[12].name: [vlans[2].pk, vlans[3].pk],
        }
        sites[1].save()

    # Labels for the choice set created in setUpTestData, used to build the expected
    # API representation of selection custom fields ({'value': ..., 'label': ...}).
    CHOICE_LABELS = {'foo': 'Foo', 'bar': 'Bar', 'baz': 'Baz'}

    @classmethod
    def _select(cls, value):
        """Return the expected API representation of a single selection choice."""
        if value is None:
            return None
        return {'value': value, 'label': cls.CHOICE_LABELS[value]}

    @classmethod
    def _multiselect(cls, values):
        """Return the expected API representation of a multiple selection value."""
        if values is None:
            return None
        return [cls._select(v) for v in values]

    def test_get_custom_fields(self):
        TYPES = {
            CustomFieldTypeChoices.TYPE_TEXT: 'string',
            CustomFieldTypeChoices.TYPE_LONGTEXT: 'string',
            CustomFieldTypeChoices.TYPE_INTEGER: 'integer',
            CustomFieldTypeChoices.TYPE_DECIMAL: 'decimal',
            CustomFieldTypeChoices.TYPE_BOOLEAN: 'boolean',
            CustomFieldTypeChoices.TYPE_DATE: 'string',
            CustomFieldTypeChoices.TYPE_DATETIME: 'string',
            CustomFieldTypeChoices.TYPE_URL: 'string',
            CustomFieldTypeChoices.TYPE_JSON: 'object',
            CustomFieldTypeChoices.TYPE_SELECT: 'string',
            CustomFieldTypeChoices.TYPE_MULTISELECT: 'array',
            CustomFieldTypeChoices.TYPE_OBJECT: 'object',
            CustomFieldTypeChoices.TYPE_MULTIOBJECT: 'array',
        }

        self.add_permissions('extras.view_customfield')
        url = reverse('extras-api:customfield-list')
        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['count'], len(TYPES))

        # Validate data types
        for customfield in response.data['results']:
            cf_type = customfield['type']['value']
            self.assertEqual(customfield['data_type'], TYPES[cf_type])

    def test_get_single_object_without_custom_field_data(self):
        """
        Validate that custom fields are present on an object even if it has no values defined.
        """
        site1 = Site.objects.get(name='Site 1')
        url = reverse('dcim-api:site-detail', kwargs={'pk': site1.pk})
        self.add_permissions('dcim.view_site')

        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['name'], site1.name)
        self.assertEqual(response.data['custom_fields'], {
            'text_field': None,
            'longtext_field': None,
            'integer_field': None,
            'decimal_field': None,
            'boolean_field': None,
            'date_field': None,
            'datetime_field': None,
            'url_field': None,
            'json_field': None,
            'select_field': None,
            'multiselect_field': None,
            'object_field': None,
            'multiobject_field': None,
        })

    def test_get_single_object_with_custom_field_data(self):
        """
        Validate that custom fields are present and correctly set for an object with values defined.
        """
        site2 = Site.objects.get(name='Site 2')
        site2_cfvs = site2.cf
        url = reverse('dcim-api:site-detail', kwargs={'pk': site2.pk})
        self.add_permissions('dcim.view_site')

        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['name'], site2.name)
        self.assertEqual(response.data['custom_fields']['text_field'], site2_cfvs['text_field'])
        self.assertEqual(response.data['custom_fields']['longtext_field'], site2_cfvs['longtext_field'])
        self.assertEqual(response.data['custom_fields']['integer_field'], site2_cfvs['integer_field'])
        self.assertEqual(response.data['custom_fields']['decimal_field'], site2_cfvs['decimal_field'])
        self.assertEqual(response.data['custom_fields']['boolean_field'], site2_cfvs['boolean_field'])
        self.assertEqual(response.data['custom_fields']['date_field'], site2_cfvs['date_field'])
        self.assertEqual(response.data['custom_fields']['datetime_field'], site2_cfvs['datetime_field'])
        self.assertEqual(response.data['custom_fields']['url_field'], site2_cfvs['url_field'])
        self.assertEqual(response.data['custom_fields']['json_field'], site2_cfvs['json_field'])
        self.assertEqual(response.data['custom_fields']['select_field'], self._select(site2_cfvs['select_field']))
        self.assertEqual(
            response.data['custom_fields']['multiselect_field'],
            self._multiselect(site2_cfvs['multiselect_field'])
        )
        self.assertEqual(response.data['custom_fields']['object_field']['id'], site2_cfvs['object_field'].pk)
        self.assertEqual(
            [obj['id'] for obj in response.data['custom_fields']['multiobject_field']],
            [obj.pk for obj in site2_cfvs['multiobject_field']]
        )

    def test_get_object_selection_field_representation(self):
        """
        Selection custom fields are rendered as an object exposing both the stored value and its
        human-friendly label on read access (see #20897).
        """
        site2 = Site.objects.get(name='Site 2')
        url = reverse('dcim-api:site-detail', kwargs={'pk': site2.pk})
        self.add_permissions('dcim.view_site')

        response = self.client.get(url, **self.header)

        # A single selection value is rendered as a {value, label} object
        self.assertEqual(response.data['custom_fields']['select_field'], {
            'value': 'bar',
            'label': 'Bar',
        })

        # A multiple selection value is rendered as a list of {value, label} objects
        self.assertEqual(response.data['custom_fields']['multiselect_field'], [
            {'value': 'bar', 'label': 'Bar'},
            {'value': 'baz', 'label': 'Baz'},
        ])

    def test_get_object_selection_field_unresolved_label(self):
        """
        A stored selection value with no matching choice falls back to using the raw value as its label.
        """
        site2 = Site.objects.get(name='Site 2')
        site2.custom_field_data['select_field'] = 'stale'
        site2.save()
        url = reverse('dcim-api:site-detail', kwargs={'pk': site2.pk})
        self.add_permissions('dcim.view_site')

        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['custom_fields']['select_field'], {
            'value': 'stale',
            'label': 'stale',
        })

    def test_graphql_selection_field_representation_matches_rest(self):
        site2 = Site.objects.get(name='Site 2')
        self.add_permissions('dcim.view_site')

        query = f'{{ site(id: {site2.pk}) {{ custom_fields }} }}'
        response = self.client.post(reverse('graphql'), data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        custom_fields = data['data']['site']['custom_fields']

        self.assertEqual(custom_fields['select_field'], self._select('bar'))
        self.assertEqual(custom_fields['multiselect_field'], self._multiselect(['bar', 'baz']))

    def test_graphql_selection_field_unresolved_label(self):
        site2 = Site.objects.get(name='Site 2')
        site2.custom_field_data['select_field'] = 'stale'
        site2.save()
        self.add_permissions('dcim.view_site')

        query = f'{{ site(id: {site2.pk}) {{ custom_fields }} }}'
        response = self.client.post(reverse('graphql'), data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(data['data']['site']['custom_fields']['select_field'], {
            'value': 'stale',
            'label': 'stale',
        })

    def test_graphql_non_selection_fields_pass_through_unchanged(self):
        site2 = Site.objects.get(name='Site 2')
        self.add_permissions('dcim.view_site')

        query = f'{{ site(id: {site2.pk}) {{ custom_fields }} }}'
        response = self.client.post(reverse('graphql'), data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        custom_fields = data['data']['site']['custom_fields']

        self.assertEqual(custom_fields['text_field'], 'bar')
        self.assertEqual(custom_fields['integer_field'], 456)
        self.assertEqual(custom_fields['boolean_field'], True)

    def test_graphql_selection_field_list_query_is_not_n_plus_one(self):
        self.add_permissions('dcim.view_site')
        Site.objects.bulk_create([Site(name=f'Site {i}', slug=f'site-{i}') for i in range(3, 13)])

        query = '{ site_list { custom_fields } }'
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.post(reverse('graphql'), data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['site_list']), 12)

        # The capture window also holds one-off request queries, so assert on per-table counts, not the total.
        site_queries = get_primary_table_queries(ctx.captured_queries, Site)
        self.assertEqual(
            len(site_queries), 1,
            f'custom_field_data must be fetched by the site list query itself, got {site_queries}'
        )
        custom_field_queries = get_primary_table_queries(ctx.captured_queries, CustomField)
        self.assertEqual(
            len(custom_field_queries), 1,
            f'custom field definitions must be fetched once per request, got {custom_field_queries}'
        )

    def test_get_for_model_select_related_choice_set(self):
        query_cache.set(None)
        custom_fields = list(CustomField.objects.get_for_model(Site))
        with self.assertNumQueries(0):
            resolved = {cf.name: cf.resolve_selection_value(cf.default) for cf in custom_fields}
        self.assertEqual(resolved['select_field'], self._select('foo'))
        self.assertEqual(resolved['multiselect_field'], self._multiselect(['foo']))

    @tag('regression')
    def test_update_selection_field_rejects_read_format(self):
        """
        Selection fields are written by passing the raw value; submitting the {value, label} read
        representation must be rejected with a clean 400, not a 500 (see #20897).
        """
        site2 = Site.objects.get(name='Site 2')
        url = reverse('dcim-api:site-detail', kwargs={'pk': site2.pk})
        self.add_permissions('dcim.change_site')

        # A single selection submitted as an object is rejected
        response = self.client.patch(
            url, {'custom_fields': {'select_field': {'value': 'foo', 'label': 'Foo'}}}, format='json', **self.header
        )
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        # A multiple selection submitted as a list of objects is rejected (must not raise a TypeError/500)
        response = self.client.patch(
            url,
            {'custom_fields': {'multiselect_field': [{'value': 'foo', 'label': 'Foo'}]}},
            format='json',
            **self.header
        )
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        # The stored values are unchanged
        site2.refresh_from_db()
        self.assertEqual(site2.custom_field_data['select_field'], 'bar')
        self.assertEqual(site2.custom_field_data['multiselect_field'], ['bar', 'baz'])

    def test_create_single_object_with_defaults(self):
        """
        Create a new site with no specified custom field values and check that it received the default values.
        """
        cf_defaults = {
            cf.name: cf.default for cf in CustomField.objects.all()
        }
        data = {
            'name': 'Site 3',
            'slug': 'site-3',
        }
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.add_site')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        # Validate response data
        response_cf = response.data['custom_fields']
        self.assertEqual(response_cf['text_field'], cf_defaults['text_field'])
        self.assertEqual(response_cf['longtext_field'], cf_defaults['longtext_field'])
        self.assertEqual(response_cf['integer_field'], cf_defaults['integer_field'])
        self.assertEqual(response_cf['decimal_field'], cf_defaults['decimal_field'])
        self.assertEqual(response_cf['boolean_field'], cf_defaults['boolean_field'])
        self.assertEqual(response_cf['date_field'].isoformat(), cf_defaults['date_field'])
        self.assertEqual(response_cf['datetime_field'].isoformat(), cf_defaults['datetime_field'])
        self.assertEqual(response_cf['url_field'], cf_defaults['url_field'])
        self.assertEqual(response_cf['json_field'], cf_defaults['json_field'])
        self.assertEqual(response_cf['select_field'], self._select(cf_defaults['select_field']))
        self.assertEqual(response_cf['multiselect_field'], self._multiselect(cf_defaults['multiselect_field']))
        self.assertEqual(response_cf['object_field']['id'], cf_defaults['object_field'])
        self.assertEqual(
            [obj['id'] for obj in response.data['custom_fields']['multiobject_field']],
            cf_defaults['multiobject_field']
        )

        # Validate database data
        site = Site.objects.get(pk=response.data['id'])
        self.assertEqual(site.custom_field_data['text_field'], cf_defaults['text_field'])
        self.assertEqual(site.custom_field_data['longtext_field'], cf_defaults['longtext_field'])
        self.assertEqual(site.custom_field_data['integer_field'], cf_defaults['integer_field'])
        self.assertEqual(site.custom_field_data['decimal_field'], cf_defaults['decimal_field'])
        self.assertEqual(site.custom_field_data['boolean_field'], cf_defaults['boolean_field'])
        self.assertEqual(site.custom_field_data['date_field'], cf_defaults['date_field'])
        self.assertEqual(site.custom_field_data['datetime_field'], cf_defaults['datetime_field'])
        self.assertEqual(site.custom_field_data['url_field'], cf_defaults['url_field'])
        self.assertEqual(site.custom_field_data['json_field'], cf_defaults['json_field'])
        self.assertEqual(site.custom_field_data['select_field'], cf_defaults['select_field'])
        self.assertEqual(site.custom_field_data['multiselect_field'], cf_defaults['multiselect_field'])
        self.assertEqual(site.custom_field_data['object_field'], cf_defaults['object_field'])
        self.assertEqual(site.custom_field_data['multiobject_field'], cf_defaults['multiobject_field'])

    def test_create_single_object_with_values(self):
        """
        Create a single new site with a value for each type of custom field.
        """
        data = {
            'name': 'Site 3',
            'slug': 'site-3',
            'custom_fields': {
                'text_field': 'bar',
                'longtext_field': 'blah blah blah',
                'integer_field': 456,
                'decimal_field': 456.78,
                'boolean_field': True,
                'date_field': datetime.date(2020, 1, 2),
                'datetime_field': datetime.datetime(2020, 1, 2, 12, 0, 0),
                'url_field': 'http://example.com/2',
                'json_field': '{"foo": 1, "bar": 2}',
                'select_field': 'bar',
                'multiselect_field': ['bar', 'baz'],
                'object_field': VLAN.objects.get(vid=2).pk,
                'multiobject_field': list(VLAN.objects.filter(vid__in=[3, 4]).values_list('pk', flat=True)),
            },
        }
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.add_site')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        # Validate response data
        response_cf = response.data['custom_fields']
        data_cf = data['custom_fields']
        self.assertEqual(response_cf['text_field'], data_cf['text_field'])
        self.assertEqual(response_cf['longtext_field'], data_cf['longtext_field'])
        self.assertEqual(response_cf['integer_field'], data_cf['integer_field'])
        self.assertEqual(response_cf['decimal_field'], data_cf['decimal_field'])
        self.assertEqual(response_cf['boolean_field'], data_cf['boolean_field'])
        self.assertEqual(response_cf['date_field'], data_cf['date_field'])
        self.assertEqual(response_cf['datetime_field'], data_cf['datetime_field'])
        self.assertEqual(response_cf['url_field'], data_cf['url_field'])
        self.assertEqual(response_cf['json_field'], data_cf['json_field'])
        self.assertEqual(response_cf['select_field'], self._select(data_cf['select_field']))
        self.assertEqual(response_cf['multiselect_field'], self._multiselect(data_cf['multiselect_field']))
        self.assertEqual(response_cf['object_field']['id'], data_cf['object_field'])
        self.assertEqual(
            [obj['id'] for obj in response_cf['multiobject_field']],
            data_cf['multiobject_field']
        )

        # Validate database data
        site = Site.objects.get(pk=response.data['id'])
        self.assertEqual(site.custom_field_data['text_field'], data_cf['text_field'])
        self.assertEqual(site.custom_field_data['longtext_field'], data_cf['longtext_field'])
        self.assertEqual(site.custom_field_data['integer_field'], data_cf['integer_field'])
        self.assertEqual(site.custom_field_data['decimal_field'], data_cf['decimal_field'])
        self.assertEqual(site.custom_field_data['boolean_field'], data_cf['boolean_field'])
        self.assertEqual(site.cf['date_field'], data_cf['date_field'])
        self.assertEqual(site.cf['datetime_field'], data_cf['datetime_field'])
        self.assertEqual(site.custom_field_data['url_field'], data_cf['url_field'])
        self.assertEqual(site.custom_field_data['json_field'], data_cf['json_field'])
        self.assertEqual(site.custom_field_data['select_field'], data_cf['select_field'])
        self.assertEqual(site.custom_field_data['multiselect_field'], data_cf['multiselect_field'])
        self.assertEqual(site.custom_field_data['object_field'], data_cf['object_field'])
        self.assertEqual(site.custom_field_data['multiobject_field'], data_cf['multiobject_field'])

    def test_create_multiple_objects_with_defaults(self):
        """
        Create three new sites with no specified custom field values and check that each received
        the default custom field values.
        """
        cf_defaults = {
            cf.name: cf.default for cf in CustomField.objects.all()
        }
        data = (
            {
                'name': 'Site 3',
                'slug': 'site-3',
            },
            {
                'name': 'Site 4',
                'slug': 'site-4',
            },
            {
                'name': 'Site 5',
                'slug': 'site-5',
            },
        )
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.add_site')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), len(data))

        for i, obj in enumerate(data):

            # Validate response data
            response_cf = response.data[i]['custom_fields']
            self.assertEqual(response_cf['text_field'], cf_defaults['text_field'])
            self.assertEqual(response_cf['longtext_field'], cf_defaults['longtext_field'])
            self.assertEqual(response_cf['integer_field'], cf_defaults['integer_field'])
            self.assertEqual(response_cf['decimal_field'], cf_defaults['decimal_field'])
            self.assertEqual(response_cf['boolean_field'], cf_defaults['boolean_field'])
            self.assertEqual(response_cf['date_field'].isoformat(), cf_defaults['date_field'])
            self.assertEqual(response_cf['datetime_field'].isoformat(), cf_defaults['datetime_field'])
            self.assertEqual(response_cf['url_field'], cf_defaults['url_field'])
            self.assertEqual(response_cf['json_field'], cf_defaults['json_field'])
            self.assertEqual(response_cf['select_field'], self._select(cf_defaults['select_field']))
            self.assertEqual(response_cf['multiselect_field'], self._multiselect(cf_defaults['multiselect_field']))
            self.assertEqual(response_cf['object_field']['id'], cf_defaults['object_field'])
            self.assertEqual(
                [obj['id'] for obj in response_cf['multiobject_field']],
                cf_defaults['multiobject_field']
            )

            # Validate database data
            site = Site.objects.get(pk=response.data[i]['id'])
            self.assertEqual(site.custom_field_data['text_field'], cf_defaults['text_field'])
            self.assertEqual(site.custom_field_data['longtext_field'], cf_defaults['longtext_field'])
            self.assertEqual(site.custom_field_data['integer_field'], cf_defaults['integer_field'])
            self.assertEqual(site.custom_field_data['decimal_field'], cf_defaults['decimal_field'])
            self.assertEqual(site.custom_field_data['boolean_field'], cf_defaults['boolean_field'])
            self.assertEqual(site.custom_field_data['date_field'], cf_defaults['date_field'])
            self.assertEqual(site.custom_field_data['datetime_field'], cf_defaults['datetime_field'])
            self.assertEqual(site.custom_field_data['url_field'], cf_defaults['url_field'])
            self.assertEqual(site.custom_field_data['json_field'], cf_defaults['json_field'])
            self.assertEqual(site.custom_field_data['select_field'], cf_defaults['select_field'])
            self.assertEqual(site.custom_field_data['multiselect_field'], cf_defaults['multiselect_field'])
            self.assertEqual(site.custom_field_data['object_field'], cf_defaults['object_field'])
            self.assertEqual(site.custom_field_data['multiobject_field'], cf_defaults['multiobject_field'])

    def test_create_multiple_objects_with_values(self):
        """
        Create a three new sites, each with custom fields defined.
        """
        custom_field_data = {
            'text_field': 'bar',
            'longtext_field': 'abcdefghij',
            'integer_field': 456,
            'decimal_field': 456.78,
            'boolean_field': True,
            'date_field': datetime.date(2020, 1, 2),
            'datetime_field': datetime.datetime(2020, 1, 2, 12, 0, 0),
            'url_field': 'http://example.com/2',
            'json_field': '{"foo": 1, "bar": 2}',
            'select_field': 'bar',
            'multiselect_field': ['bar', 'baz'],
            'object_field': VLAN.objects.get(vid=2).pk,
            'multiobject_field': list(VLAN.objects.filter(vid__in=[3, 4]).values_list('pk', flat=True)),
        }
        data = (
            {
                'name': 'Site 3',
                'slug': 'site-3',
                'custom_fields': custom_field_data,
            },
            {
                'name': 'Site 4',
                'slug': 'site-4',
                'custom_fields': custom_field_data,
            },
            {
                'name': 'Site 5',
                'slug': 'site-5',
                'custom_fields': custom_field_data,
            },
        )
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.add_site')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), len(data))

        for i, obj in enumerate(data):

            # Validate response data
            response_cf = response.data[i]['custom_fields']
            self.assertEqual(response_cf['text_field'], custom_field_data['text_field'])
            self.assertEqual(response_cf['longtext_field'], custom_field_data['longtext_field'])
            self.assertEqual(response_cf['integer_field'], custom_field_data['integer_field'])
            self.assertEqual(response_cf['decimal_field'], custom_field_data['decimal_field'])
            self.assertEqual(response_cf['boolean_field'], custom_field_data['boolean_field'])
            self.assertEqual(response_cf['date_field'], custom_field_data['date_field'])
            self.assertEqual(response_cf['datetime_field'], custom_field_data['datetime_field'])
            self.assertEqual(response_cf['url_field'], custom_field_data['url_field'])
            self.assertEqual(response_cf['json_field'], custom_field_data['json_field'])
            self.assertEqual(response_cf['select_field'], self._select(custom_field_data['select_field']))
            self.assertEqual(
                response_cf['multiselect_field'],
                self._multiselect(custom_field_data['multiselect_field'])
            )
            self.assertEqual(response_cf['object_field']['id'], custom_field_data['object_field'])
            self.assertEqual(
                [obj['id'] for obj in response_cf['multiobject_field']],
                custom_field_data['multiobject_field']
            )

            # Validate database data
            site = Site.objects.get(pk=response.data[i]['id'])
            self.assertEqual(site.custom_field_data['text_field'], custom_field_data['text_field'])
            self.assertEqual(site.custom_field_data['longtext_field'], custom_field_data['longtext_field'])
            self.assertEqual(site.custom_field_data['integer_field'], custom_field_data['integer_field'])
            self.assertEqual(site.custom_field_data['decimal_field'], custom_field_data['decimal_field'])
            self.assertEqual(site.custom_field_data['boolean_field'], custom_field_data['boolean_field'])
            self.assertEqual(site.cf['date_field'], custom_field_data['date_field'])
            self.assertEqual(site.cf['datetime_field'], custom_field_data['datetime_field'])
            self.assertEqual(site.custom_field_data['url_field'], custom_field_data['url_field'])
            self.assertEqual(site.custom_field_data['json_field'], custom_field_data['json_field'])
            self.assertEqual(site.custom_field_data['select_field'], custom_field_data['select_field'])
            self.assertEqual(site.custom_field_data['multiselect_field'], custom_field_data['multiselect_field'])
            self.assertEqual(site.custom_field_data['object_field'], custom_field_data['object_field'])
            self.assertEqual(site.custom_field_data['multiobject_field'], custom_field_data['multiobject_field'])

    def test_update_single_object_with_values(self):
        """
        Update an object with existing custom field values. Ensure that only the updated custom field values are
        modified.
        """
        site2 = Site.objects.get(name='Site 2')
        original_cfvs = {**site2.cf}
        data = {
            'custom_fields': {
                'text_field': 'ABCD',
                'integer_field': 1234,
            },
        }
        url = reverse('dcim-api:site-detail', kwargs={'pk': site2.pk})
        self.add_permissions('dcim.change_site')

        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        # Validate response data
        response_cf = response.data['custom_fields']
        self.assertEqual(response_cf['text_field'], data['custom_fields']['text_field'])
        self.assertEqual(response_cf['longtext_field'], original_cfvs['longtext_field'])
        self.assertEqual(response_cf['integer_field'], data['custom_fields']['integer_field'])
        self.assertEqual(response_cf['decimal_field'], original_cfvs['decimal_field'])
        self.assertEqual(response_cf['boolean_field'], original_cfvs['boolean_field'])
        self.assertEqual(response_cf['date_field'], original_cfvs['date_field'])
        self.assertEqual(response_cf['datetime_field'], original_cfvs['datetime_field'])
        self.assertEqual(response_cf['url_field'], original_cfvs['url_field'])
        self.assertEqual(response_cf['json_field'], original_cfvs['json_field'])
        self.assertEqual(response_cf['select_field'], self._select(original_cfvs['select_field']))
        self.assertEqual(response_cf['multiselect_field'], self._multiselect(original_cfvs['multiselect_field']))
        self.assertEqual(response_cf['object_field']['id'], original_cfvs['object_field'].pk)
        self.assertListEqual(
            [obj['id'] for obj in response_cf['multiobject_field']],
            [obj.pk for obj in original_cfvs['multiobject_field']]
        )

        # Validate database data
        site2 = Site.objects.get(pk=site2.pk)
        self.assertEqual(site2.cf['text_field'], data['custom_fields']['text_field'])
        self.assertEqual(site2.cf['longtext_field'], original_cfvs['longtext_field'])
        self.assertEqual(site2.cf['integer_field'], data['custom_fields']['integer_field'])
        self.assertEqual(site2.cf['decimal_field'], original_cfvs['decimal_field'])
        self.assertEqual(site2.cf['boolean_field'], original_cfvs['boolean_field'])
        self.assertEqual(site2.cf['date_field'], original_cfvs['date_field'])
        self.assertEqual(site2.cf['datetime_field'], original_cfvs['datetime_field'])
        self.assertEqual(site2.cf['url_field'], original_cfvs['url_field'])
        self.assertEqual(site2.cf['json_field'], original_cfvs['json_field'])
        self.assertEqual(site2.cf['select_field'], original_cfvs['select_field'])
        self.assertEqual(site2.cf['multiselect_field'], original_cfvs['multiselect_field'])
        self.assertEqual(site2.cf['object_field'], original_cfvs['object_field'])
        self.assertListEqual(
            list(site2.cf['multiobject_field']),
            list(original_cfvs['multiobject_field'])
        )

    @tag('regression')
    def test_update_single_object_rejects_unknown_custom_fields(self):
        site2 = Site.objects.get(name='Site 2')
        original_cf_data = {**site2.custom_field_data}
        url = reverse('dcim-api:site-detail', kwargs={'pk': site2.pk})
        self.add_permissions('dcim.change_site')

        data = {
            'custom_fields': {
                'text_field': 'valid',
                'thisfieldshouldntexist': 'random text here',
            },
        }

        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('custom_fields', response.data)
        self.assertIn('thisfieldshouldntexist', response.data['custom_fields'])

        # Ensure the object was not modified
        site2.refresh_from_db()
        self.assertEqual(site2.custom_field_data, original_cf_data)

    @tag('regression')
    def test_update_single_object_prunes_stale_custom_field_data_from_database_and_postchange_data(self):
        stale_key = 'thisfieldshouldntexist'
        stale_value = 'random text here'
        updated_text_value = 'ABCD'

        site2 = Site.objects.get(name='Site 2')
        original_text_value = site2.custom_field_data['text_field']
        object_type = ObjectType.objects.get_for_model(Site)

        # Seed stale custom field data directly in the database to mimic a polluted row.
        Site.objects.filter(pk=site2.pk).update(
            custom_field_data={
                **site2.custom_field_data,
                stale_key: stale_value,
            }
        )
        site2.refresh_from_db()
        self.assertIn(stale_key, site2.custom_field_data)

        existing_change_ids = set(
            ObjectChange.objects.filter(
                changed_object_type=object_type,
                changed_object_id=site2.pk,
            ).values_list('pk', flat=True)
        )

        url = reverse('dcim-api:site-detail', kwargs={'pk': site2.pk})
        self.add_permissions('dcim.change_site')
        data = {
            'custom_fields': {
                'text_field': updated_text_value,
            },
        }

        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        site2.refresh_from_db()
        self.assertEqual(site2.cf['text_field'], updated_text_value)
        self.assertNotIn(stale_key, site2.custom_field_data)

        object_changes = ObjectChange.objects.filter(
            changed_object_type=object_type,
            changed_object_id=site2.pk,
        ).exclude(pk__in=existing_change_ids)
        self.assertEqual(object_changes.count(), 1)

        object_change = object_changes.get()
        self.assertEqual(object_change.prechange_data['custom_fields']['text_field'], original_text_value)
        self.assertEqual(object_change.postchange_data['custom_fields']['text_field'], updated_text_value)
        self.assertNotIn(stale_key, object_change.postchange_data['custom_fields'])

    def test_specify_related_object_by_attr(self):
        site1 = Site.objects.get(name='Site 1')
        vlans = VLAN.objects.all()[:3]
        url = reverse('dcim-api:site-detail', kwargs={'pk': site1.pk})
        self.add_permissions('dcim.change_site', 'ipam.view_vlan')

        # Set related objects by PK
        data = {
            'custom_fields': {
                'object_field': vlans[0].pk,
                'multiobject_field': [vlans[1].pk, vlans[2].pk],
            },
        }
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(
            response.data['custom_fields']['object_field']['id'],
            vlans[0].pk
        )
        self.assertListEqual(
            [obj['id'] for obj in response.data['custom_fields']['multiobject_field']],
            [vlans[1].pk, vlans[2].pk]
        )

        # Set related objects by name
        data = {
            'custom_fields': {
                'object_field': {
                    'name': vlans[0].name,
                },
                'multiobject_field': [
                    {
                        'name': vlans[1].name
                    },
                    {
                        'name': vlans[2].name
                    },
                ],
            },
        }
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(
            response.data['custom_fields']['object_field']['id'],
            vlans[0].pk
        )
        self.assertListEqual(
            [obj['id'] for obj in response.data['custom_fields']['multiobject_field']],
            [vlans[1].pk, vlans[2].pk]
        )

        # Clear related objects
        data = {
            'custom_fields': {
                'object_field': None,
                'multiobject_field': [],
            },
        }
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertIsNone(response.data['custom_fields']['object_field'])
        self.assertListEqual(response.data['custom_fields']['multiobject_field'], [])

    def test_minimum_maximum_values_validation(self):
        site2 = Site.objects.get(name='Site 2')
        url = reverse('dcim-api:site-detail', kwargs={'pk': site2.pk})
        self.add_permissions('dcim.change_site')

        cf_integer = CustomField.objects.get(name='integer_field')
        cf_integer.validation_minimum = 10
        cf_integer.validation_maximum = 20
        cf_integer.save()

        data = {'custom_fields': {'integer_field': 9}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        data = {'custom_fields': {'integer_field': 21}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        data = {'custom_fields': {'integer_field': 15}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

    def test_regex_validation(self):
        site2 = Site.objects.get(name='Site 2')
        url = reverse('dcim-api:site-detail', kwargs={'pk': site2.pk})
        self.add_permissions('dcim.change_site')

        cf_text = CustomField.objects.get(name='text_field')
        cf_text.validation_regex = r'^[A-Z]{3}$'  # Three uppercase letters
        cf_text.save()

        data = {'custom_fields': {'text_field': 'ABC123'}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        data = {'custom_fields': {'text_field': 'abc'}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        data = {'custom_fields': {'text_field': 'ABC'}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

    def test_url_regex_validation(self):
        """
        Test that validation_regex is applied to URL custom fields (fixes #20498).
        """
        site2 = Site.objects.get(name='Site 2')
        url = reverse('dcim-api:site-detail', kwargs={'pk': site2.pk})
        self.add_permissions('dcim.change_site')

        cf_url = CustomField.objects.get(name='url_field')
        cf_url.validation_regex = r'^https://'  # Require HTTPS
        cf_url.save()

        # Test invalid URL (http instead of https)
        data = {'custom_fields': {'url_field': 'http://example.com'}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        # Test valid URL (https)
        data = {'custom_fields': {'url_field': 'https://example.com'}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

    def test_url_scheme_validation(self):
        """
        Test that URL custom field values must use a scheme permitted by ALLOWED_URL_SCHEMES (fixes
        #22640), and that a schemeless value is normalized to an absolute URL (assume_scheme='https'),
        consistent with the UI.
        """
        site2 = Site.objects.get(name='Site 2')
        url = reverse('dcim-api:site-detail', kwargs={'pk': site2.pk})
        self.add_permissions('dcim.change_site')

        # A dangerous scheme (e.g. javascript:) must be rejected
        data = {'custom_fields': {'url_field': 'javascript:alert(1)'}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        # A well-formed URL using a scheme outside ALLOWED_URL_SCHEMES must be rejected
        data = {'custom_fields': {'url_field': 'gopher://example.com'}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        # An allowed scheme must be accepted
        data = {'custom_fields': {'url_field': 'https://example.com'}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        # A schemeless value must be accepted and normalized to https, matching the UI
        data = {'custom_fields': {'url_field': 'example.com'}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        site2.refresh_from_db()
        self.assertEqual(site2.custom_field_data['url_field'], 'https://example.com')

    def test_json_schema_validation(self):
        site2 = Site.objects.get(name='Site 2')
        url = reverse('dcim-api:site-detail', kwargs={'pk': site2.pk})
        self.add_permissions('dcim.change_site')

        cf_json = CustomField.objects.get(name='json_field')
        cf_json.validation_schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'},
            },
            'required': ['name'],
        }
        cf_json.save()

        # Invalid: missing required 'name' property
        data = {'custom_fields': {'json_field': {'age': 25}}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        # Invalid: 'age' is not an integer
        data = {'custom_fields': {'json_field': {'name': 'test', 'age': 'not_an_int'}}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        # Valid: conforms to schema
        data = {'custom_fields': {'json_field': {'name': 'test', 'age': 25}}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        # Valid: null value (schema not enforced on empty)
        data = {'custom_fields': {'json_field': None}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

    def test_uniqueness_validation(self):
        # Create a unique custom field
        cf_text = CustomField.objects.get(name='text_field')
        cf_text.unique = True
        cf_text.save()

        # Set a value on site 1
        site1 = Site.objects.get(name='Site 1')
        site1.custom_field_data['text_field'] = 'ABC123'
        site1.save()

        site2 = Site.objects.get(name='Site 2')
        url = reverse('dcim-api:site-detail', kwargs={'pk': site2.pk})
        self.add_permissions('dcim.change_site')

        data = {'custom_fields': {'text_field': 'ABC123'}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        data = {'custom_fields': {'text_field': 'DEF456'}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)


class CustomFieldImportTestCase(TestCase):
    user_permissions = (
        'dcim.view_site',
        'dcim.add_site',
    )

    @classmethod
    def setUpTestData(cls):

        # Create a set of custom field choices
        choice_set = CustomFieldChoiceSet.objects.create(
            name='Custom Field Choice Set 1',
            extra_choices=(
                ('a', 'Option A'),
                ('b', 'Option B'),
                ('c', 'Option C'),
            )
        )

        custom_fields = (
            CustomField(name='text', type=CustomFieldTypeChoices.TYPE_TEXT),
            CustomField(name='longtext', type=CustomFieldTypeChoices.TYPE_LONGTEXT),
            CustomField(name='integer', type=CustomFieldTypeChoices.TYPE_INTEGER),
            CustomField(name='decimal', type=CustomFieldTypeChoices.TYPE_DECIMAL),
            CustomField(name='boolean', type=CustomFieldTypeChoices.TYPE_BOOLEAN),
            CustomField(name='date', type=CustomFieldTypeChoices.TYPE_DATE),
            CustomField(name='datetime', type=CustomFieldTypeChoices.TYPE_DATETIME),
            CustomField(name='url', type=CustomFieldTypeChoices.TYPE_URL),
            CustomField(name='json', type=CustomFieldTypeChoices.TYPE_JSON),
            CustomField(name='select', type=CustomFieldTypeChoices.TYPE_SELECT, choice_set=choice_set),
            CustomField(name='multiselect', type=CustomFieldTypeChoices.TYPE_MULTISELECT, choice_set=choice_set),
        )
        for cf in custom_fields:
            cf.save()
            cf.object_types.set([ObjectType.objects.get_for_model(Site)])

    def test_import(self):
        """
        Import a Site in CSV format, including a value for each CustomField.
        """
        data = (
            (
                'name', 'slug', 'status', 'cf_text', 'cf_longtext', 'cf_integer', 'cf_decimal', 'cf_boolean', 'cf_date',
                'cf_datetime', 'cf_url', 'cf_json', 'cf_select', 'cf_multiselect',
            ),
            (
                'Site 1', 'site-1', 'active', 'ABC', 'Foo', '123', '123.45', 'True', '2020-01-01',
                '2020-01-01 12:00:00', 'http://example.com/1', '{"foo": 123}', 'a', '"a,b"',
            ),
            (
                'Site 2', 'site-2', 'active', 'DEF', 'Bar', '456', '456.78', 'False', '2020-01-02',
                '2020-01-02 12:00:00', 'http://example.com/2', '{"bar": 456}', 'b', '"b,c"',
            ),
            ('Site 3', 'site-3', 'active', '', '', '', '', '', '', '', '', '', '', ''),
        )
        csv_data = '\n'.join(','.join(row) for row in data)

        response = self.client.post(reverse('dcim:site_bulk_import'), {
            'data': csv_data,
            'format': ImportFormatChoices.CSV,
            'csv_delimiter': CSVDelimiterChoices.AUTO,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Site.objects.count(), 3)

        # Validate data for site 1
        site1 = Site.objects.get(name='Site 1')
        self.assertEqual(len(site1.custom_field_data), 11)
        self.assertEqual(site1.custom_field_data['text'], 'ABC')
        self.assertEqual(site1.custom_field_data['longtext'], 'Foo')
        self.assertEqual(site1.custom_field_data['integer'], 123)
        self.assertEqual(site1.custom_field_data['decimal'], 123.45)
        self.assertEqual(site1.custom_field_data['boolean'], True)
        self.assertEqual(site1.cf['date'].isoformat(), '2020-01-01')
        self.assertEqual(site1.cf['datetime'].isoformat(), '2020-01-01T12:00:00+00:00')
        self.assertEqual(site1.custom_field_data['url'], 'http://example.com/1')
        self.assertEqual(site1.custom_field_data['json'], {"foo": 123})
        self.assertEqual(site1.custom_field_data['select'], 'a')
        self.assertEqual(site1.custom_field_data['multiselect'], ['a', 'b'])

        # Validate data for site 2
        site2 = Site.objects.get(name='Site 2')
        self.assertEqual(len(site2.custom_field_data), 11)
        self.assertEqual(site2.custom_field_data['text'], 'DEF')
        self.assertEqual(site2.custom_field_data['longtext'], 'Bar')
        self.assertEqual(site2.custom_field_data['integer'], 456)
        self.assertEqual(site2.custom_field_data['decimal'], 456.78)
        self.assertEqual(site2.custom_field_data['boolean'], False)
        self.assertEqual(site2.cf['date'].isoformat(), '2020-01-02')
        self.assertEqual(site2.cf['datetime'].isoformat(), '2020-01-02T12:00:00+00:00')
        self.assertEqual(site2.custom_field_data['url'], 'http://example.com/2')
        self.assertEqual(site2.custom_field_data['json'], {"bar": 456})
        self.assertEqual(site2.custom_field_data['select'], 'b')
        self.assertEqual(site2.custom_field_data['multiselect'], ['b', 'c'])

        # No custom field data should be set for site 3
        site3 = Site.objects.get(name='Site 3')
        self.assertFalse(any(site3.custom_field_data.values()))

    def test_import_missing_required(self):
        """
        Attempt to import an object missing a required custom field.
        """
        # Set one of our CustomFields to required
        CustomField.objects.filter(name='text').update(required=True)

        form_data = {
            'name': 'Site 1',
            'slug': 'site-1',
        }

        form = SiteImportForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cf_text', form.errors)

    def test_import_invalid_choice(self):
        """
        Attempt to import an object with an invalid choice selection.
        """
        form_data = {
            'name': 'Site 1',
            'slug': 'site-1',
            'cf_select': 'Choice X'
        }

        form = SiteImportForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cf_select', form.errors)


class CustomFieldModelTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cf1 = CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='foo')
        cf1.save()
        cf1.object_types.set([ObjectType.objects.get_for_model(Site)])

        cf2 = CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='bar')
        cf2.save()
        cf2.object_types.set([ObjectType.objects.get_for_model(Rack)])

    def test_cf_data(self):
        """
        Check that custom field data is present on the instance immediately after being set and after being fetched
        from the database.
        """
        site = Site(name='Test Site', slug='test-site')

        # Check custom field data on new instance
        site.custom_field_data['foo'] = 'abc'
        self.assertEqual(site.cf['foo'], 'abc')

        # Check custom field data from database
        site.save()
        site = Site.objects.get(name='Test Site')
        self.assertEqual(site.cf['foo'], 'abc')

    def test_invalid_data(self):
        """
        Any invalid or stale custom field data should be removed from the instance.
        """
        site = Site(name='Test Site', slug='test-site')

        # Set custom field data
        site.custom_field_data['foo'] = 'abc'
        site.custom_field_data['bar'] = 'def'
        site.clean()

        self.assertIn('foo', site.custom_field_data)
        self.assertNotIn('bar', site.custom_field_data)

    def test_missing_required_field(self):
        """
        Check that a ValidationError is raised if any required custom fields are not present.
        """
        cf3 = CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='baz', required=True)
        cf3.save()
        cf3.object_types.set([ObjectType.objects.get_for_model(Site)])

        site = Site(name='Test Site', slug='test-site')

        # Set custom field data with a required field omitted
        site.custom_field_data['foo'] = 'abc'
        with self.assertRaises(ValidationError):
            site.clean()

        site.custom_field_data['baz'] = 'def'
        site.clean()

    def test_required_field_enforced_on_existing_objects(self):
        """
        Adding a required custom field invalidates the objects which already exist, whether they
        carry no key for it -- the normal state now that empty values are not provisioned -- or an
        explicit null. Both are rejected, as they were before: every object then held a materialized
        null, which CustomField.validate() rejects for a required field.
        """
        site = Site.objects.create(name='Test Site', slug='test-site')

        cf = CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='req', required=True)
        cf.save()
        cf.object_types.set([ObjectType.objects.get_for_model(Site)])

        # No value was provisioned onto the existing object
        site.refresh_from_db()
        self.assertNotIn('req', site.custom_field_data)
        with self.assertRaises(ValidationError):
            site.clean()

        # An explicit null is rejected identically
        site.custom_field_data['req'] = None
        with self.assertRaises(ValidationError):
            site.clean()

        site.custom_field_data['req'] = 'value'
        site.clean()


class MissingKeyAwareFilterTestCase(TestCase):
    """
    MissingKeyAwareFilterMixin reimplements MultipleChoiceFilter.filter() for the negated case, so
    it may only be mixed into a class which inherits that method unmodified and which does not
    filter conjoined. Both constraints are enforced, as violating either would yield a wrong result
    set rather than an error.
    """
    def test_factory_rejects_a_class_which_defines_filter(self):
        # MultiValueMACAddressFilter overrides filter() to swallow ValidationError
        with self.assertRaises(TypeError):
            missing_key_aware_filter_factory(MultiValueMACAddressFilter)

        # BooleanFilter does not inherit MultipleChoiceFilter.filter() at all
        with self.assertRaises(TypeError):
            missing_key_aware_filter_factory(django_filters.BooleanFilter)

    def test_factory_accepts_a_class_which_inherits_filter(self):
        filter_class = missing_key_aware_filter_factory(MultiValueCharFilter)

        self.assertTrue(issubclass(filter_class, MissingKeyAwareFilterMixin))
        self.assertTrue(issubclass(filter_class, MultiValueCharFilter))
        # The factory is cached, so a class yields a single stable subclass
        self.assertIs(filter_class, missing_key_aware_filter_factory(MultiValueCharFilter))

    def test_conjoined_filtering_is_rejected(self):
        filter_class = missing_key_aware_filter_factory(MultiValueCharFilter)

        filter_class(field_name='custom_field_data__foo')
        filter_class(field_name='custom_field_data__foo', conjoined=False)
        with self.assertRaises(TypeError):
            filter_class(field_name='custom_field_data__foo', conjoined=True)

    def test_every_supported_custom_field_type_satisfies_the_constraints(self):
        """
        The filter classes CustomField.to_filter() selects must all remain admissible.
        """
        for cf_type in CustomFieldTypeChoices.values():
            with self.subTest(cf_type):
                cf = CustomField(name='test', type=cf_type)
                # Raises TypeError if the selected filter class violates a constraint
                cf.to_filter()
                cf.to_filter(lookup_expr='empty')


class CustomFieldModelFilterTestCase(TestCase):
    queryset = Site.objects.all()
    filterset = SiteFilterSet

    @classmethod
    def setUpTestData(cls):
        object_type = ObjectType.objects.get_for_model(Site)

        manufacturers = Manufacturer.objects.bulk_create((
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
            Manufacturer(name='Manufacturer 3', slug='manufacturer-3'),
            Manufacturer(name='Manufacturer 4', slug='manufacturer-4'),
        ))

        choice_set = CustomFieldChoiceSet.objects.create(
            name='Custom Field Choice Set 1',
            extra_choices=(('a', 'A'), ('b', 'B'), ('c', 'C'))
        )

        # Integer filtering
        cf = CustomField(name='cf1', type=CustomFieldTypeChoices.TYPE_INTEGER)
        cf.save()
        cf.object_types.set([object_type])

        # Decimal filtering
        cf = CustomField(name='cf2', type=CustomFieldTypeChoices.TYPE_DECIMAL)
        cf.save()
        cf.object_types.set([object_type])

        # Boolean filtering
        cf = CustomField(name='cf3', type=CustomFieldTypeChoices.TYPE_BOOLEAN)
        cf.save()
        cf.object_types.set([object_type])

        # Exact text filtering
        cf = CustomField(
            name='cf4',
            type=CustomFieldTypeChoices.TYPE_TEXT,
            filter_logic=CustomFieldFilterLogicChoices.FILTER_EXACT
        )
        cf.save()
        cf.object_types.set([object_type])

        # Loose text filtering
        cf = CustomField(
            name='cf5',
            type=CustomFieldTypeChoices.TYPE_TEXT,
            filter_logic=CustomFieldFilterLogicChoices.FILTER_LOOSE
        )
        cf.save()
        cf.object_types.set([object_type])

        # Date filtering
        cf = CustomField(name='cf6', type=CustomFieldTypeChoices.TYPE_DATE)
        cf.save()
        cf.object_types.set([object_type])

        # Exact URL filtering
        cf = CustomField(
            name='cf7',
            type=CustomFieldTypeChoices.TYPE_URL,
            filter_logic=CustomFieldFilterLogicChoices.FILTER_EXACT
        )
        cf.save()
        cf.object_types.set([object_type])

        # Loose URL filtering
        cf = CustomField(
            name='cf8',
            type=CustomFieldTypeChoices.TYPE_URL,
            filter_logic=CustomFieldFilterLogicChoices.FILTER_LOOSE
        )
        cf.save()
        cf.object_types.set([object_type])

        # Selection filtering
        cf = CustomField(
            name='cf9',
            type=CustomFieldTypeChoices.TYPE_SELECT,
            choice_set=choice_set
        )
        cf.save()
        cf.object_types.set([object_type])

        # Multiselect filtering
        cf = CustomField(
            name='cf10',
            type=CustomFieldTypeChoices.TYPE_MULTISELECT,
            choice_set=choice_set
        )
        cf.save()
        cf.object_types.set([object_type])

        # Object filtering
        cf = CustomField(
            name='cf11',
            type=CustomFieldTypeChoices.TYPE_OBJECT,
            related_object_type=ObjectType.objects.get_for_model(Manufacturer)
        )
        cf.save()
        cf.object_types.set([object_type])

        # Multi-object filtering
        cf = CustomField(
            name='cf12',
            type=CustomFieldTypeChoices.TYPE_MULTIOBJECT,
            related_object_type=ObjectType.objects.get_for_model(Manufacturer)
        )
        cf.save()
        cf.object_types.set([object_type])

        Site.objects.bulk_create([
            Site(name='Site 1', slug='site-1', custom_field_data={
                'cf1': 100,
                'cf2': 100.1,
                'cf3': True,
                'cf4': 'foo',
                'cf5': 'foo',
                'cf6': '2016-06-26',
                'cf7': 'http://a.example.com',
                'cf8': 'http://a.example.com',
                'cf9': 'A',
                'cf10': ['A', 'B'],
                'cf11': manufacturers[0].pk,
                'cf12': [manufacturers[0].pk, manufacturers[3].pk],
            }),
            Site(name='Site 2', slug='site-2', custom_field_data={
                'cf1': 200,
                'cf2': 200.2,
                'cf3': True,
                'cf4': 'foobar',
                'cf5': 'foobar',
                'cf6': '2016-06-27',
                'cf7': 'http://b.example.com',
                'cf8': 'http://b.example.com',
                'cf9': 'B',
                'cf10': ['B', 'C'],
                'cf11': manufacturers[1].pk,
                'cf12': [manufacturers[1].pk, manufacturers[3].pk],
            }),
            Site(name='Site 3', slug='site-3', custom_field_data={
                'cf1': 300,
                'cf2': 300.3,
                'cf3': False,
                'cf4': 'bar',
                'cf5': 'bar',
                'cf6': '2016-06-28',
                'cf7': 'http://c.example.com',
                'cf8': 'http://c.example.com',
                'cf9': 'C',
                'cf10': None,
                'cf11': manufacturers[2].pk,
                'cf12': [manufacturers[2].pk, manufacturers[3].pk],
            }),
            # Carries no custom field data at all. Negated lookups ("is not x") match it, as they
            # do an object holding an explicit null; see MissingKeyAwareFilterMixin.
            Site(name='Site 4', slug='site-4'),
        ])

    def test_filter_integer(self):
        self.assertEqual(self.filterset({'cf_cf1': [100, 200]}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf1__n': [200]}, self.queryset).qs.count(), 3)
        self.assertEqual(self.filterset({'cf_cf1__gt': [200]}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf1__gte': [200]}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf1__lt': [200]}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf1__lte': [200]}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf1__empty': True}, self.queryset).qs.count(), 1)

    def test_filter_decimal(self):
        self.assertEqual(self.filterset({'cf_cf2': [100.1, 200.2]}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf2__n': [200.2]}, self.queryset).qs.count(), 3)
        self.assertEqual(self.filterset({'cf_cf2__gt': [200.2]}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf2__gte': [200.2]}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf2__lt': [200.2]}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf2__lte': [200.2]}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf2__empty': True}, self.queryset).qs.count(), 1)

    def test_filter_boolean(self):
        self.assertEqual(self.filterset({'cf_cf3': True}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf3': False}, self.queryset).qs.count(), 1)

    def test_filter_text_strict(self):
        self.assertEqual(self.filterset({'cf_cf4': ['foo']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf4__n': ['foo']}, self.queryset).qs.count(), 3)
        self.assertEqual(self.filterset({'cf_cf4__ic': ['foo']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf4__nic': ['foo']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf4__isw': ['foo']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf4__nisw': ['foo']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf4__iew': ['bar']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf4__niew': ['bar']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf4__ie': ['FOO']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf4__nie': ['FOO']}, self.queryset).qs.count(), 3)
        self.assertEqual(self.filterset({'cf_cf4__empty': True}, self.queryset).qs.count(), 1)

    def test_filter_text_loose(self):
        self.assertEqual(self.filterset({'cf_cf5': ['foo']}, self.queryset).qs.count(), 2)

    def test_filter_date(self):
        self.assertEqual(self.filterset({'cf_cf6': ['2016-06-26', '2016-06-27']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf6__n': ['2016-06-27']}, self.queryset).qs.count(), 3)
        self.assertEqual(self.filterset({'cf_cf6__gt': ['2016-06-27']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf6__gte': ['2016-06-27']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf6__lt': ['2016-06-27']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf6__lte': ['2016-06-27']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf6__empty': True}, self.queryset).qs.count(), 1)

    def test_filter_url_strict(self):
        self.assertEqual(
            self.filterset({'cf_cf7': ['http://a.example.com', 'http://b.example.com']}, self.queryset).qs.count(),
            2
        )
        self.assertEqual(self.filterset({'cf_cf7__n': ['http://b.example.com']}, self.queryset).qs.count(), 3)
        self.assertEqual(self.filterset({'cf_cf7__ic': ['b']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf7__nic': ['b']}, self.queryset).qs.count(), 3)
        self.assertEqual(self.filterset({'cf_cf7__isw': ['http://']}, self.queryset).qs.count(), 3)
        self.assertEqual(self.filterset({'cf_cf7__nisw': ['http://']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf7__iew': ['.com']}, self.queryset).qs.count(), 3)
        self.assertEqual(self.filterset({'cf_cf7__niew': ['.com']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf7__ie': ['HTTP://A.EXAMPLE.COM']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf7__nie': ['HTTP://A.EXAMPLE.COM']}, self.queryset).qs.count(), 3)
        self.assertEqual(self.filterset({'cf_cf7__empty': True}, self.queryset).qs.count(), 1)

    def test_filter_url_loose(self):
        self.assertEqual(self.filterset({'cf_cf8': ['example.com']}, self.queryset).qs.count(), 3)

    def test_filter_negation_matches_unset_values(self):
        """
        A negated lookup must match an object which holds no value for the field, whether that is
        recorded as an explicit null or by the absence of the key; see MissingKeyAwareFilterMixin.
        """
        no_key = Site.objects.get(slug='site-4')
        explicit_null = Site.objects.create(name='Site 5', slug='site-5', custom_field_data={
            'cf1': None,
            'cf4': None,
            'cf6': None,
            'cf7': None,
        })

        for filter_name, value in (
            ('cf_cf1__n', 100),
            ('cf_cf4__n', 'foo'),
            ('cf_cf4__nic', 'foo'),
            ('cf_cf4__nisw', 'foo'),
            ('cf_cf4__niew', 'bar'),
            ('cf_cf4__nie', 'FOO'),
            ('cf_cf6__n', '2016-06-26'),
            ('cf_cf7__n', 'http://a.example.com'),
            ('cf_cf7__nic', 'a'),
            ('cf_cf7__nisw', 'http://'),
            ('cf_cf7__niew', '.com'),
        ):
            with self.subTest(filter_name):
                pks = set(
                    self.filterset({filter_name: [value]}, self.queryset).qs.values_list('pk', flat=True)
                )
                self.assertIn(no_key.pk, pks, "an object carrying no key must match")
                self.assertIn(explicit_null.pk, pks, "an object holding a null must match")

    def test_filter_null_sentinel_matches_unset_values(self):
        """
        The null sentinel (FILTERS_NULL_CHOICE_VALUE) asks for the objects holding no value, which
        must include those carrying no key as well as those holding an explicit null. Negating it
        must therefore return exactly the objects which do hold a value -- and in particular must
        not return the ones it is being asked to exclude.

        Only string-backed field types are exercised: a numeric or date field rejects 'null' during
        form validation ("Enter a whole number"), so the sentinel never reaches the filter at all.
        That is a property of multivalue_field_factory() and is unaffected by this behavior.
        """
        no_key = Site.objects.get(slug='site-4')
        explicit_null = Site.objects.create(name='Site 5', slug='site-5', custom_field_data={
            'cf4': None,
            'cf7': None,
            'cf9': None,
        })
        has_value = set(
            Site.objects.filter(slug__in=('site-1', 'site-2', 'site-3')).values_list('pk', flat=True)
        )

        for filter_name in ('cf_cf4', 'cf_cf7', 'cf_cf9'):
            with self.subTest(filter_name):
                pks = set(
                    self.filterset({filter_name: ['null']}, self.queryset).qs.values_list('pk', flat=True)
                )
                self.assertEqual(pks, {no_key.pk, explicit_null.pk})

                pks = set(
                    self.filterset({f'{filter_name}__n': ['null']}, self.queryset)
                    .qs.values_list('pk', flat=True)
                )
                self.assertEqual(pks, has_value)

    def test_filter_null_sentinel_combined_with_a_value(self):
        """
        The sentinel may be passed alongside real values, in which case it widens the match rather
        than replacing it. Under negation the valueless objects are then excluded, as they are among
        the values being negated.
        """
        no_key = Site.objects.get(slug='site-4')
        site_1 = Site.objects.get(slug='site-1')

        pks = set(
            self.filterset({'cf_cf4': ['foo', 'null']}, self.queryset).qs.values_list('pk', flat=True)
        )
        self.assertIn(site_1.pk, pks, "an object holding the value must match")
        self.assertIn(no_key.pk, pks, "an object holding no value must match")

        pks = set(
            self.filterset({'cf_cf4__n': ['foo', 'null']}, self.queryset).qs.values_list('pk', flat=True)
        )
        self.assertNotIn(site_1.pk, pks, "an object holding the value must be excluded")
        self.assertNotIn(no_key.pk, pks, "an object holding no value must be excluded")

    def test_filter_select(self):
        self.assertEqual(self.filterset({'cf_cf9': ['A', 'B']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf9__empty': True}, self.queryset).qs.count(), 1)

    def test_filter_multiselect(self):
        self.assertEqual(self.filterset({'cf_cf10': ['A']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf10': ['A', 'C']}, self.queryset).qs.count(), 2)
        # Matches both the object holding a literal null and the one carrying no key, as `empty` does
        self.assertEqual(self.filterset({'cf_cf10': ['null']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf10__empty': True}, self.queryset).qs.count(), 2)

    def test_filter_object(self):
        manufacturer_ids = Manufacturer.objects.values_list('id', flat=True)
        self.assertEqual(
            self.filterset({'cf_cf11': [manufacturer_ids[0], manufacturer_ids[1]]}, self.queryset).qs.count(),
            2
        )
        self.assertEqual(self.filterset({'cf_cf11__empty': True}, self.queryset).qs.count(), 1)

    def test_filter_multiobject(self):
        manufacturer_ids = Manufacturer.objects.values_list('id', flat=True)
        self.assertEqual(
            self.filterset({'cf_cf12': [manufacturer_ids[0], manufacturer_ids[1]]}, self.queryset).qs.count(),
            2
        )
        self.assertEqual(
            self.filterset({'cf_cf12': [manufacturer_ids[3]]}, self.queryset).qs.count(),
            3
        )
        self.assertEqual(self.filterset({'cf_cf12__empty': True}, self.queryset).qs.count(), 1)


@contextmanager
def hold_data_lock(custom_field):
    """
    Hold a custom field's data lock on a connection of its own, as a running background job does.

    A separate connection is what makes the lock observable: it is held for the duration of a job,
    which spans many transactions, so a test cannot take it on the connection it is testing.
    """
    lock_key = CustomField.data_lock_key(custom_field.pk)
    connection = connections.create_connection(DEFAULT_DB_ALIAS)
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT pg_try_advisory_lock(%s, %s)', lock_key)
            if not cursor.fetchone()[0]:
                raise RuntimeError(f"Failed to acquire the data lock for {custom_field}")
        yield
    finally:
        # Closing the session releases any advisory lock held on it
        connection.close()


@override_settings(BULK_UPDATE_CHUNK_SIZE=1)
class DeferredCustomFieldDataTestCase(TestCase):
    """
    Where too many objects are affected to update within the request, provisioning and purging
    custom field data is handed to a background job and the field is not live until it completes.

    BULK_UPDATE_CHUNK_SIZE (which doubles as the threshold for deferral) is overridden down so that
    the two objects below force the deferred path. It cannot be set to zero, which the setting
    rejects, and which would also empty every batch so that the jobs updated nothing.
    """
    @classmethod
    def setUpTestData(cls):
        Site.objects.bulk_create([
            Site(name='Site A', slug='site-a'),
            Site(name='Site B', slug='site-b'),
        ])
        cls.object_type = ObjectType.objects.get_for_model(Site)

    def create_field(self, name='field1', **kwargs):
        cf = CustomField.objects.create(name=name, type=CustomFieldTypeChoices.TYPE_TEXT, **kwargs)
        cf.object_types.set([self.object_type])
        cf.refresh_from_db()
        return cf

    #
    # Provisioning
    #

    def test_provisioning_is_deferred(self):
        cf = self.create_field(default='foo')

        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_PROVISIONING)
        # No object data has been written yet
        self.assertEqual(Site.objects.filter(custom_field_data__has_key='field1').count(), 0)

    def test_field_is_not_live_while_provisioning(self):
        cf = self.create_field(default='foo')
        site = Site.objects.first()

        self.assertNotIn(cf, CustomField.objects.get_for_model(Site))
        self.assertNotIn('field1', site.cf)
        self.assertNotIn('field1', {f.name for f in site.get_custom_fields()})

        # It is still reachable where a caller asks for that status, as get_defaults_for_model() does
        self.assertIn(cf, CustomField.objects.get_for_model(
            Site, statuses=(CustomFieldStatusChoices.STATUS_PROVISIONING,)
        ))

    def test_new_objects_receive_default_while_provisioning(self):
        """
        A field is provisioned precisely because it carries a default, so an object created while
        the backfill runs must still receive that default -- the job backfills only what predates
        the field.
        """
        self.create_field(default='foo')

        site = Site.objects.create(name='Site C', slug='site-c')

        site.refresh_from_db()
        self.assertEqual(site.custom_field_data['field1'], 'foo')

    def test_stored_data_survives_validation_while_provisioning(self):
        """
        A field which is not live is not validated, and neither is its stored data pruned as stale.
        Saving an object through full_clean() -- as the edit form, the REST API and bulk edit all do
        -- while the backfill runs must leave the stored value alone rather than reverting it to the
        field's default.
        """
        self.create_field(default='foo')
        site = Site.objects.first()
        # Written via the queryset so that the setup does not itself depend on save()
        Site.objects.filter(pk=site.pk).update(custom_field_data={'field1': 'bar'})
        site.refresh_from_db()

        site.full_clean()
        site.save()

        site.refresh_from_db()
        self.assertEqual(site.custom_field_data['field1'], 'bar')

    def test_required_field_is_not_enforced_while_provisioning(self):
        """
        The field is not live, so an object which the backfill has yet to reach must still validate.
        """
        self.create_field(default='foo', required=True)
        site = Site.objects.first()
        self.assertNotIn('field1', site.custom_field_data)

        site.full_clean()  # Must not raise

    def test_provisioning_job_backfills_and_activates(self):
        cf = self.create_field(default='foo')

        self.assertTrue(provision_custom_field(cf.pk, [self.object_type.pk]))

        cf.refresh_from_db()
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_ACTIVE)
        self.assertEqual(Site.objects.filter(custom_field_data__field1='foo').count(), 2)
        self.assertIn(cf, CustomField.objects.get_for_model(Site))

    def test_provisioning_job_commits_each_batch(self):
        """
        One transaction spanning the whole backfill would hold a row lock on every object it had
        rewritten until it finished, for as long as CUSTOMFIELD_JOB_TIMEOUT allows the job to run
        (see CustomField._update_object_data()).
        """
        cf = self.create_field(default='foo')

        with patch.object(CustomField, '_update_object_data') as update:
            provision_custom_field(cf.pk, [self.object_type.pk])

        update.assert_called()
        for call in update.call_args_list:
            self.assertTrue(call.kwargs['commit_per_batch'])

    def test_provisioning_job_does_not_activate_a_field_marked_for_deletion(self):
        """
        The field's status is rechecked as it is brought live, so that a deletion which landed while
        the backfill ran -- as one could were the job's lock lost with its connection -- is not
        undone by it.
        """
        cf = self.create_field(default='foo')

        def mark_deleting(*args, **kwargs):
            CustomField.objects.filter(pk=cf.pk).update(status=CustomFieldStatusChoices.STATUS_DELETING)

        with patch.object(CustomField, 'populate_initial_data', side_effect=mark_deleting):
            self.assertFalse(provision_custom_field(cf.pk, [self.object_type.pk]))

        cf.refresh_from_db()
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_DELETING)

    def test_provisioning_job_is_idempotent(self):
        cf = self.create_field(default='foo')
        provision_custom_field(cf.pk, [self.object_type.pk])

        # A second run finds the field no longer awaiting provisioning and does nothing
        self.assertFalse(provision_custom_field(cf.pk, [self.object_type.pk]))

    def test_provisioning_job_overrides_the_default_timeout(self):
        """
        The job is enqueued precisely because the work exceeds what a request can absorb, so it must
        not inherit RQ's default timeout, which is of the same order (see CUSTOMFIELD_JOB_TIMEOUT).
        """
        with patch.object(CustomFieldProvisioningJob, 'enqueue') as enqueue:
            with self.captureOnCommitCallbacks(execute=True):
                cf = self.create_field(default='foo')

        enqueue.assert_called_once()
        self.assertEqual(enqueue.call_args.kwargs['job_timeout'], CUSTOMFIELD_JOB_TIMEOUT)
        self.assertEqual(enqueue.call_args.kwargs['custom_field_pk'], cf.pk)

    def test_provisioning_job_is_enqueued(self):
        """
        The Job record itself must be valid: a custom field cannot be assigned to a Job as its
        object, so the field is identified by primary key instead (see CustomFieldDataJob).
        """
        with patch('core.models.jobs.django_rq') as django_rq:
            with self.captureOnCommitCallbacks(execute=True):
                cf = self.create_field(default='foo')

        job = Job.objects.get(name__startswith=CustomFieldProvisioningJob.name)
        self.assertIsNone(job.object_type)
        self.assertIn(str(cf), job.name)
        self.assertEqual(
            django_rq.get_queue.return_value.enqueue.call_args.kwargs['custom_field_pk'], cf.pk
        )

    def test_provisioning_job_forwards_its_object_types(self):
        """
        Only the caller which deferred the work knows which assignments are the new ones, so the
        types are carried by the job: run() has to pass them to the backfill rather than swallowing
        them, or the field would go live having provisioned nothing.
        """
        cf = self.create_field(default='foo')

        CustomFieldProvisioningJob(Job()).run(custom_field_pk=cf.pk, object_type_pks=[self.object_type.pk])

        cf.refresh_from_db()
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_ACTIVE)
        self.assertEqual(Site.objects.filter(custom_field_data__field1='foo').count(), 2)

    def test_provisioning_is_scoped_to_the_new_object_types(self):
        """
        Assigning a further object type provisions only that type. The job cannot work this out for
        itself once the assignment is made, so the types are carried to it.
        """
        cf = self.create_field()
        cf.default = 'foo'
        cf.save()
        rack_type = ObjectType.objects.get_for_model(Rack)
        site = Site.objects.first()
        Rack.objects.bulk_create([
            Rack(name='Rack 1', site=site),
            Rack(name='Rack 2', site=site),
        ])

        with patch.object(CustomFieldProvisioningJob, 'enqueue') as enqueue:
            with self.captureOnCommitCallbacks(execute=True):
                cf.object_types.add(rack_type)

        enqueue.assert_called_once()
        self.assertEqual(enqueue.call_args.kwargs['object_type_pks'], [rack_type.pk])

    def test_deferral_weighs_only_the_new_object_types(self):
        """
        A field already assigned to a large table stays inline when assigned a small one: the tables
        provisioned previously are not rewritten, so their size is beside the point.
        """
        cf = self.create_field()
        cf.default = 'foo'
        cf.save()

        # No racks exist, so there is nothing to defer even though the two sites exceed the limit
        cf.object_types.add(ObjectType.objects.get_for_model(Rack))

        cf.refresh_from_db()
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_ACTIVE)

    def test_provisioning_preserves_stored_values(self):
        """
        An object which already holds a value for the field is left as it is: the backfill supplies
        the default only where no value has been recorded.
        """
        cf = self.create_field(default='foo')
        Site.objects.update(custom_field_data={'field1': 'bar'})

        self.assertTrue(provision_custom_field(cf.pk, [self.object_type.pk]))

        cf.refresh_from_db()
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_ACTIVE)
        self.assertEqual(Site.objects.filter(custom_field_data__field1='bar').count(), 2)

    def test_field_without_default_is_not_deferred(self):
        """
        A field with no default has nothing to provision, so it goes live immediately regardless of
        how many objects it applies to.
        """
        cf = self.create_field()

        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_ACTIVE)

    def test_field_without_default_enqueues_nothing(self):
        """
        The decision rests with provision_data() rather than its caller, so a field with no default
        must not reach the point of sizing its object types, let alone of handing a job the no-op of
        writing a null to each of them.
        """
        cf = self.create_field()

        with (
            patch.object(CustomField, '_exceeds_inline_limit') as exceeds_limit,
            patch.object(CustomFieldProvisioningJob, 'enqueue') as enqueue,
        ):
            with self.captureOnCommitCallbacks(execute=True):
                cf.provision_data([self.object_type])

        exceeds_limit.assert_not_called()
        enqueue.assert_not_called()

    def test_assignment_is_refused_while_provisioning(self):
        """
        A second deferral would hand its job only the object types newly assigned, and whichever of
        the two jobs ran first would bring the field live -- leaving the other to find a field it no
        longer matched, and its own types unprovisioned. The assignment is refused instead, as every
        other change to a field which is not live is (see CustomField.clean()).
        """
        cf = self.create_field(default='foo')
        rack_type = ObjectType.objects.get_for_model(Rack)

        with patch.object(CustomFieldProvisioningJob, 'enqueue') as enqueue:
            with self.assertRaises(AbortRequest):
                # Contained in a savepoint: the assignment is rolled back by the refusal, which
                # would otherwise leave the test's own transaction needing one
                with transaction.atomic():
                    cf.object_types.add(rack_type)

        enqueue.assert_not_called()
        cf.refresh_from_db()
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_PROVISIONING)
        self.assertNotIn(rack_type.pk, cf.object_types.values_list('pk', flat=True))

    def test_assignment_is_refused_while_deleting(self):
        """
        The refusal precedes the check for a default: a field whose data is being purged must not
        take on further object types either, whether or not it has anything to provision on them.
        """
        cf = self.create_field()
        cf.delete()
        rack_type = ObjectType.objects.get_for_model(Rack)

        with self.assertRaises(AbortRequest):
            with transaction.atomic():
                cf.object_types.add(rack_type)

        cf.refresh_from_db()
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_DELETING)
        self.assertNotIn(rack_type.pk, cf.object_types.values_list('pk', flat=True))

    def test_assignment_is_refused_against_the_stored_status(self):
        """
        The status is read from the database rather than taken from the instance in hand, which a
        job may have taken offline (or brought live) since it was fetched.
        """
        cf = self.create_field()

        # Marked directly, leaving the instance in hand still reporting the field as live
        CustomField.objects.filter(pk=cf.pk).update(status=CustomFieldStatusChoices.STATUS_PROVISIONING)
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_ACTIVE)

        with self.assertRaises(AbortRequest):
            with transaction.atomic():
                cf.object_types.add(ObjectType.objects.get_for_model(Rack))

    def test_assignment_to_a_removed_field_is_refused(self):
        """
        The row may be gone by the time the status is read under its lock, the field having been
        deleted since the instance in hand was fetched. The assignment is reported as refused rather
        than failing on the absent status.
        """
        cf = self.create_field()
        rack_type = ObjectType.objects.get_for_model(Rack)

        # Removed directly, leaving the instance in hand still reporting the field as live
        CustomField.objects.filter(pk=cf.pk).delete()
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_ACTIVE)

        with self.assertRaises(AbortRequest):
            with transaction.atomic():
                cf.provision_data([rack_type])

    def test_unassignment_is_refused_while_provisioning(self):
        """
        A field being provisioned must not be unassigned from an object type either: the job carries
        the object types it was given, and would write its defaults into objects behind the removal.
        """
        cf = self.create_field(default='foo')
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_PROVISIONING)

        with self.assertRaises(AbortRequest):
            with transaction.atomic():
                cf.object_types.remove(self.object_type)

        self.assertIn(self.object_type.pk, cf.object_types.values_list('pk', flat=True))

    def test_unassignment_is_refused_while_deleting(self):
        cf = self.create_field()
        cf.delete()

        with self.assertRaises(AbortRequest):
            with transaction.atomic():
                cf.object_types.remove(self.object_type)

        self.assertIn(self.object_type.pk, cf.object_types.values_list('pk', flat=True))

    def test_clearing_object_types_is_refused_while_provisioning(self):
        """
        clear() is handled ahead of the removal rather than after it, as remove() is, so the refusal
        reaches the caller with the assignments still in place.
        """
        cf = self.create_field(default='foo')

        with self.assertRaises(AbortRequest):
            with transaction.atomic():
                cf.object_types.clear()

        self.assertIn(self.object_type.pk, cf.object_types.values_list('pk', flat=True))

    def test_unassignment_is_refused_against_the_stored_status(self):
        """
        The status is read from the database rather than taken from the instance in hand, which a
        job may have taken offline since it was fetched.
        """
        cf = self.create_field()

        # Marked directly, leaving the instance in hand still reporting the field as live
        CustomField.objects.filter(pk=cf.pk).update(status=CustomFieldStatusChoices.STATUS_PROVISIONING)
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_ACTIVE)

        with self.assertRaises(AbortRequest):
            with transaction.atomic():
                cf.object_types.remove(self.object_type)

    def test_unassignment_is_permitted_once_the_field_is_live(self):
        cf = self.create_field(default='foo')
        Site.objects.update(custom_field_data={'field1': 'foo'})
        self.assertTrue(provision_custom_field(cf.pk, [self.object_type.pk]))
        cf.refresh_from_db()

        cf.object_types.remove(self.object_type)  # Must not raise

        self.assertEqual(Site.objects.filter(custom_field_data__has_key='field1').count(), 0)

    def test_provisioning_job_skips_object_types_since_unassigned(self):
        """
        The job provisions only those of its object types which the field still carries. remove_data()
        refuses an unassignment while the field is being provisioned, so this covers a change made
        through the m2m table directly, which emits no signal for either to act on.
        """
        cf = self.create_field(default='foo')
        rack_type = ObjectType.objects.get_for_model(Rack)
        object_type_pks = [self.object_type.pk, rack_type.pk]

        # Unassigned without the signal handler's involvement
        CustomField.object_types.through.objects.filter(
            customfield=cf, contenttype=self.object_type
        ).delete()

        self.assertTrue(provision_custom_field(cf.pk, object_type_pks))

        self.assertEqual(Site.objects.filter(custom_field_data__has_key='field1').count(), 0)

    def test_assignment_is_permitted_once_the_field_is_live(self):
        """
        The refusal lasts only as long as the pending update: once the job has brought the field
        live, further object types are assigned as usual.
        """
        cf = self.create_field(default='foo')
        self.assertTrue(provision_custom_field(cf.pk, [self.object_type.pk]))
        rack_type = ObjectType.objects.get_for_model(Rack)
        cf.refresh_from_db()

        cf.object_types.add(rack_type)  # Must not raise

        self.assertIn(rack_type.pk, cf.object_types.values_list('pk', flat=True))

    #
    # Request cache
    #

    def test_taking_a_field_offline_clears_the_cached_fields(self):
        """
        The fields cached for a request span the whole of it -- and the whole of a script or job run
        -- so a field taken offline partway through one must not be served from what was cached
        before it.
        """
        token = query_cache.set(defaultdict(dict))
        self.addCleanup(query_cache.reset, token)

        CustomField.objects.get_for_model(Site)  # Prime the cache while no field is assigned

        cf = self.create_field(default='foo')
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_PROVISIONING)

        # Not live, but its default still reaches the objects created while it is provisioned
        self.assertEqual(CustomField.objects.get_for_model(Site), [])
        self.assertEqual(CustomField.objects.get_defaults_for_model(Site), {'field1': 'foo'})

    def test_marking_a_field_for_deletion_clears_the_cached_fields(self):
        cf = self.create_field()

        token = query_cache.set(defaultdict(dict))
        self.addCleanup(query_cache.reset, token)

        self.assertEqual([f.pk for f in CustomField.objects.get_for_model(Site)], [cf.pk])

        cf.delete()

        self.assertEqual(CustomField.objects.get_for_model(Site), [])

    def test_bringing_a_field_live_clears_the_cached_fields(self):
        cf = self.create_field(default='foo')

        token = query_cache.set(defaultdict(dict))
        self.addCleanup(query_cache.reset, token)

        self.assertEqual(CustomField.objects.get_for_model(Site), [])  # Not live while provisioning

        self.assertTrue(provision_custom_field(cf.pk, [self.object_type.pk]))

        self.assertEqual([f.pk for f in CustomField.objects.get_for_model(Site)], [cf.pk])

    #
    # Deletion
    #

    def test_deletion_is_deferred(self):
        cf = self.create_field()
        Site.objects.update(custom_field_data={'field1': 'foo'})

        cf.delete()

        cf = CustomField.objects.get(pk=cf.pk)
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_DELETING)
        # The stored data is left for the purge job
        self.assertEqual(Site.objects.filter(custom_field_data__has_key='field1').count(), 2)

    def test_deletion_is_deferred_even_without_stored_data(self):
        """
        The deferral decision weighs every row of the assigned types, not just those which hold a
        value, so a field holding no data on an over-limit table is still deferred. Deliberate: the
        probe cannot count the rows holding a key without a sequential scan (see
        _exceeds_inline_limit()), and the purge job it hands off to has nothing to do.
        """
        cf = self.create_field()
        self.assertEqual(Site.objects.filter(custom_field_data__has_key='field1').count(), 0)

        cf.delete()

        cf = CustomField.objects.get(pk=cf.pk)
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_DELETING)
        self.assertTrue(purge_custom_field(cf.pk))
        self.assertFalse(CustomField.objects.filter(pk=cf.pk).exists())

    def test_field_is_not_live_while_deleting(self):
        cf = self.create_field()
        Site.objects.update(custom_field_data={'field1': 'foo'})
        cf.delete()

        site = Site.objects.first()
        self.assertNotIn(cf, CustomField.objects.get_for_model(Site))
        self.assertNotIn('field1', site.cf)
        self.assertNotIn('field1', {f.name for f in site.get_custom_fields()})

    def test_stored_data_is_pruned_while_deleting(self):
        """
        The converse of a field being provisioned: one on its way out has no claim on the data, so an
        object saved before the purge job reaches it sheds the value as stale.
        """
        cf = self.create_field()
        Site.objects.update(custom_field_data={'field1': 'foo'})
        cf.delete()

        site = Site.objects.first()
        site.full_clean()
        site.save()

        site.refresh_from_db()
        self.assertNotIn('field1', site.custom_field_data)

    def test_purge_job_removes_data_and_field(self):
        cf = self.create_field()
        Site.objects.update(custom_field_data={'field1': 'foo'})
        cf.delete()

        self.assertTrue(purge_custom_field(cf.pk))

        self.assertFalse(CustomField.objects.filter(pk=cf.pk).exists())
        self.assertEqual(Site.objects.filter(custom_field_data__has_key='field1').count(), 0)

    def test_purge_job_commits_each_batch(self):
        cf = self.create_field()
        Site.objects.update(custom_field_data={'field1': 'foo'})
        cf.delete()

        with patch.object(CustomField, '_update_object_data') as update:
            purge_custom_field(cf.pk)

        update.assert_called()
        for call in update.call_args_list:
            self.assertTrue(call.kwargs['commit_per_batch'])

    def test_purge_job_is_idempotent(self):
        cf = self.create_field()
        cf.delete()
        purge_custom_field(cf.pk)

        # A second run finds the field already gone and does nothing
        self.assertFalse(purge_custom_field(cf.pk))

    def test_deleting_twice_does_not_repeat_the_deletion(self):
        cf = self.create_field()
        cf.delete()

        cf.delete()

        self.assertTrue(CustomField.objects.filter(pk=cf.pk).exists())

    def test_deletion_is_decided_against_the_stored_status(self):
        """
        The status is read from the database rather than taken from the instance in hand, which a
        concurrent deletion may have marked since it was fetched. Acting on the stale copy would
        dispatch the deletion signals a second time, recording a second change and firing the
        deletion's event rules again for a field already gone.
        """
        cf = self.create_field()
        # Retained, as a deletion clears the primary key of the instance it was called on
        pk = cf.pk

        # Marked directly, leaving the instance in hand still reporting the field as live
        CustomField.objects.filter(pk=pk).update(status=CustomFieldStatusChoices.STATUS_DELETING)
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_ACTIVE)

        request = RequestFactory().get('/')
        request.id = uuid.uuid4()
        request.user = self.user
        with event_tracking(request):
            deleted = cf.delete()

        self.assertEqual(deleted, (0, {}))
        self.assertFalse(
            ObjectChange.objects.filter(
                changed_object_type=ObjectType.objects.get_for_model(CustomField),
                changed_object_id=pk,
                action=ObjectChangeActionChoices.ACTION_DELETE,
            ).exists()
        )

    def test_deleting_a_field_already_removed_is_a_no_op(self):
        """
        The row may be gone by the time the status is read under its lock, a concurrent request
        having deleted the field outright. Nothing remains to delete, to report, or to purge.
        """
        cf = self.create_field()
        # Retained, as a deletion clears the primary key of the instance it was called on
        pk = cf.pk

        # Removed directly, leaving the instance in hand still reporting the field as live
        CustomField.objects.filter(pk=pk).delete()

        request = RequestFactory().get('/')
        request.id = uuid.uuid4()
        request.user = self.user
        with patch.object(CustomFieldPurgeJob, 'enqueue') as enqueue:
            with event_tracking(request), self.captureOnCommitCallbacks(execute=True):
                deleted = cf.delete()

        self.assertEqual(deleted, (0, {}))
        enqueue.assert_not_called()
        # The deletion signals belong to the request which removed the row, not to this one
        self.assertFalse(
            ObjectChange.objects.filter(
                changed_object_type=ObjectType.objects.get_for_model(CustomField),
                changed_object_id=pk,
                action=ObjectChangeActionChoices.ACTION_DELETE,
            ).exists()
        )

    def test_deleting_a_field_already_pending_deletion_enqueues_a_fresh_purge_job(self):
        """
        delete() is the only route to a purge job, so a field left pending deletion by a job which
        never ran must be given another when its deletion is retried. It could not otherwise be
        removed at all, and would hold its name against a replacement indefinitely.
        """
        cf = self.create_field()
        cf.delete()

        with patch.object(CustomFieldPurgeJob, 'enqueue') as enqueue:
            with self.captureOnCommitCallbacks(execute=True):
                cf.delete()

        enqueue.assert_called_once()
        self.assertEqual(enqueue.call_args.kwargs['custom_field_pk'], cf.pk)

    def test_deleting_a_field_being_purged_is_refused(self):
        """
        A running purge job needs no help, and a second job would only wait on its lock, occupying a
        worker for as long as the first ran (see CUSTOMFIELD_JOB_TIMEOUT). The retry is refused as
        the deletion of a live field would be: returning quietly would have the caller report a
        deletion which did not happen, the field remaining exactly as it was.
        """
        cf = self.create_field()

        # Marked directly rather than by delete(), which would take the lock on this connection and
        # hold it for the remainder of the test transaction, leaving none for the job to hold
        CustomField.objects.filter(pk=cf.pk).update(status=CustomFieldStatusChoices.STATUS_DELETING)
        cf.refresh_from_db()

        with patch.object(CustomFieldPurgeJob, 'enqueue') as enqueue:
            with hold_data_lock(cf):
                with self.assertRaises(AbortRequest):
                    cf.delete()

        enqueue.assert_not_called()
        cf.refresh_from_db()
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_DELETING)

    def test_deleting_a_field_being_purged_is_reported_to_the_user(self):
        """
        The refusal reaches the user as an error, rather than the unqualified success the delete view
        reports for any deletion which does not raise.
        """
        cf = self.create_field()
        CustomField.objects.filter(pk=cf.pk).update(status=CustomFieldStatusChoices.STATUS_DELETING)
        cf.refresh_from_db()
        self.add_permissions('extras.view_customfield', 'extras.delete_customfield')

        with hold_data_lock(cf):
            response = self.client.post(
                reverse('extras:customfield_delete', kwargs={'pk': cf.pk}),
                data={'confirm': True},
                follow=True,
            )

        self.assertEqual(
            [str(m) for m in response.context['messages']],
            [f"Custom field '{cf.name}' is being updated by a background job and cannot be deleted "
             f"until that job has completed."]
        )
        self.assertTrue(CustomField.objects.filter(pk=cf.pk).exists())

    def test_aborted_deletion_leaves_the_field_intact(self):
        """
        A receiver rejecting the deletion (e.g. handle_deleted_object() raising AbortRequest for a
        failed protection rule) must leave the field live, rather than marked for a purge which
        would destroy the very data the rule protected.
        """
        cf = self.create_field()
        Site.objects.update(custom_field_data={'field1': 'foo'})

        def reject(sender, instance, **kwargs):
            raise AbortRequest("Deletion is prevented by a protection rule")

        pre_delete.connect(reject, sender=CustomField)
        try:
            with self.assertRaises(AbortRequest):
                cf.delete()
        finally:
            pre_delete.disconnect(reject, sender=CustomField)

        cf = CustomField.objects.get(pk=cf.pk)
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_ACTIVE)
        self.assertIn(cf, CustomField.objects.get_for_model(Site))
        self.assertEqual(Site.objects.filter(custom_field_data__field1='foo').count(), 2)

    def test_purge_job_overrides_the_default_timeout(self):
        cf = self.create_field()
        Site.objects.update(custom_field_data={'field1': 'foo'})

        with patch.object(CustomFieldPurgeJob, 'enqueue') as enqueue:
            with self.captureOnCommitCallbacks(execute=True):
                cf.delete()

        enqueue.assert_called_once()
        self.assertEqual(enqueue.call_args.kwargs['job_timeout'], CUSTOMFIELD_JOB_TIMEOUT)
        self.assertEqual(enqueue.call_args.kwargs['custom_field_pk'], cf.pk)

    def test_purge_job_is_enqueued(self):
        cf = self.create_field()
        Site.objects.update(custom_field_data={'field1': 'foo'})

        with patch('core.models.jobs.django_rq') as django_rq:
            with self.captureOnCommitCallbacks(execute=True):
                cf.delete()

        job = Job.objects.get(name__startswith=CustomFieldPurgeJob.name)
        self.assertIsNone(job.object_type)
        self.assertIn(str(cf), job.name)
        self.assertEqual(
            django_rq.get_queue.return_value.enqueue.call_args.kwargs['custom_field_pk'], cf.pk
        )

    def test_deletion_records_a_change(self):
        """
        The change log must report the deletion where the user performed it, rather than when the
        row is eventually removed in a worker (where there is no request to attribute it to).
        """
        cf = self.create_field()

        request = RequestFactory().get('/')
        request.id = uuid.uuid4()
        request.user = self.user
        with event_tracking(request):
            cf.delete()

        self.assertTrue(
            ObjectChange.objects.filter(
                changed_object_type=ObjectType.objects.get_for_model(CustomField),
                changed_object_id=cf.pk,
                action=ObjectChangeActionChoices.ACTION_DELETE,
            ).exists()
        )

    def test_deletion_is_scoped_to_the_write_database(self):
        """
        The commit hook must be registered against the connection the marking was written on, or the
        purge job can be enqueued before -- or without -- the field being durably marked.
        """
        cf = self.create_field()

        with patch('extras.models.customfields.transaction.on_commit') as on_commit:
            cf.delete()

        # transaction.on_commit is patched on the shared module, so hooks registered by unrelated
        # machinery during the delete (deferred search indexing, for one) are captured here too.
        # Select the hook which enqueues the purge job rather than assuming it is the only one.
        calls = [
            call for call in on_commit.call_args_list
            if 'CustomField.delete' in getattr(call.args[0], '__qualname__', '')
        ]
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].kwargs['using'], DEFAULT_DB_ALIAS)

    #
    # Name reservation
    #

    def test_name_is_reserved_while_deleting(self):
        """
        A field pending deletion holds its name, so that a new field cannot inherit the values still
        stored against it.
        """
        cf = self.create_field()
        Site.objects.update(custom_field_data={'field1': 'foo'})
        cf.delete()

        replacement = CustomField(name='field1', type=CustomFieldTypeChoices.TYPE_TEXT)
        with self.assertRaises(ValidationError):
            replacement.full_clean()

    def test_rename_onto_reserved_name_is_rejected(self):
        cf = self.create_field()
        Site.objects.update(custom_field_data={'field1': 'foo'})
        cf.delete()
        other = self.create_field(name='field2')

        other.name = 'field1'
        with self.assertRaises(ValidationError):
            other.full_clean()

    def test_name_is_released_once_purged(self):
        cf = self.create_field()
        cf.delete()
        purge_custom_field(cf.pk)

        replacement = CustomField(name='field1', type=CustomFieldTypeChoices.TYPE_TEXT)
        replacement.full_clean()  # Should not raise

    #
    # Modification and deletion guards
    #

    def test_pending_field_cannot_be_modified(self):
        cf = self.create_field(default='foo')

        cf.label = 'Changed'
        with self.assertRaises(ValidationError):
            cf.full_clean()

    def test_deletion_claims_the_data_lock_without_waiting(self):
        """
        A job holds the field's data lock for the duration of its bulk update, so a deletion which
        waited on it would occupy a worker for as long as the job ran (see CUSTOMFIELD_JOB_TIMEOUT).
        """
        cf = self.create_field()

        with CaptureQueriesContext(connection) as queries:
            cf.delete()

        self.assertTrue(
            any('pg_try_advisory_xact_lock' in query['sql'] for query in queries),
            "Deletion did not claim the field's data lock without waiting"
        )

    def test_deletion_holds_the_data_lock_until_its_transaction_ends(self):
        """
        Where the caller supplies its own transaction -- BulkDeleteView, and every REST API deletion
        -- the field's new status is still uncommitted when delete() returns. Releasing the lock
        there would let a provisioning job read the field as live and set it live again.
        """
        cf = self.create_field()

        with transaction.atomic():
            cf.delete()

        # delete() has returned and its own atomic block has exited, but the enclosing transaction
        # has yet to commit, so the lock must still be held
        with self.assertRaises(RuntimeError):
            with hold_data_lock(cf):
                pass

    def test_deletion_is_refused_while_a_job_holds_the_data_lock(self):
        """
        Failing to take the lock aborts the deletion cleanly, rather than surfacing a database error,
        and must leave the field exactly as it was.
        """
        cf = self.create_field()

        with hold_data_lock(cf):
            with self.assertRaises(AbortRequest):
                cf.delete()

            cf.refresh_from_db()
            self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_ACTIVE)

        cf.delete()  # Released: the deletion now proceeds

        cf.refresh_from_db()
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_DELETING)

    def test_stranded_field_can_be_deleted(self):
        """
        The refusal is on the lock, not on the status: a field left mid-provisioning by a job which
        never ran holds no lock, and must remain deletable.
        """
        cf = self.create_field(default='foo')
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_PROVISIONING)

        cf.delete()

        cf.refresh_from_db()
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_DELETING)


class InlineCustomFieldDataTestCase(TestCase):
    """
    Where few enough objects are affected, provisioning and purging remain synchronous: the field is
    live (or gone) as soon as the request completes, with no background job involved.
    """
    @classmethod
    def setUpTestData(cls):
        Site.objects.create(name='Site A', slug='site-a')
        cls.object_type = ObjectType.objects.get_for_model(Site)

    def test_provisioning_is_inline(self):
        cf = CustomField.objects.create(
            name='field1', type=CustomFieldTypeChoices.TYPE_TEXT, default='foo'
        )
        cf.object_types.set([self.object_type])

        cf.refresh_from_db()
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_ACTIVE)
        self.assertEqual(Site.objects.filter(custom_field_data__field1='foo').count(), 1)

    def test_inline_provisioning_is_atomic(self):
        """
        The request path answers to an enclosing transaction, which owns the commit: committing each
        batch there would silently do nothing, and a failure part-way must leave nothing behind.
        """
        with patch.object(CustomField, '_update_object_data') as update:
            cf = CustomField.objects.create(
                name='field1', type=CustomFieldTypeChoices.TYPE_TEXT, default='foo'
            )
            cf.object_types.set([self.object_type])

        update.assert_called()
        for call in update.call_args_list:
            self.assertFalse(call.kwargs['commit_per_batch'])

    def test_default_added_later_is_not_backfilled(self):
        """
        A default added to a field which already exists is not backfilled, and assigning a further
        object type must not backfill it either: only the newly assigned type is provisioned. The
        sites below would otherwise acquire a value they were documented never to receive.
        """
        cf = CustomField.objects.create(name='field1', type=CustomFieldTypeChoices.TYPE_TEXT)
        cf.object_types.set([self.object_type])
        self.assertEqual(Site.objects.first().custom_field_data, {})

        cf.default = 'foo'
        cf.save()
        self.assertEqual(Site.objects.first().custom_field_data, {})

        rack = Rack.objects.create(name='Rack 1', site=Site.objects.first())
        cf.object_types.add(ObjectType.objects.get_for_model(Rack))

        # The newly assigned type is provisioned; the one assigned before the default is not
        rack.refresh_from_db()
        self.assertEqual(rack.custom_field_data['field1'], 'foo')
        self.assertEqual(Site.objects.first().custom_field_data, {})

    def test_provisioning_preserves_existing_values(self):
        """
        Values stored against a type assigned previously must survive a further assignment.
        """
        cf = CustomField.objects.create(
            name='field1', type=CustomFieldTypeChoices.TYPE_TEXT, default='foo'
        )
        cf.object_types.set([self.object_type])
        Site.objects.update(custom_field_data={'field1': 'bar'})

        cf.object_types.add(ObjectType.objects.get_for_model(Rack))

        self.assertEqual(Site.objects.first().custom_field_data['field1'], 'bar')

    def test_provisioning_preserves_cleared_values(self):
        """
        A cleared value is stored as a JSON null rather than an absent key, and must survive
        reprovisioning just as a set value does.
        """
        cf = CustomField.objects.create(
            name='field1', type=CustomFieldTypeChoices.TYPE_TEXT, default='foo'
        )
        cf.object_types.set([self.object_type])
        Site.objects.update(custom_field_data={'field1': None})

        cf.object_types.add(ObjectType.objects.get_for_model(Rack))

        self.assertIsNone(Site.objects.first().custom_field_data['field1'])

    def test_deletion_is_inline(self):
        cf = CustomField.objects.create(name='field1', type=CustomFieldTypeChoices.TYPE_TEXT)
        cf.object_types.set([self.object_type])
        Site.objects.update(custom_field_data={'field1': 'foo'})

        cf.delete()

        self.assertFalse(CustomField.objects.filter(pk=cf.pk).exists())
        self.assertEqual(Site.objects.filter(custom_field_data__has_key='field1').count(), 0)


@override_settings(BULK_UPDATE_CHUNK_SIZE=None)
class UnchunkedCustomFieldDataTestCase(TestCase):
    """
    Setting BULK_UPDATE_CHUNK_SIZE to None disables chunking, so a bulk update is issued as a single
    unbounded statement. There is then no batch size for the deferral threshold to test against, and
    an unbounded JSONB rewrite is exactly what must not run inside a request -- so any affected
    object sends the work to a background job, which issues that one statement under a timeout
    generous enough to survive it.
    """
    @classmethod
    def setUpTestData(cls):
        Site.objects.create(name='Site A', slug='site-a')
        cls.object_type = ObjectType.objects.get_for_model(Site)

    @staticmethod
    def _count_updates(queries, model):
        """
        Count the UPDATE statements issued against the given model's table, ignoring those the job
        makes to the custom field row itself (marking it active).
        """
        table = model._meta.db_table
        return len([
            q for q in queries
            if q['sql'].strip().upper().startswith('UPDATE') and table in q['sql']
        ])

    def test_provisioning_is_deferred(self):
        """
        A single object is enough: with chunking disabled there is no bound on the statement the
        request would otherwise issue.
        """
        cf = CustomField.objects.create(
            name='field1', type=CustomFieldTypeChoices.TYPE_TEXT, default='foo'
        )
        cf.object_types.set([self.object_type])

        cf.refresh_from_db()
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_PROVISIONING)
        self.assertEqual(Site.objects.filter(custom_field_data__has_key='field1').count(), 0)

    def test_provisioning_job_backfills_in_a_single_statement(self):
        cf = CustomField.objects.create(
            name='field1', type=CustomFieldTypeChoices.TYPE_TEXT, default='foo'
        )
        cf.object_types.set([self.object_type])

        with CaptureQueriesContext(connection) as queries:
            self.assertTrue(provision_custom_field(cf.pk, [self.object_type.pk]))

        # One statement covers the table, rather than one per batch
        self.assertEqual(self._count_updates(queries.captured_queries, Site), 1)

        cf.refresh_from_db()
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_ACTIVE)
        self.assertEqual(Site.objects.filter(custom_field_data__field1='foo').count(), 1)

    def test_field_affecting_no_objects_stays_inline(self):
        """
        A limit of zero still leaves the probe testing for a single row, so a field which rewrites
        nothing goes live in the request rather than waiting on a job with no work to do.
        """
        cf = CustomField.objects.create(
            name='field1', type=CustomFieldTypeChoices.TYPE_TEXT, default='foo'
        )

        # No racks exist, so there is nothing to rewrite
        cf.object_types.set([ObjectType.objects.get_for_model(Rack)])

        cf.refresh_from_db()
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_ACTIVE)

    def test_deletion_is_deferred(self):
        cf = CustomField.objects.create(name='field1', type=CustomFieldTypeChoices.TYPE_TEXT)
        cf.object_types.set([self.object_type])
        Site.objects.update(custom_field_data={'field1': 'foo'})

        cf.delete()

        cf.refresh_from_db()
        self.assertEqual(cf.status, CustomFieldStatusChoices.STATUS_DELETING)
        self.assertTrue(purge_custom_field(cf.pk))
        self.assertFalse(CustomField.objects.filter(pk=cf.pk).exists())
        self.assertEqual(Site.objects.filter(custom_field_data__has_key='field1').count(), 0)
