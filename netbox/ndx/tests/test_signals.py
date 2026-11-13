from django.test import TestCase

from dcim.models import DeviceType, Manufacturer
from ndx.models import Enrichment, ImportRecord, Provenance

from .utils import create_import_record


class SignalsTestCase(TestCase):

    def test_delete_object_deletes_import_record(self):
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Model', slug='model')
        other_device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Other', slug='other')
        record = create_import_record(device_type, 'acme/model')
        create_import_record(other_device_type, 'acme/other')
        enrichment = Enrichment.objects.create(import_record=record)
        Provenance.objects.create(enrichment=enrichment, field='lifecycle.ga_date')

        device_type.delete()

        self.assertEqual(list(ImportRecord.objects.values_list('ndx_id', flat=True)), ['acme/other'])
        self.assertFalse(Enrichment.objects.exists())
        self.assertFalse(Provenance.objects.exists())
