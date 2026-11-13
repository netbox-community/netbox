import uuid
from unittest.mock import MagicMock, patch

from django.test import override_settings
from django.utils import timezone

from core.choices import JobStatusChoices, ObjectChangeActionChoices
from core.exceptions import JobFailed
from core.models import Job, ObjectChange
from dcim.models import DeviceType, Manufacturer
from ndx.jobs import ImportJob, SyncJob, get_last_sync_job, register_sync_job, sync_catalog
from ndx.models import ImportRecord
from netbox.registry import registry
from utilities.request import NetBoxFakeRequest
from utilities.testing import TestCase

from .utils import (
    create_import_record,
    mock_auth_response,
    mock_entry,
    mock_error_response,
    mock_manifest_response,
)


def make_runner(job_class, user=None):
    job = Job.objects.create(name=job_class.name, user=user, job_id='00000000-0000-0000-0000-000000000000')
    return job_class(job)


@override_settings(NDX_API_TOKEN='token', ISOLATED_DEPLOYMENT=False)
class SyncJobTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        device_types = [
            DeviceType.objects.create(manufacturer=manufacturer, model=f'Model {i}', slug=f'model-{i}')
            for i in range(1, 5)
        ]
        create_import_record(device_types[0], 'cisco/model-1', checksum='current')
        create_import_record(device_types[1], 'cisco/model-2', checksum='old')
        create_import_record(device_types[2], 'juniper/model-3', checksum='old', update_available=True)
        create_import_record(device_types[3], 'arista/model-4', checksum='old', update_available=True)

    def get_client(self, checksums):
        client = MagicMock()
        client.verify_auth.return_value = mock_auth_response('paid')
        client.get_manifest.return_value = mock_manifest_response(checksums)
        client.check_sync.return_value = {'total_count': 50000}
        return client

    @patch('ndx.jobs.get_client')
    def test_sync(self, get_client):
        get_client.return_value = self.get_client({'cisco': 'current', 'juniper': 'old'})
        runner = make_runner(SyncJob)
        runner.run()

        flags = dict(ImportRecord.objects.values_list('ndx_id', 'update_available'))
        self.assertEqual(flags, {
            'cisco/model-1': False,
            'cisco/model-2': True,
            # Checksum now matches
            'juniper/model-3': False,
            # Vendor absent from the manifest
            'arista/model-4': False,
        })
        self.assertEqual(runner.job.data, {
            'tier': 'paid',
            'catalog_count': 50000,
            'imported_count': 4,
            'updates_available': 1,
            'flagged': 1,
            'cleared': 2,
        })

    @patch('ndx.jobs.get_client')
    def test_sync_auth_failure(self, get_client):
        client = self.get_client({'cisco': 'new'})
        client.verify_auth.return_value = mock_error_response(401)
        get_client.return_value = client

        runner = make_runner(SyncJob)
        with self.assertRaises(JobFailed):
            runner.run()
        self.assertEqual(ImportRecord.objects.filter(update_available=True).count(), 2)
        # The reason is recorded for display
        self.assertIn('HTTP 401', runner.job.data['error'])

    def test_sync_vendor(self):
        result = sync_catalog(self.get_client({'cisco': 'current', 'juniper': 'old'}), vendor='juniper')
        flags = dict(ImportRecord.objects.values_list('ndx_id', 'update_available'))
        self.assertEqual(flags, {
            'cisco/model-1': False,
            # Not synced
            'cisco/model-2': False,
            'juniper/model-3': False,
            'arista/model-4': True,
        })
        self.assertEqual(result['imported_count'], 1)
        self.assertEqual(result['cleared'], 1)

    def test_sync_blank_checksum(self):
        # A record imported without a checksum can't be compared, so it isn't flagged (and an existing flag is cleared)
        ImportRecord.objects.filter(ndx_id='cisco/model-2').update(checksum='')
        ImportRecord.objects.filter(ndx_id='juniper/model-3').update(checksum='')
        sync_catalog(self.get_client({'cisco': 'current', 'juniper': 'new'}))
        flags = dict(ImportRecord.objects.values_list('ndx_id', 'update_available'))
        self.assertFalse(flags['cisco/model-2'])
        self.assertFalse(flags['juniper/model-3'])

    def test_get_last_sync_job(self):
        Job.objects.create(name=SyncJob.name, status='completed', completed=timezone.now(), data=None,
                           job_id=uuid.uuid4())
        full = Job.objects.create(name=SyncJob.name, status='completed', completed=timezone.now(),
                                  data={'tier': 'free'}, job_id=uuid.uuid4())
        # A sync limited to one vendor is ignored
        Job.objects.create(name=SyncJob.name, status='completed', completed=timezone.now(),
                           data={'tier': 'free', 'vendor': 'cisco'}, job_id=uuid.uuid4())
        self.assertEqual(get_last_sync_job(), full)
        full.delete()
        self.assertIsNotNone(get_last_sync_job())

    @patch('ndx.jobs.get_client')
    def test_sync_without_checksums(self, get_client):
        get_client.return_value = self.get_client({})
        with self.assertRaises(JobFailed):
            make_runner(SyncJob).run()
        self.assertEqual(ImportRecord.objects.filter(update_available=True).count(), 2)

    @override_settings(NDX_API_TOKEN=None)
    @patch('ndx.jobs.get_client')
    def test_sync_disabled(self, get_client):
        make_runner(SyncJob).run()
        get_client.assert_not_called()

    def test_register_sync_job(self):
        system_jobs = dict(registry['system_jobs'])
        self.addCleanup(lambda: (registry['system_jobs'].clear(), registry['system_jobs'].update(system_jobs)))
        registry['system_jobs'].pop(SyncJob, None)

        with override_settings(NDX_SYNC_INTERVAL=0):
            register_sync_job()
        self.assertNotIn(SyncJob, registry['system_jobs'])

        with override_settings(NDX_SYNC_INTERVAL=60):
            register_sync_job()
        self.assertEqual(registry['system_jobs'][SyncJob], {'interval': 60})


class ImportJobTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.user.is_superuser = True
        self.user.save()

    @patch('ndx.importers.get_client')
    def test_import_job(self, get_client):
        client = MagicMock()
        client.get_manifest.return_value = mock_manifest_response({'cisco': 'abc123'})
        client.get_entry.side_effect = [mock_entry(), mock_error_response(404)]
        client.get_image.return_value = None
        get_client.return_value = client

        request = NetBoxFakeRequest({
            'META': {}, 'COOKIES': {}, 'POST': {}, 'GET': {}, 'FILES': {}, 'user': self.user, 'method': 'POST',
            'path': '/ndx/catalog/import/', 'id': '11111111-1111-1111-1111-111111111111',
        })
        runner = make_runner(ImportJob, user=self.user)
        runner.run(ndx_ids=['cisco/catalyst-9300', 'cisco/missing'], request=request)

        # Results are saved as each entry completes
        runner.job.refresh_from_db()
        results = runner.job.data['results']
        self.assertEqual(results[0]['status'], 'created')
        self.assertEqual(results[0]['object_type'], 'dcim.devicetype')
        self.assertEqual(results[1]['status'], 'failed')

        # Changes are logged and attributed to the requesting user
        device_type = DeviceType.objects.get()
        objectchange = ObjectChange.objects.get(changed_object_type__model='devicetype')
        self.assertEqual(objectchange.changed_object_id, device_type.pk)
        self.assertEqual(objectchange.action, ObjectChangeActionChoices.ACTION_CREATE)
        self.assertEqual(objectchange.user, self.user)
        self.assertTrue(ObjectChange.objects.filter(changed_object_type__model='importrecord').exists())

    @override_settings(RQ_DEFAULT_TIMEOUT=300)
    @patch('ndx.jobs.ImportJob.enqueue')
    def test_enqueue_timeout(self, enqueue):
        request = MagicMock(user=self.user)
        with patch('ndx.jobs.copy_safe_request'):
            ImportJob.enqueue_for(request, ['cisco/a'])
            self.assertEqual(enqueue.call_args.kwargs['job_timeout'], 300)
            ImportJob.enqueue_for(request, [f'cisco/{i}' for i in range(10)])
            self.assertEqual(enqueue.call_args.kwargs['job_timeout'], 1200)

    def test_import_job_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        runner = make_runner(ImportJob, user=self.user)
        with self.assertRaises(JobFailed):
            runner.run(ndx_ids=['cisco/catalyst-9300'], request=MagicMock())
        self.assertEqual(runner.job.status, JobStatusChoices.STATUS_PENDING)
