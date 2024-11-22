import uuid

from django_rq import get_queue
from django_rq.workers import get_worker
from django.urls import reverse
from django.utils import timezone
from rq.job import Job as RQ_Job, JobStatus
from rq.registry import FailedJobRegistry, StartedJobRegistry

from users.models import Token, User
from utilities.testing import APITestCase, APIViewTestCases, TestCase
from ..models import *


class AppTest(APITestCase):

    def test_root(self):
        url = reverse('core-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class DataSourceTest(APIViewTestCases.APIViewTestCase):
    model = DataSource
    brief_fields = ['description', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'enabled': False,
        'description': 'foo bar baz',
    }

    @classmethod
    def setUpTestData(cls):
        data_sources = (
            DataSource(name='Data Source 1', type='local', source_url='file:///var/tmp/source1/'),
            DataSource(name='Data Source 2', type='local', source_url='file:///var/tmp/source2/'),
            DataSource(name='Data Source 3', type='local', source_url='file:///var/tmp/source3/'),
        )
        DataSource.objects.bulk_create(data_sources)

        cls.create_data = [
            {
                'name': 'Data Source 4',
                'type': 'git',
                'source_url': 'https://example.com/git/source4'
            },
            {
                'name': 'Data Source 5',
                'type': 'git',
                'source_url': 'https://example.com/git/source5'
            },
            {
                'name': 'Data Source 6',
                'type': 'git',
                'source_url': 'https://example.com/git/source6'
            },
        ]


class DataFileTest(
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.GraphQLTestCase
):
    model = DataFile
    brief_fields = ['display', 'id', 'path', 'url']
    user_permissions = ('core.view_datasource', )

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


class BackgroundTaskTestCase(TestCase):
    user_permissions = ()

    @staticmethod
    def dummy_job_default():
        return "Job finished"

    @staticmethod
    def dummy_job_failing():
        raise Exception("Job failed")

    def setUp(self):
        """
        Create a user and token for API calls.
        """
        # Create the test user and assign permissions
        self.user = User.objects.create_user(username='testuser')
        self.user.is_staff = True
        self.user.is_active = True
        self.user.save()
        self.token = Token.objects.create(user=self.user)
        self.header = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

        # Clear all queues prior to running each test
        get_queue('default').connection.flushall()
        get_queue('high').connection.flushall()
        get_queue('low').connection.flushall()

    def test_background_queue_list(self):
        url = reverse('core-api:rqqueue-list')

        # Attempt to load view without permission
        self.user.is_staff = False
        self.user.save()
        response = self.client.get(url, **self.header)
        self.assertEqual(response.status_code, 403)

        # Load view with permission
        self.user.is_staff = True
        self.user.save()
        response = self.client.get(url, **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertIn('default', str(response.content))
        self.assertIn('high', str(response.content))
        self.assertIn('low', str(response.content))

    def test_background_queue(self):
        response = self.client.get(reverse('core-api:rqqueue-detail', args=['default']), **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertIn('default', str(response.content))
        self.assertIn('oldest_job_timestamp', str(response.content))
        self.assertIn('scheduled_jobs', str(response.content))

    def test_background_task_list(self):
        queue = get_queue('default')
        queue.enqueue(self.dummy_job_default)

        response = self.client.get(reverse('core-api:rqtask-list'), **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertIn('origin', str(response.content))
        self.assertIn('core.tests.test_api.BackgroundTaskTestCase.dummy_job_default()', str(response.content))

    def test_background_task(self):
        queue = get_queue('default')
        job = queue.enqueue(self.dummy_job_default)

        response = self.client.get(reverse('core-api:rqtask-detail', args=[job.id]), **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertIn(str(job.id), str(response.content))
        self.assertIn('origin', str(response.content))
        self.assertIn('meta', str(response.content))
        self.assertIn('kwargs', str(response.content))

    def test_background_task_delete(self):
        queue = get_queue('default')
        job = queue.enqueue(self.dummy_job_default)

        response = self.client.post(reverse('core-api:rqtask-delete', args=[job.id]), **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(RQ_Job.exists(job.id, connection=queue.connection))
        queue = get_queue('default')
        self.assertNotIn(job.id, queue.job_ids)

    def test_background_task_requeue(self):
        queue = get_queue('default')

        # Enqueue & run a job that will fail
        job = queue.enqueue(self.dummy_job_failing)
        worker = get_worker('default')
        worker.work(burst=True)
        self.assertTrue(job.is_failed)

        # Re-enqueue the failed job and check that its status has been reset
        response = self.client.post(reverse('core-api:rqtask-requeue', args=[job.id]), **self.header)
        self.assertEqual(response.status_code, 200)
        job = RQ_Job.fetch(job.id, queue.connection)
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
        response = self.client.post(reverse('core-api:rqtask-enqueue', args=[job.id]), **self.header)
        self.assertEqual(response.status_code, 200)

        # Check that job's status is updated correctly
        job = queue.fetch_job(job.id)
        self.assertEqual(job.get_status(), JobStatus.QUEUED)
        self.assertIsNotNone(job.enqueued_at)

    def test_background_task_stop(self):
        queue = get_queue('default')

        worker = get_worker('default')
        job = queue.enqueue(self.dummy_job_default)
        worker.prepare_job_execution(job)

        self.assertEqual(job.get_status(), JobStatus.STARTED)
        response = self.client.post(reverse('core-api:rqtask-stop', args=[job.id]), **self.header)
        self.assertEqual(response.status_code, 200)
        worker.monitor_work_horse(job, queue)  # Sets the job as Failed and removes from Started
        started_job_registry = StartedJobRegistry(queue.name, connection=queue.connection)
        self.assertEqual(len(started_job_registry), 0)

        canceled_job_registry = FailedJobRegistry(queue.name, connection=queue.connection)
        self.assertEqual(len(canceled_job_registry), 1)
        self.assertIn(job.id, canceled_job_registry)

    def test_worker_list(self):
        worker1 = get_worker('default', name=uuid.uuid4().hex)
        worker1.register_birth()

        worker2 = get_worker('high')
        worker2.register_birth()

        response = self.client.get(reverse('core-api:rqworker-list'), **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertIn(str(worker1.name), str(response.content))

    def test_worker(self):
        worker1 = get_worker('default', name=uuid.uuid4().hex)
        worker1.register_birth()

        response = self.client.get(reverse('core-api:rqworker-detail', args=[worker1.name]), **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertIn(str(worker1.name), str(response.content))
        self.assertIn('birth_date', str(response.content))
        self.assertIn('total_working_time', str(response.content))
