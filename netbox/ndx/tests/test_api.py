from unittest.mock import MagicMock, patch

from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from core.models import Job
from dcim.models import DeviceType, Manufacturer
from ndx.constants import IMPORT_BACKGROUND_THRESHOLD
from ndx.models import Enrichment, ImportRecord
from utilities.testing import APITestCase, APIViewTestCases

from .utils import (
    create_import_record,
    mock_entry,
    mock_error_response,
    mock_manifest_response,
    mock_search_response,
)


class AppTest(APITestCase):

    def test_root(self):
        response = self.client.get(reverse('ndx-api:api-root'), **self.header)
        self.assertEqual(response.status_code, 200)


def create_test_records():
    manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
    records = [
        create_import_record(
            DeviceType.objects.create(manufacturer=manufacturer, model=f'Model {i}', slug=f'model-{i}'),
            f'acme/model-{i}',
        )
        for i in range(1, 4)
    ]
    for record in records:
        Enrichment.objects.create(import_record=record, nos='Acme OS', has_platform=True)
    return records


class ImportRecordTestCase(
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
    APIViewTestCases.GraphQLTestCase,
):
    model = ImportRecord
    brief_fields = ['display', 'id', 'ndx_id', 'object_id', 'object_type', 'update_available', 'url']

    @classmethod
    def setUpTestData(cls):
        create_test_records()

    def test_create_and_update_not_allowed(self):
        self.user.is_superuser = True
        self.user.save()
        record = ImportRecord.objects.first()
        list_url = reverse('ndx-api:importrecord-list')
        detail_url = reverse('ndx-api:importrecord-detail', kwargs={'pk': record.pk})

        self.assertHttpStatus(
            self.client.post(list_url, {'ndx_id': 'acme/new'}, format='json', **self.header),
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assertHttpStatus(
            self.client.patch(detail_url, {'update_available': True}, format='json', **self.header),
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assertHttpStatus(
            self.client.patch(list_url, [{'id': record.pk}], format='json', **self.header),
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class EnrichmentTestCase(
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.GraphQLTestCase,
):
    model = Enrichment
    brief_fields = ['display', 'id', 'import_record', 'url']
    user_permissions = ('ndx.view_importrecord',)

    @classmethod
    def setUpTestData(cls):
        create_test_records()


@override_settings(NDX_API_TOKEN='token', ISOLATED_DEPLOYMENT=False)
class CatalogTestCase(APITestCase):

    def setUp(self):
        super().setUp()
        self.add_permissions('ndx.view_importrecord')
        self.mock_client = MagicMock()
        patcher = patch('ndx.api.views.get_client', return_value=self.mock_client)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_list(self):
        entries = [dict(mock_entry(slug=f'model-{i}', model=f'Model {i}')) for i in range(1, 3)]
        self.mock_client.search.return_value = mock_search_response(entries, total=120)

        url = reverse('ndx-api:catalog-list')
        response = self.client.get(f'{url}?q=model&vendor=cisco&type=device-type&limit=2&offset=2', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 120)
        self.assertIn('offset=4', response.data['next'])
        self.assertNotIn('offset', response.data['previous'])
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['ndx_id'], 'cisco/model-1')
        self.assertIsNone(response.data['results'][0]['import_record_id'])
        self.mock_client.search.assert_called_once_with(
            q='model', vendor='cisco', entry_type='device-type', offset=2, limit=2,
        )

    def test_list_brief(self):
        self.mock_client.search.return_value = mock_search_response([dict(mock_entry())])
        response = self.client.get(f"{reverse('ndx-api:catalog-list')}?brief=true", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(
            sorted(response.data['results'][0]),
            ['manufacturer', 'model', 'ndx_id', 'part_number', 'slug', 'type', 'vendor_slug'],
        )

    def test_list_limit_capped(self):
        self.mock_client.search.return_value = mock_search_response()
        self.client.get(f"{reverse('ndx-api:catalog-list')}?limit=5000", **self.header)
        self.assertEqual(self.mock_client.search.call_args.kwargs['limit'], 200)

    def test_list_error(self):
        self.mock_client.search.return_value = mock_error_response(429)
        response = self.client.get(reverse('ndx-api:catalog-list'), **self.header)
        self.assertHttpStatus(response, status.HTTP_429_TOO_MANY_REQUESTS)

        self.mock_client.search.return_value = mock_error_response(401)
        response = self.client.get(reverse('ndx-api:catalog-list'), **self.header)
        self.assertHttpStatus(response, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_retrieve(self):
        self.mock_client.get_entry.return_value = mock_entry()
        url = reverse('ndx-api:catalog-detail', kwargs={'ndx_id': 'cisco/catalyst-9300'})
        response = self.client.get(url, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['model'], 'Catalyst 9300')
        self.assertIn('dtl', response.data)
        self.mock_client.get_entry.assert_called_once_with('cisco', 'catalyst-9300')

    def test_retrieve_not_found(self):
        self.mock_client.get_entry.return_value = mock_error_response(404)
        url = reverse('ndx-api:catalog-detail', kwargs={'ndx_id': 'cisco/missing'})
        self.assertHttpStatus(self.client.get(url, **self.header), status.HTTP_404_NOT_FOUND)

    @patch('ndx.importers.get_client')
    def test_import(self, importer_get_client):
        self.user.is_superuser = True
        self.user.save()
        importer_get_client.return_value = self.mock_client
        self.mock_client.get_manifest.return_value = mock_manifest_response({'cisco': 'abc123'})
        self.mock_client.get_entry.return_value = mock_entry()
        self.mock_client.get_image.return_value = None

        url = reverse('ndx-api:catalog-run-import')
        response = self.client.post(url, {'ndx_ids': ['cisco/catalyst-9300']}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['status'], 'created')
        self.assertEqual(response.data[0]['object_type'], 'dcim.devicetype')
        self.assertTrue(ImportRecord.objects.filter(ndx_id='cisco/catalyst-9300').exists())

    def test_import_manifest_unavailable(self):
        self.mock_client.get_manifest.return_value = mock_error_response(401)
        url = reverse('ndx-api:catalog-run-import')
        response = self.client.post(url, {'ndx_ids': ['cisco/catalyst-9300']}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn('HTTP 401', response.data['detail'])
        self.mock_client.get_entry.assert_not_called()

    def test_import_permission_denied(self):
        self.mock_client.get_manifest.return_value = mock_manifest_response({'cisco': 'abc123'})
        self.mock_client.get_entry.return_value = mock_entry()
        url = reverse('ndx-api:catalog-run-import')
        response = self.client.post(url, {'ndx_ids': ['cisco/catalyst-9300']}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['status'], 'failed')
        self.assertFalse(DeviceType.objects.exists())

    @patch('ndx.api.views.ImportJob.enqueue')
    def test_import_background(self, enqueue):
        enqueue.return_value = Job.objects.create(
            name='NDX Import', user=self.user, job_id='11111111-1111-1111-1111-111111111111'
        )
        url = reverse('ndx-api:catalog-run-import')
        response = self.client.post(
            f'{url}?background=true', {'ndx_ids': ['cisco/a', 'cisco/b']}, format='json', **self.header
        )
        self.assertHttpStatus(response, status.HTTP_202_ACCEPTED)
        self.assertEqual(enqueue.call_args.kwargs['ndx_ids'], ['cisco/a', 'cisco/b'])
        self.assertEqual(response.data['name'], 'NDX Import')

    @patch('ndx.api.views.ImportJob.enqueue')
    def test_import_over_threshold(self, enqueue):
        enqueue.return_value = Job.objects.create(
            name='NDX Import', user=self.user, job_id='44444444-4444-4444-4444-444444444444'
        )
        ndx_ids = [f'cisco/model-{i}' for i in range(IMPORT_BACKGROUND_THRESHOLD + 1)]
        response = self.client.post(
            reverse('ndx-api:catalog-run-import'), {'ndx_ids': ndx_ids}, format='json', **self.header
        )
        self.assertHttpStatus(response, status.HTTP_202_ACCEPTED)
        self.assertEqual(enqueue.call_args.kwargs['ndx_ids'], ndx_ids)
        self.mock_client.get_entry.assert_not_called()

    def test_import_invalid_request(self):
        url = reverse('ndx-api:catalog-run-import')
        response = self.client.post(url, {'ndx_ids': []}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

    def test_read_only_token_cannot_import(self):
        self.token.write_enabled = False
        self.token.save()
        url = reverse('ndx-api:catalog-run-import')
        response = self.client.post(url, {'ndx_ids': ['cisco/a']}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_403_FORBIDDEN)

    def test_permission_required(self):
        self.remove_permissions('ndx.view_importrecord')
        response = self.client.get(reverse('ndx-api:catalog-list'), **self.header)
        self.assertHttpStatus(response, status.HTTP_403_FORBIDDEN)

    @override_settings(NDX_API_TOKEN=None)
    def test_disabled(self):
        response = self.client.get(reverse('ndx-api:catalog-list'), **self.header)
        self.assertHttpStatus(response, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.mock_client.search.assert_not_called()


@override_settings(NDX_API_TOKEN='token', ISOLATED_DEPLOYMENT=False)
class SyncTestCase(APITestCase):

    def setUp(self):
        super().setUp()
        self.add_permissions('ndx.view_importrecord')

    def test_status(self):
        create_test_records()
        ImportRecord.objects.filter(ndx_id='acme/model-1').update(update_available=True)
        Job.objects.create(
            name='NDX Catalog Sync', status='completed', data={'tier': 'paid'},
            job_id='22222222-2222-2222-2222-222222222222',
        )

        response = self.client.get(reverse('ndx-api:sync-list'), **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertTrue(response.data['enabled'])
        self.assertEqual(response.data['imported_count'], 3)
        self.assertEqual(response.data['updates_available'], 1)
        self.assertEqual(response.data['last_sync']['data'], {'tier': 'paid'})

    @patch('ndx.api.views.SyncJob.enqueue')
    def test_sync(self, enqueue):
        enqueue.side_effect = lambda **kwargs: Job.objects.create(
            name='NDX Catalog Sync', user=self.user, job_id='33333333-3333-3333-3333-333333333333'
        )
        response = self.client.post(reverse('ndx-api:sync-list'), **self.header)
        self.assertHttpStatus(response, status.HTTP_403_FORBIDDEN)

        self.add_permissions('ndx.sync_importrecord')
        response = self.client.post(reverse('ndx-api:sync-list'), **self.header)
        self.assertHttpStatus(response, status.HTTP_202_ACCEPTED)
        enqueue.assert_called_once()

        # The pending job is returned rather than queuing another
        job_id = response.data['id']
        response = self.client.post(reverse('ndx-api:sync-list'), **self.header)
        self.assertHttpStatus(response, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['id'], job_id)
        enqueue.assert_called_once()

    @override_settings(NDX_API_TOKEN=None)
    def test_sync_disabled(self):
        self.add_permissions('ndx.sync_importrecord')
        response = self.client.post(reverse('ndx-api:sync-list'), **self.header)
        self.assertHttpStatus(response, status.HTTP_503_SERVICE_UNAVAILABLE)
