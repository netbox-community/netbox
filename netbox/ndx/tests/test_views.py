from unittest.mock import MagicMock, patch

from django.test import override_settings
from django.urls import reverse

from core.models import Job
from dcim.models import DeviceType, Manufacturer
from ndx.constants import UPGRADE_URL
from ndx.models import Enrichment, ImportRecord, Provenance
from utilities.testing import TestCase, ViewTestCases

from .utils import (
    create_import_record,
    mock_auth_response,
    mock_entry,
    mock_error_response,
    mock_manifest_response,
    mock_search_response,
)


class ImportRecordTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    model = ImportRecord

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        records = [
            create_import_record(
                DeviceType.objects.create(manufacturer=manufacturer, model=f'Model {i}', slug=f'model-{i}'),
                f'acme/model-{i}',
            )
            for i in range(1, 4)
        ]
        enrichment = Enrichment.objects.create(
            import_record=records[0], ga_date='2020-01-01', nos='Acme OS', extensions={'gnmi': {'paths': []}}
        )
        Provenance.objects.create(enrichment=enrichment, field='lifecycle.ga_date', source='https://example.com/')

    def test_enrichment_panels(self):
        self.add_permissions('ndx.view_importrecord')
        record = ImportRecord.objects.get(ndx_id='acme/model-1')
        response = self.client.get(record.get_absolute_url())
        self.assertHttpStatus(response, 200)
        self.assertContains(response, 'Acme OS')
        self.assertContains(response, 'lifecycle.ga_date')
        self.assertContains(response, 'gnmi')

        # Enrichment panels are omitted for a record without enrichment
        record = ImportRecord.objects.get(ndx_id='acme/model-2')
        response = self.client.get(record.get_absolute_url())
        self.assertHttpStatus(response, 200)
        self.assertNotContains(response, 'Lifecycle')


class DeviceTypePanelTestCase(TestCase):

    def test_import_record_panel(self):
        self.add_permissions('dcim.view_devicetype', 'ndx.view_importrecord')
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Model', slug='model')

        response = self.client.get(device_type.get_absolute_url())
        self.assertHttpStatus(response, 200)
        self.assertNotContains(response, 'acme/model')

        record = create_import_record(device_type, 'acme/model', update_available=True)
        Enrichment.objects.create(import_record=record, last_support_date='2030-01-01')
        response = self.client.get(device_type.get_absolute_url())
        self.assertContains(response, 'acme/model')
        self.assertContains(response, '2030-01-01')
        self.assertContains(response, 'Update available')
        self.assertNotContains(response, 'free NDX tier')

    @override_settings(NDX_API_TOKEN='token', ISOLATED_DEPLOYMENT=False)
    def test_import_record_panel_free_tier(self):
        self.add_permissions('dcim.view_devicetype', 'ndx.view_importrecord')
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Model', slug='model')
        create_import_record(device_type, 'acme/model')
        job = Job.objects.create(
            name='NDX Catalog Sync', status='completed', data={'tier': 'paid'},
            job_id='66666666-6666-6666-6666-666666666666',
        )
        self.assertNotContains(self.client.get(device_type.get_absolute_url()), 'free NDX tier')

        job.data = {'tier': 'free'}
        job.save()
        response = self.client.get(device_type.get_absolute_url())
        self.assertContains(response, 'free NDX tier')
        self.assertContains(response, UPGRADE_URL)


