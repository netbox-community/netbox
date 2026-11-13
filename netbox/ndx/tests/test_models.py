from django.test import TestCase

from dcim.models import DeviceType, Manufacturer
from ndx.models import Enrichment, Provenance

from .utils import create_import_record


class ImportRecordTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        cls.device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Model', slug='model')

    def test_import_record(self):
        record = create_import_record(self.device_type, 'acme/model-x')
        self.assertEqual(str(record), 'acme/model-x')
        self.assertEqual(record.slug, 'model-x')
        self.assertEqual(record.object, self.device_type)

    def test_related_objects(self):
        record = create_import_record(self.device_type, 'acme/model')
        enrichment = Enrichment.objects.create(import_record=record)
        provenance = Provenance.objects.create(enrichment=enrichment, field='lifecycle.ga_date')
        self.assertEqual(enrichment.get_absolute_url(), record.get_absolute_url())
        self.assertEqual(enrichment.to_objectchange('create').related_object, record)
        self.assertEqual(provenance.to_objectchange('create').related_object, record)
