from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from dcim.models import DeviceType, Manufacturer, RackType
from ndx.choices import ImportRecordSourceChoices
from ndx.filtersets import EnrichmentFilterSet, ImportRecordFilterSet
from ndx.models import Enrichment, ImportRecord
from utilities.testing import ChangeLoggedFilterSetTestMixin

from .utils import create_import_record


class ImportRecordTestCase(TestCase, ChangeLoggedFilterSetTestMixin):
    queryset = ImportRecord.objects.all()
    filterset = ImportRecordFilterSet
    ignore_fields = ('enrichment',)

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        device_types = [
            DeviceType.objects.create(manufacturer=manufacturer, model=f'Model {i}', slug=f'model-{i}')
            for i in range(1, 3)
        ]
        rack_type = RackType.objects.create(manufacturer=manufacturer, model='Rack', slug='rack', width=19)
        records = (
            create_import_record(
                device_types[0], 'cisco/model-1', source=ImportRecordSourceChoices.SOURCE_COMMUNITY,
                checksum='aaa',
            ),
            create_import_record(
                device_types[1], 'cisco/model-2', source=ImportRecordSourceChoices.SOURCE_NETBOX_LABS,
                checksum='bbb', update_available=True,
            ),
            create_import_record(
                rack_type, 'apc/rack', entry_type='rack-type', source=ImportRecordSourceChoices.SOURCE_BOTH,
                checksum='ccc',
            ),
        )
        Enrichment.objects.create(import_record=records[0])

    def test_q(self):
        params = {'q': 'cisco'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_ndx_id(self):
        params = {'ndx_id': ['cisco/model-1', 'apc/rack']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_entry_type(self):
        params = {'entry_type': ['rack-type']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_vendor_slug(self):
        params = {'vendor_slug': ['cisco']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_source(self):
        params = {'source': [ImportRecordSourceChoices.SOURCE_COMMUNITY, ImportRecordSourceChoices.SOURCE_BOTH]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_checksum(self):
        params = {'checksum': ['aaa', 'bbb']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_update_available(self):
        params = {'update_available': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_has_enrichment(self):
        params = {'has_enrichment': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {'has_enrichment': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_object_type(self):
        params = {'object_type': ['dcim.devicetype']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'object_type_id': [ContentType.objects.get_for_model(RackType).pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_object_id(self):
        params = {'object_id': [DeviceType.objects.first().pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class EnrichmentTestCase(TestCase, ChangeLoggedFilterSetTestMixin):
    queryset = Enrichment.objects.all()
    filterset = EnrichmentFilterSet
    ignore_fields = ('api_types', 'extensions')

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        records = [
            create_import_record(
                DeviceType.objects.create(manufacturer=manufacturer, model=f'Model {i}', slug=f'model-{i}'),
                f'cisco/model-{i}',
            )
            for i in range(1, 4)
        ]
        Enrichment.objects.create(import_record=records[0], nos='IOS-XE', nos_family='IOS', has_lifecycle=True)
        Enrichment.objects.create(import_record=records[1], nos='NX-OS', nos_family='NX-OS', has_thermal=True)
        Enrichment.objects.create(import_record=records[2], nos='Junos', nos_family='Junos', has_lifecycle=True)

    def test_q(self):
        params = {'q': 'ios'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_import_record(self):
        params = {'import_record_id': [ImportRecord.objects.first().pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_nos(self):
        params = {'nos': ['IOS-XE', 'Junos']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_nos_family(self):
        params = {'nos_family': ['IOS']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_has_lifecycle(self):
        params = {'has_lifecycle': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_thermal(self):
        params = {'has_thermal': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
