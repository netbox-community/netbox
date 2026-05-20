import json
import urllib.parse
import uuid
from datetime import datetime
from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from django_rq import get_queue
from django_rq.settings import get_queues_map
from django_rq.workers import get_worker
from rq.job import Job as RQ_Job
from rq.job import JobStatus
from rq.registry import DeferredJobRegistry, FailedJobRegistry, FinishedJobRegistry, StartedJobRegistry

from core.choices import CorePluginStatusChoices, ObjectChangeActionChoices
from core.core_plugins import CORE_PLUGINS, get_core_plugins
from core.models import *
from core.plugins import Plugin
from dcim.models import Site
from users.models import User
from utilities.testing import TestCase, ViewTestCases, create_tags, disable_logging


class DataSourceTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = DataSource

    @classmethod
    def setUpTestData(cls):
        data_sources = (
            DataSource(name='Data Source 1', type='local', source_url='file:///var/tmp/source1/'),
            DataSource(name='Data Source 2', type='local', source_url='file:///var/tmp/source2/'),
            DataSource(name='Data Source 3', type='local', source_url='file:///var/tmp/source3/'),
        )
        DataSource.objects.bulk_create(data_sources)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Data Source X',
            'type': 'git',
            'source_url': 'http:///exmaple/com/foo/bar/',
            'description': 'Something',
            'comments': 'Foo bar baz',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,type,source_url,enabled",
            "Data Source 4,local,file:///var/tmp/source4/,true",
            "Data Source 5,local,file:///var/tmp/source4/,true",
            "Data Source 6,git,http:///exmaple/com/foo/bar/,false",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{data_sources[0].pk},Data Source 7,New description7",
            f"{data_sources[1].pk},Data Source 8,New description8",
            f"{data_sources[2].pk},Data Source 9,New description9",
        )

        cls.bulk_edit_data = {
            'enabled': False,
            'description': 'New description',
        }


class DataFileTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    model = DataFile

    @classmethod
    def setUpTestData(cls):
        datasource = DataSource.objects.create(
            name='Data Source 1',
            type='local',
            source_url='file:///var/tmp/source1/'
        )

        data_files = (
            DataFile(
                source=datasource,
                path='dir1/file1.txt',
                last_updated=timezone.now(),
                size=1000,
                hash='442da078f0111cbdf42f21903724f6597c692535f55bdfbbea758a1ae99ad9e1'
            ),
            DataFile(
                source=datasource,
                path='dir1/file2.txt',
                last_updated=timezone.now(),
                size=2000,
                hash='a78168c7c97115bafd96450ed03ea43acec495094c5caa28f0d02e20e3a76cc2'
            ),
            DataFile(
                source=datasource,
                path='dir1/file3.txt',
                last_updated=timezone.now(),
                size=3000,
                hash='12b8827a14c4d5a2f30b6c6e2b7983063988612391c6cbe8ee7493b59054827a'
            ),
        )
        DataFile.objects.bulk_create(data_files)


class JobTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    model = Job

    @classmethod
    def setUpTestData(cls):
        datasource = DataSource.objects.create(
            name='Data Source 1',
            type='local',
            source_url='file:///var/tmp/source1/',
        )
        ct = ContentType.objects.get_for_model(DataSource)
        Job.objects.bulk_create(
            [
                Job(
                    name='Job 1',
                    object_type=ct,
                    object_id=datasource.pk,
                    status='pending',
                    queue_name='default',
                    job_id=uuid.uuid4(),
                ),
                Job(
                    name='Job 2',
                    object_type=ct,
                    object_id=datasource.pk,
                    status='running',
                    queue_name='default',
                    job_id=uuid.uuid4(),
                ),
                Job(
                    name='Job 3',
                    object_type=ct,
                    object_id=datasource.pk,
                    status='completed',
                    queue_name='default',
                    job_id=uuid.uuid4(),
                ),
            ]
        )


