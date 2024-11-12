from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django_rq import get_queue

from ..jobs import *
from core.models import DataSource, Job
from core.choices import JobStatusChoices


class TestJobRunner(JobRunner):
    def run(self, *args, **kwargs):
        pass


class JobRunnerTestCase(TestCase):
    def tearDown(self):
        super().tearDown()

        # Clear all queues after running each test
        get_queue('default').connection.flushall()
        get_queue('high').connection.flushall()
        get_queue('low').connection.flushall()

    @staticmethod
    def get_schedule_at(offset=1):
        # Schedule jobs a week in advance to avoid accidentally running jobs on worker nodes used for testing.
        return timezone.now() + timedelta(weeks=offset)


class JobRunnerTest(JobRunnerTestCase):
    """
    Test internal logic of `JobRunner`.
    """

    def test_name_default(self):
        self.assertEqual(TestJobRunner.name, TestJobRunner.__name__)

    def test_name_set(self):
        class NamedJobRunner(TestJobRunner):
            class Meta:
                name = 'TestName'

        self.assertEqual(NamedJobRunner.name, 'TestName')

    def test_handle(self):
        job = TestJobRunner.enqueue(immediate=True)

        self.assertEqual(job.status, JobStatusChoices.STATUS_COMPLETED)

    def test_handle_errored(self):
        class ErroredJobRunner(TestJobRunner):
            EXP = Exception('Test error')

            def run(self, *args, **kwargs):
                raise self.EXP

        job = ErroredJobRunner.enqueue(immediate=True)

        self.assertEqual(job.status, JobStatusChoices.STATUS_ERRORED)
        self.assertEqual(job.error, repr(ErroredJobRunner.EXP))


class EnqueueTest(JobRunnerTestCase):
    """
    Test enqueuing of `JobRunner`.
    """

    def test_enqueue(self):
        instance = DataSource()
        for i in range(1, 3):
            job = TestJobRunner.enqueue(instance, schedule_at=self.get_schedule_at())

            self.assertIsInstance(job, Job)
            self.assertEqual(TestJobRunner.get_jobs(instance).count(), i)

    def test_enqueue_once(self):
        job = TestJobRunner.enqueue_once(instance=DataSource(), schedule_at=self.get_schedule_at())

        self.assertIsInstance(job, Job)
        self.assertEqual(job.name, TestJobRunner.__name__)

    def test_enqueue_once_twice_same(self):
        instance = DataSource()
        schedule_at = self.get_schedule_at()
        job1 = TestJobRunner.enqueue_once(instance, schedule_at=schedule_at)
        job2 = TestJobRunner.enqueue_once(instance, schedule_at=schedule_at)

        self.assertEqual(job1, job2)
        self.assertEqual(TestJobRunner.get_jobs(instance).count(), 1)

    def test_enqueue_once_twice_different_schedule_at(self):
        instance = DataSource()
        job1 = TestJobRunner.enqueue_once(instance, schedule_at=self.get_schedule_at())
        job2 = TestJobRunner.enqueue_once(instance, schedule_at=self.get_schedule_at(2))

        self.assertNotEqual(job1, job2)
        self.assertRaises(Job.DoesNotExist, job1.refresh_from_db)
        self.assertEqual(TestJobRunner.get_jobs(instance).count(), 1)

    def test_enqueue_once_twice_different_interval(self):
        instance = DataSource()
        schedule_at = self.get_schedule_at()
        job1 = TestJobRunner.enqueue_once(instance, schedule_at=schedule_at)
        job2 = TestJobRunner.enqueue_once(instance, schedule_at=schedule_at, interval=60)

        self.assertNotEqual(job1, job2)
        self.assertEqual(job1.interval, None)
        self.assertEqual(job2.interval, 60)
        self.assertRaises(Job.DoesNotExist, job1.refresh_from_db)
        self.assertEqual(TestJobRunner.get_jobs(instance).count(), 1)

    def test_enqueue_once_with_enqueue(self):
        instance = DataSource()
        job1 = TestJobRunner.enqueue_once(instance, schedule_at=self.get_schedule_at(2))
        job2 = TestJobRunner.enqueue(instance, schedule_at=self.get_schedule_at())

        self.assertNotEqual(job1, job2)
        self.assertEqual(TestJobRunner.get_jobs(instance).count(), 2)

    def test_enqueue_once_after_enqueue(self):
        instance = DataSource()
        job1 = TestJobRunner.enqueue(instance, schedule_at=self.get_schedule_at())
        job2 = TestJobRunner.enqueue_once(instance, schedule_at=self.get_schedule_at(2))

        self.assertNotEqual(job1, job2)
        self.assertRaises(Job.DoesNotExist, job1.refresh_from_db)
        self.assertEqual(TestJobRunner.get_jobs(instance).count(), 1)
