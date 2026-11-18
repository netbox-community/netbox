from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import CommandError, call_command
from django.test import TestCase, override_settings

from core.choices import JobStatusChoices
from core.models import Job, ObjectChange
from dcim.models import DeviceType, Manufacturer
from ndx.jobs import SyncJob
from ndx.models import ImportRecord
from users.models import User

from .utils import (
    create_import_record,
    mock_auth_response,
    mock_entry,
    mock_error_response,
    mock_manifest_response,
)


@override_settings(NDX_API_TOKEN='token', ISOLATED_DEPLOYMENT=False)
class NDXSyncCommandTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Cisco', slug='cisco')
        cls.device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Catalyst 9300', slug='catalyst-9300'
        )
        create_import_record(cls.device_type, 'cisco/catalyst-9300', checksum='old')
        cls.user = User.objects.create(username='admin', is_superuser=True)

    def setUp(self):
        self.client = MagicMock()
        self.client.verify_auth.return_value = mock_auth_response('paid')
        self.client.get_manifest.return_value = mock_manifest_response({'cisco': 'new'})
        self.client.check_sync.return_value = {'total_count': 50000}
        self.client.get_entry.return_value = mock_entry(model='Catalyst 9300')
        self.client.get_image.return_value = None
        for target in ('ndx.jobs.get_client', 'ndx.importers.get_client'):
            patcher = patch(target, return_value=self.client)
            patcher.start()
            self.addCleanup(patcher.stop)

    def call(self, *args):
        stdout = StringIO()
        call_command('ndx_sync', *args, stdout=stdout)
        return stdout.getvalue()

    def test_sync(self):
        output = self.call()
        self.assertIn('1 record(s) flagged for update', output)
        self.assertTrue(ImportRecord.objects.get().update_available)
        self.client.get_entry.assert_not_called()

        # The sync is recorded as a job
        job = Job.objects.get(name=SyncJob.name)
        self.assertEqual(job.status, JobStatusChoices.STATUS_COMPLETED)
        self.assertEqual(job.data['flagged'], 1)

    def test_sync_vendor(self):
        self.call('--vendor', 'juniper')
        self.assertFalse(ImportRecord.objects.get().update_available)
        self.assertEqual(Job.objects.get(name=SyncJob.name).data['vendor'], 'juniper')

    def test_apply(self):
        output = self.call('--apply', '--user', 'admin')
        self.assertIn('1 updated', output)
        record = ImportRecord.objects.get()
        self.assertFalse(record.update_available)
        self.assertEqual(record.checksum, 'new')
        self.assertTrue(ObjectChange.objects.filter(user=self.user, changed_object_id=self.device_type.pk).exists())

    def test_apply_requires_user(self):
        with self.assertRaises(CommandError):
            self.call('--apply')
        with self.assertRaises(CommandError):
            self.call('--apply', '--user', 'nobody')
        self.client.verify_auth.assert_not_called()

    def test_sync_failure(self):
        self.client.verify_auth.return_value = mock_error_response(401)
        with self.assertRaisesMessage(CommandError, 'HTTP 401'):
            self.call()
        self.assertEqual(Job.objects.get(name=SyncJob.name).status, JobStatusChoices.STATUS_FAILED)

    @override_settings(NDX_API_TOKEN=None)
    def test_disabled(self):
        with self.assertRaises(CommandError):
            self.call()