# TODO: Convert to StandardTestCases.Views
class ObjectChangeTestCase(TestCase):
    user_permissions = (
        'core.view_objectchange',
    )

    @classmethod
    def setUpTestData(cls):

        site = Site(name='Site 1', slug='site-1')
        site.save()

        # Create three ObjectChanges
        user = User.objects.create_user(username='testuser2')
        for i in range(1, 4):
            oc = site.to_objectchange(action=ObjectChangeActionChoices.ACTION_UPDATE)
            oc.user = user
            oc.request_id = uuid.uuid4()
            oc.save()

    def test_objectchange_list(self):

        url = reverse('core:objectchange_list')
        params = {
            "user": User.objects.first().pk,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertHttpStatus(response, 200)

    def test_objectchange(self):

        objectchange = ObjectChange.objects.first()
        response = self.client.get(objectchange.get_absolute_url())
        self.assertHttpStatus(response, 200)


class BackgroundTaskTestCase(TestCase):
    user_permissions = ()

    # Dummy worker functions
    @staticmethod
    def dummy_job_default():
        return "Job finished"

    @staticmethod
    def dummy_job_high():
        return "Job finished"

    @staticmethod
    def dummy_job_failing():
        raise Exception("Job failed")

    def setUp(self):
        super().setUp()
        self.user.is_superuser = True
        self.user.is_active = True
        self.user.save()

        # Clear all queues prior to running each test
        get_queue('default').connection.flushall()
        get_queue('high').connection.flushall()
        get_queue('low').connection.flushall()

    def tearDown(self):
        super().tearDown()

        # Clear all queues after each test so no leftover jobs leak into the next test suite
        get_queue('default').connection.flushall()
        get_queue('high').connection.flushall()
        get_queue('low').connection.flushall()

    def test_background_queue_list(self):
        url = reverse('core:background_queue_list')

        # Attempt to load view without permission
        self.user.is_superuser = False
        self.user.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # Load view with permission
        self.user.is_superuser = True
        self.user.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('default', str(response.content))
        self.assertIn('high', str(response.content))
        self.assertIn('low', str(response.content))

    def test_background_tasks_list_default(self):
        queue = get_queue('default')
        queue.enqueue(self.dummy_job_default)
        queue_index = get_queues_map()['default']

        response = self.client.get(reverse('core:background_task_list', args=[queue_index, 'queued']))
        self.assertEqual(response.status_code, 200)
        self.assertIn('BackgroundTaskTestCase.dummy_job_default', str(response.content))

    def test_background_tasks_list_high(self):
        queue = get_queue('high')
        queue.enqueue(self.dummy_job_high)
        queue_index = get_queues_map()['high']

        response = self.client.get(reverse('core:background_task_list', args=[queue_index, 'queued']))
        self.assertEqual(response.status_code, 200)
        self.assertIn('BackgroundTaskTestCase.dummy_job_high', str(response.content))

    def test_background_tasks_list_finished(self):
        queue = get_queue('default')
        job = queue.enqueue(self.dummy_job_default)
        queue_index = get_queues_map()['default']

        registry = FinishedJobRegistry(queue.name, queue.connection)
        registry.add(job, 2)
        response = self.client.get(reverse('core:background_task_list', args=[queue_index, 'finished']))
        self.assertEqual(response.status_code, 200)
        self.assertIn('BackgroundTaskTestCase.dummy_job_default', str(response.content))

    def test_background_tasks_list_failed(self):
        queue = get_queue('default')
        job = queue.enqueue(self.dummy_job_default)
        queue_index = get_queues_map()['default']

        registry = FailedJobRegistry(queue.name, queue.connection)
        registry.add(job, 2)
        response = self.client.get(reverse('core:background_task_list', args=[queue_index, 'failed']))
        self.assertEqual(response.status_code, 200)
        self.assertIn('BackgroundTaskTestCase.dummy_job_default', str(response.content))

    def test_background_tasks_scheduled(self):
        queue = get_queue('default')
        queue.enqueue_at(datetime.now(), self.dummy_job_default)
        queue_index = get_queues_map()['default']

        response = self.client.get(reverse('core:background_task_list', args=[queue_index, 'scheduled']))
        self.assertEqual(response.status_code, 200)
        self.assertIn('BackgroundTaskTestCase.dummy_job_default', str(response.content))

    def test_background_tasks_list_deferred(self):
        queue = get_queue('default')
        job = queue.enqueue(self.dummy_job_default)
        queue_index = get_queues_map()['default']

        registry = DeferredJobRegistry(queue.name, queue.connection)
        registry.add(job, 2)
        response = self.client.get(reverse('core:background_task_list', args=[queue_index, 'deferred']))
        self.assertEqual(response.status_code, 200)
        self.assertIn('BackgroundTaskTestCase.dummy_job_default', str(response.content))

    def test_background_task(self):
        queue = get_queue('default')
        job = queue.enqueue(self.dummy_job_default)

        response = self.client.get(reverse('core:background_task', args=[job.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Background Tasks', str(response.content))
        self.assertIn(str(job.id), str(response.content))
        self.assertIn('Callable', str(response.content))
        self.assertIn('Meta', str(response.content))
        self.assertIn('Keyword Arguments', str(response.content))

    def test_background_task_delete(self):
        queue = get_queue('default')
        job = queue.enqueue(self.dummy_job_default)

        response = self.client.post(reverse('core:background_task_delete', args=[job.id]), {'confirm': True})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(RQ_Job.exists(job.id, connection=queue.connection))
        self.assertNotIn(job.id, queue.job_ids)

    def test_background_task_requeue(self):
        queue = get_queue('default')

        # Enqueue & run a job that will fail
        job = queue.enqueue(self.dummy_job_failing)
        worker = get_worker('default')
        with disable_logging():
            worker.work(burst=True)
        self.assertTrue(job.is_failed)

        # Re-enqueue the failed job and check that its status has been reset
        response = self.client.get(reverse('core:background_task_requeue', args=[job.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(job.is_failed)

    def test_background_task_enqueue(self):
        queue = get_queue('default')

        # Enqueue some jobs that each depends on its predecessor
        job = previous_job = None
        for _ in range(0, 3):
            job = queue.enqueue(self.dummy_job_default, depends_on=previous_job)
            previous_job = job

        # Check that the last job to be enqueued has a status of deferred
        self.assertIsNotNone(job)
        self.assertEqual(job.get_status(), JobStatus.DEFERRED)
        self.assertIsNone(job.enqueued_at)

        # Force-enqueue the deferred job
        response = self.client.get(reverse('core:background_task_enqueue', args=[job.id]))
        self.assertEqual(response.status_code, 302)

        # Check that job's status is updated correctly
        job = queue.fetch_job(job.id)
        self.assertEqual(job.get_status(), JobStatus.QUEUED)
        self.assertIsNotNone(job.enqueued_at)

    def test_background_task_stop(self):
        queue = get_queue('default')

        worker = get_worker('default')
        job = queue.enqueue(self.dummy_job_default)
        worker.prepare_job_execution(job)
        worker.prepare_execution(job)

        self.assertEqual(job.get_status(), JobStatus.STARTED)

        # Stop those jobs using the view
        started_job_registry = StartedJobRegistry(queue.name, connection=queue.connection)
        self.assertEqual(len(started_job_registry), 1)
        response = self.client.get(reverse('core:background_task_stop', args=[job.id]))
        self.assertEqual(response.status_code, 302)
        with disable_logging():
            worker.monitor_work_horse(job, queue)  # Sets the job as Failed and removes from Started
        self.assertEqual(len(started_job_registry), 0)

        canceled_job_registry = FailedJobRegistry(queue.name, connection=queue.connection)
        self.assertEqual(len(canceled_job_registry), 1)
        self.assertIn(job.id, canceled_job_registry)

    def test_worker_list(self):
        worker1 = get_worker('default', name=uuid.uuid4().hex)
        worker1.register_birth()

        worker2 = get_worker('high')
        worker2.register_birth()

        queue_index = get_queues_map()['default']
        response = self.client.get(reverse('core:worker_list', args=[queue_index]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(str(worker1.name), str(response.content))
        self.assertNotIn(str(worker2.name), str(response.content))

    def test_worker(self):
        worker1 = get_worker('default', name=uuid.uuid4().hex)
        worker1.register_birth()

        response = self.client.get(reverse('core:worker', args=[worker1.name]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(str(worker1.name), str(response.content))
        self.assertIn('Birth', str(response.content))
        self.assertIn('Total working time', str(response.content))


class SystemTestCase(TestCase):

    def setUp(self):
        super().setUp()

        self.user.is_superuser = True
        self.user.save()

    def test_system_view_default(self):
        # Test UI render
        response = self.client.get(reverse('core:system'))
        self.assertEqual(response.status_code, 200)

        # Test export
        response = self.client.get(f"{reverse('core:system')}?export=true")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('netbox_release', data)
        self.assertIn('plugins', data)
        self.assertIn('config', data)
        self.assertIn('objects', data)
        self.assertIn('db_schema', data)

    def test_system_view_with_config_revision(self):
        ConfigRevision.objects.create()

        # Test UI render
        response = self.client.get(reverse('core:system'))
        self.assertEqual(response.status_code, 200)

        # Test export
        response = self.client.get(f"{reverse('core:system')}?export=true")
        self.assertEqual(response.status_code, 200)


class PluginListViewTestCase(TestCase):
    """
    Tests for the Core Plugins section rendered on the plugins list page.
    """

    def setUp(self):
        super().setUp()

        self.user.is_superuser = True
        self.user.save()
        # The plugin catalog feed is cached process-wide; clear it so the patched
        # catalog fetch is honored on every request.
        cache.delete('plugins-catalog-feed')
        cache.delete('plugins-catalog-error')

    def _set_commercial_features(self, enabled):
        # settings.RELEASE is a dataclass loaded at startup; mutate the field in
        # place and restore on teardown.
        from django.conf import settings
        original = settings.RELEASE.features.commercial
        settings.RELEASE.features.commercial = enabled
        self.addCleanup(setattr, settings.RELEASE.features, 'commercial', original)

    @patch('core.views.get_catalog_plugins', return_value={})
    def test_plugin_list_shows_core_section_locked_for_oss(self, _mock_catalog):
        self._set_commercial_features(False)

        response = self.client.get(reverse('core:plugin_list'))

        self.assertEqual(response.status_code, 200)
        core_plugins = response.context['core_plugins']
        self.assertEqual(len(core_plugins), len(CORE_PLUGINS))

        # Commercial plugins should be Locked in OSS; non-commercial plugins should
        # appear as Available.
        status_by_name = {entry['config_name']: entry['status'] for entry in core_plugins}
        for plugin in CORE_PLUGINS:
            expected = (
                CorePluginStatusChoices.STATUS_LOCKED if plugin.commercial
                else CorePluginStatusChoices.STATUS_AVAILABLE
            )
            self.assertEqual(status_by_name[plugin.config_name], expected)

        # The Core Plugins heading and at least one product link should render.
        self.assertContains(response, 'Core Plugins')
        first_commercial = next(p for p in CORE_PLUGINS if p.commercial)
        self.assertContains(response, first_commercial.product_url)

    @patch('core.views.get_catalog_plugins', return_value={})
    def test_plugin_list_shows_core_section_available_for_commercial(self, _mock_catalog):
        self._set_commercial_features(True)

        response = self.client.get(reverse('core:plugin_list'))

        self.assertEqual(response.status_code, 200)
        for entry in response.context['core_plugins']:
            self.assertEqual(entry['status'], CorePluginStatusChoices.STATUS_AVAILABLE)

    def test_get_core_plugins_marks_installed(self):
        # Unit-level test: simulate a locally-installed core plugin and confirm
        # the helper reports it as installed with the recorded version.
        target = CORE_PLUGINS[0]
        local_plugins = {
            target.config_name: Plugin(
                config_name=target.config_name,
                title_short=str(target.title),
                title_long=str(target.title),
                is_local=True,
                is_loaded=True,
                installed_version='1.2.3',
            ),
        }

        self._set_commercial_features(False)
        entries = get_core_plugins(local_plugins)
        installed = next(e for e in entries if e['config_name'] == target.config_name)

        self.assertEqual(installed['status'], CorePluginStatusChoices.STATUS_INSTALLED)
        self.assertEqual(installed['installed_version'], '1.2.3')

    @patch('core.views.get_catalog_plugins')
    def test_plugin_list_excludes_core_from_community_list(self, mock_catalog):
        # Seed the "catalog" with one of the core plugins plus a community plugin,
        # and verify only the community plugin reaches the catalog table.
        target = CORE_PLUGINS[0]
        mock_catalog.return_value = {
            target.config_name: Plugin(
                config_name=target.config_name,
                title_short=str(target.title),
                title_long=str(target.title),
            ),
            'some_community_plugin': Plugin(
                config_name='some_community_plugin',
                title_short='Community Plugin',
                title_long='Community Plugin',
            ),
        }
        self._set_commercial_features(False)

        response = self.client.get(reverse('core:plugin_list'))

        self.assertEqual(response.status_code, 200)
        table_rows = list(response.context['table'].rows)
        row_names = {row.record.config_name for row in table_rows}
        self.assertIn('some_community_plugin', row_names)
        self.assertNotIn(target.config_name, row_names)