@override_settings(NDX_API_TOKEN='token', ISOLATED_DEPLOYMENT=False)
class CatalogViewsTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.add_permissions('ndx.view_importrecord')
        self.mock_client = MagicMock()
        self.mock_client.api_url = 'https://netboxlabs.com/ndx/api/v1'
        self.mock_client.get_all_vendors.return_value = [{'slug': 'cisco', 'display_name': 'Cisco'}]
        for target in ('ndx.views.get_client', 'ndx.importers.get_client'):
            patcher = patch(target, return_value=self.mock_client)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_catalog(self):
        entries = [dict(mock_entry(slug=f'model-{i}', model=f'Model {i}')) for i in range(1, 3)]
        self.mock_client.search.return_value = mock_search_response(entries, total=500)

        response = self.client.get(f"{reverse('ndx:catalog')}?q=model&vendor=cisco&per_page=25")
        self.assertHttpStatus(response, 200)
        self.assertContains(response, 'Model 1')
        self.assertContains(response, 'value="cisco/model-2"')
        # The remote result count drives pagination
        self.assertContains(response, '500')
        self.assertEqual(self.mock_client.search.call_args.kwargs['vendor'], 'cisco')
        self.assertEqual(self.mock_client.search.call_args.kwargs['q'], 'model')

    def test_catalog_paging(self):
        entries = [dict(mock_entry(slug=f'model-{i}', model=f'Model {i}')) for i in range(1, 51)]
        self.mock_client.search.return_value = mock_search_response(entries, total=1000)
        self.client.get(f"{reverse('ndx:catalog')}?page=3&per_page=50")
        # Only the requested page is retrieved (which also provides the total count)
        self.assertEqual(
            [(call.kwargs['offset'], call.kwargs['limit']) for call in self.mock_client.search.call_args_list],
            [(100, 50)],
        )

    def test_catalog_last_page(self):
        entries = [dict(mock_entry(slug=f'model-{i}', model=f'Model {i}')) for i in range(1, 11)]
        self.mock_client.search.return_value = mock_search_response(entries, total=110)
        response = self.client.get(f"{reverse('ndx:catalog')}?page=3&per_page=50")
        self.assertContains(response, 'Model 10')
        self.assertEqual(self.mock_client.search.call_count, 1)

    def test_catalog_unlisted_vendor(self):
        # A vendor which isn't listed (e.g. because the vendor list is unavailable) is still applied
        self.mock_client.get_all_vendors.return_value = []
        self.mock_client.search.return_value = mock_search_response([dict(mock_entry())])
        self.client.get(f"{reverse('ndx:catalog')}?vendor=juniper")
        self.assertEqual(self.mock_client.search.call_args.kwargs['vendor'], 'juniper')

    def test_catalog_htmx(self):
        self.mock_client.search.return_value = mock_search_response([dict(mock_entry())])
        response = self.client.get(reverse('ndx:catalog'), HTTP_HX_REQUEST='true')
        self.assertHttpStatus(response, 200)
        self.assertContains(response, 'Catalyst 9300')
        self.assertNotContains(response, '<html')

    def test_catalog_error(self):
        self.mock_client.search.return_value = mock_error_response(401)
        response = self.client.get(reverse('ndx:catalog'))
        self.assertHttpStatus(response, 200)
        self.assertContains(response, 'NDX API token rejected')

    def test_catalog_entry(self):
        self.mock_client.get_entry.return_value = mock_entry()
        url = reverse('ndx:catalog_entry', kwargs={'vendor_slug': 'cisco', 'slug': 'catalyst-9300'})
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        self.assertContains(response, 'GigabitEthernet0/0/0')
        self.assertContains(response, 'Modbus')

        self.mock_client.get_entry.return_value = mock_error_response(404)
        response = self.client.get(reverse('ndx:catalog_entry', kwargs={'vendor_slug': 'cisco', 'slug': 'missing'}))
        self.assertHttpStatus(response, 404)

    def test_import_single(self):
        self.user.is_superuser = True
        self.user.save()
        self.mock_client.get_manifest.return_value = mock_manifest_response({'cisco': 'abc123'})
        self.mock_client.get_entry.return_value = mock_entry()
        self.mock_client.get_image.return_value = None

        response = self.client.post(reverse('ndx:catalog_import'), {'pk': ['cisco/catalyst-9300']})
        device_type = DeviceType.objects.get(model='Catalyst 9300')
        self.assertRedirects(response, device_type.get_absolute_url(), fetch_redirect_response=False)
        self.assertTrue(ImportRecord.objects.filter(ndx_id='cisco/catalyst-9300').exists())

    @patch('ndx.views.ImportJob.enqueue')
    def test_import_multiple(self, enqueue):
        self.add_permissions('dcim.add_devicetype')
        enqueue.return_value = Job.objects.create(name='NDX Import', job_id='11111111-1111-1111-1111-111111111111')
        response = self.client.post(reverse('ndx:catalog_import'), {'pk': ['cisco/a', 'cisco/b']})
        self.assertRedirects(response, enqueue.return_value.get_absolute_url(), fetch_redirect_response=False)
        self.assertEqual(enqueue.call_args.kwargs['ndx_ids'], ['cisco/a', 'cisco/b'])

    @patch('ndx.views.ImportJob.enqueue')
    def test_import_permission_required(self, enqueue):
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Model', slug='model')
        create_import_record(device_type, 'acme/model', update_available=True)

        # Requires permission to create an importable type of object
        response = self.client.post(reverse('ndx:catalog_import'), {'pk': ['cisco/a', 'cisco/b']})
        self.assertHttpStatus(response, 403)
        response = self.client.post(reverse('ndx:apply_updates'))
        self.assertHttpStatus(response, 403)
        enqueue.assert_not_called()

    def test_sync_status_error(self):
        self.mock_client.verify_auth.return_value = mock_auth_response('paid')
        Job.objects.create(
            name='NDX Catalog Sync', status='failed', data={'error': 'Manifest unavailable'},
            job_id='55555555-5555-5555-5555-555555555555',
        )
        response = self.client.get(reverse('ndx:sync_status'))
        self.assertHttpStatus(response, 200)
        self.assertContains(response, 'Manifest unavailable')

    def test_sync_status(self):
        self.mock_client.verify_auth.return_value = mock_auth_response('paid')
        Job.objects.create(
            name='NDX Catalog Sync', status='completed', data={'catalog_count': 12345},
            job_id='22222222-2222-2222-2222-222222222222',
        )
        response = self.client.get(reverse('ndx:sync_status'))
        self.assertHttpStatus(response, 200)
        self.assertContains(response, 'paid')
        self.assertContains(response, '12345')

    @patch('ndx.views.SyncJob.enqueue')
    def test_sync(self, enqueue):
        enqueue.side_effect = lambda **kwargs: Job.objects.create(
            name='NDX Catalog Sync', job_id='33333333-3333-3333-3333-333333333333'
        )
        response = self.client.post(reverse('ndx:sync'))
        self.assertHttpStatus(response, 403)

        self.add_permissions('ndx.sync_importrecord')
        response = self.client.post(reverse('ndx:sync'))
        self.assertRedirects(response, reverse('ndx:sync_status'), fetch_redirect_response=False)
        enqueue.assert_called_once()

        # No further job is queued while one is pending
        response = self.client.post(reverse('ndx:sync'))
        self.assertRedirects(response, reverse('ndx:sync_status'), fetch_redirect_response=False)
        enqueue.assert_called_once()

    def test_permission_required(self):
        self.remove_permissions('ndx.view_importrecord')
        self.assertHttpStatus(self.client.get(reverse('ndx:catalog')), 403)

    @override_settings(NDX_API_TOKEN=None)
    def test_disabled(self):
        self.assertHttpStatus(self.client.get(reverse('ndx:catalog')), 404)
        self.assertHttpStatus(self.client.get(reverse('ndx:sync_status')), 404)
