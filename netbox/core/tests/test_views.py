import uuid
from datetime import datetime
from django.contrib.auth.models import User
from django.utils import timezone
from django_rq import get_queue
from django.test import override_settings
from django.test.client import Client
from django_rq.settings import QUEUES_MAP, QUEUES_LIST
from django_rq.workers import get_worker
from django.urls import reverse
from rq import get_current_job
from rq.job import Job as RQ_Job
from rq.registry import (
    DeferredJobRegistry,
    FailedJobRegistry,
    FinishedJobRegistry,
    ScheduledJobRegistry,
    StartedJobRegistry,
)

from utilities.testing import TestCase, ViewTestCases, create_tags

from ..models import *


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


def test_job_default():
    return 'TestNBJob'


def test_job_high():
    return 'TestNBJob'


class BackgroundTaskTestCase(TestCase):
    user_permissions = ()

    def setUp(self):
        super().setUp()
        self.user.is_staff = True
        self.user.is_active = True
        self.user.save()
        get_queue('default').connection.flushall()
        get_queue('high').connection.flushall()
        get_queue('low').connection.flushall()

    def test_background_queue_list(self):
        response = self.client.get(reverse('core:background_queue_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('default', str(response.content))
        self.assertIn('high', str(response.content))
        self.assertIn('low', str(response.content))

    def test_background_queue_list_no_perm(self):
        self.user.is_staff = False
        self.user.save()
        response = self.client.get(reverse('core:background_queue_list'))
        self.assertEqual(response.status_code, 403)
        self.user.is_staff = True
        self.user.save()

    def test_background_tasks_list_default(self):
        queue = get_queue('default')
        job = queue.enqueue(test_job_default)
        queue_index = QUEUES_MAP['default']

        response = self.client.get(reverse('core:background_task_list', args=[queue_index, 'queued']))
        self.assertEqual(response.status_code, 200)
        self.assertIn('core.tests.test_views.test_job_default', str(response.content))

    def test_background_tasks_list_high(self):
        queue = get_queue('high')
        job = queue.enqueue(test_job_high)
        queue_index = QUEUES_MAP['high']

        response = self.client.get(reverse('core:background_task_list', args=[queue_index, 'queued']))
        self.assertEqual(response.status_code, 200)
        self.assertIn('core.tests.test_views.test_job_high', str(response.content))

    def test_background_tasks_list_finished(self):
        queue = get_queue('default')
        job = queue.enqueue(test_job_default)
        queue_index = QUEUES_MAP['default']

        registry = FinishedJobRegistry(queue.name, queue.connection)
        registry.add(job, 2)
        response = self.client.get(reverse('core:background_task_list', args=[queue_index, 'finished']))
        self.assertIn('core.tests.test_views.test_job_default', str(response.content))

    def test_background_tasks_list_failed(self):
        queue = get_queue('default')
        job = queue.enqueue(test_job_default)
        queue_index = QUEUES_MAP['default']

        registry = FailedJobRegistry(queue.name, queue.connection)
        registry.add(job, 2)
        response = self.client.get(reverse('core:background_task_list', args=[queue_index, 'failed']))
        self.assertIn('core.tests.test_views.test_job_default', str(response.content))

    def test_background_tasks_scheduled(self):
        queue = get_queue('default')
        job = queue.enqueue_at(datetime.now(), test_job_default)
        queue_index = QUEUES_MAP['default']

        response = self.client.get(reverse('core:background_task_list', args=[queue_index, 'scheduled']))
        self.assertIn('core.tests.test_views.test_job_default', str(response.content))

    def test_background_tasks_list_deferred(self):
        queue = get_queue('default')
        job = queue.enqueue(test_job_default)
        queue_index = QUEUES_MAP['default']

        registry = DeferredJobRegistry(queue.name, queue.connection)
        registry.add(job, 2)
        response = self.client.get(reverse('core:background_task_list', args=[queue_index, 'deferred']))
        self.assertIn('core.tests.test_views.test_job_default', str(response.content))

    def test_background_task(self):
        queue = get_queue('default')
        job = queue.enqueue(test_job_default)
        queue_index = QUEUES_MAP['default']

        response = self.client.get(reverse('core:background_task', args=[job.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Background Tasks', str(response.content))
        self.assertIn(str(job.id), str(response.content))
        self.assertIn('Callable', str(response.content))
        self.assertIn('Meta', str(response.content))
        self.assertIn('Kwargs', str(response.content))

    def test_background_task_delete(self):
        queue = get_queue('default')
        job = queue.enqueue(test_job_default)
        queue_index = QUEUES_MAP['default']

        response = self.client.post(reverse('core:background_task_delete', args=[job.id]), {'confirm': True})
        self.assertFalse(RQ_Job.exists(job.id, connection=queue.connection))
        self.assertNotIn(job.id, queue.job_ids)

    def test_background_task_requeue(self):
        pass

    def test_background_task_enqueue(self):
        pass

    def test_background_task_stop(self):
        pass

    def test_worker_list(self):
        worker1 = get_worker('default', name=uuid.uuid4().hex)
        worker1.register_birth()

        worker2 = get_worker('high')
        worker2.register_birth()

        queue_index = QUEUES_MAP['default']
        response = self.client.get(reverse('core:worker_list', args=[queue_index]))
        self.assertIn(str(worker1.name), str(response.content))
        self.assertNotIn(str(worker2.name), str(response.content))

    def test_worker(self):
        worker1 = get_worker('default', name=uuid.uuid4().hex)
        worker1.register_birth()

        queue_index = QUEUES_MAP['default']
        response = self.client.get(reverse('core:worker', args=[worker1.name]))
        self.assertIn(str(worker1.name), str(response.content))
        self.assertIn('Birth', str(response.content))
        self.assertIn('Total working time (seconds)', str(response.content))
