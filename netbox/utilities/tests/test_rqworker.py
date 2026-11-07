import logging
import uuid
from datetime import timedelta
from unittest.mock import MagicMock, PropertyMock, patch

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.utils import timezone
from django_rq import get_queue
from rq.job import JobStatus as RQJobStatus
from rq.results import Result

from core.choices import JobStatusChoices
from core.models import Job
from netbox.jobs import JobRunner
from utilities.rqworker import (
    NetBoxRQWorker,
    any_workers_for_queue,
    get_all_workers,
    get_workers_for_queue,
)
from utilities.testing.mixins import RQQueueTestMixin


class DummyJobRunner(JobRunner):

    def run(self, *args, **kwargs):
        pass


def _make_worker(name='worker-1', queues=('default',)):
    """
    Build a MagicMock that mimics the rq.Worker attributes consumed by
    get_workers_for_queue() / any_workers_for_queue().

    Heartbeat freshness is intentionally not modeled here: liveness is
    enforced by RQ itself (Worker.all() / find_by_key() only return workers
    whose Redis hash has not expired), so any worker reaching our code is
    already known-fresh.
    """
    worker = MagicMock()
    worker.name = name
    worker.queue_names.return_value = list(queues)
    return worker


class NetBoxRQWorkerHeartbeatTestCase(TestCase):
    """
    The overridden heartbeat() must call register_birth() iff the worker is
    missing from the rq:workers registry set, and must always invoke
    super().heartbeat().
    """

    def setUp(self):
        super().setUp()
        # These tests exercise the recovery branches, which log a "re-registering" warning (and,
        # for the Redis-failure case, an exception traceback). Mute the logger so the expected
        # messages don't clutter the test runner's output.
        logger = logging.getLogger('netbox.rqworker')
        original_level = logger.level
        logger.setLevel(logging.CRITICAL)
        self.addCleanup(logger.setLevel, original_level)

    def _make_subject(self, is_member, hash_exists=False, marked_dead=False):
        worker = NetBoxRQWorker.__new__(NetBoxRQWorker)
        worker.name = 'test-worker'
        worker.connection = MagicMock()
        worker.connection.sismember.return_value = is_member
        worker.connection.exists.return_value = hash_exists
        worker.connection.hexists.return_value = marked_dead
        worker.register_birth = MagicMock()
        worker.log = MagicMock()
        return worker

    def test_heartbeat_skips_register_when_present(self):
        worker = self._make_subject(is_member=True)
        with patch('rq.Worker.heartbeat') as super_heartbeat:
            NetBoxRQWorker.heartbeat(worker)
        worker.register_birth.assert_not_called()
        super_heartbeat.assert_called_once()

    def test_heartbeat_calls_register_birth_when_hash_missing(self):
        # Full data loss: set membership and hash both gone.
        worker = self._make_subject(is_member=False, hash_exists=False)
        with patch('rq.Worker.heartbeat') as super_heartbeat, \
                patch('utilities.rqworker.register_worker') as register_set:
            NetBoxRQWorker.heartbeat(worker)
        worker.register_birth.assert_called_once()
        register_set.assert_not_called()
        super_heartbeat.assert_called_once()

    def test_heartbeat_readds_to_set_when_hash_survives(self):
        # Partial data loss: hash present (and not dead), set membership gone.
        # register_birth() would raise here; we must re-add to the set instead.
        worker = self._make_subject(is_member=False, hash_exists=True, marked_dead=False)
        with patch('rq.Worker.heartbeat') as super_heartbeat, \
                patch('utilities.rqworker.register_worker') as register_set:
            NetBoxRQWorker.heartbeat(worker)
        worker.register_birth.assert_not_called()
        register_set.assert_called_once_with(worker, worker.connection)
        # Liveness is gated on the 'death' hash field specifically; pin the
        # field name so a typo can't silently fall through to register_birth().
        worker.connection.hexists.assert_called_with(worker.key, 'death')
        super_heartbeat.assert_called_once()

    def test_heartbeat_calls_register_birth_when_hash_marked_dead(self):
        # Hash exists but is marked dead -- treat as full recreate.
        worker = self._make_subject(is_member=False, hash_exists=True, marked_dead=True)
        with patch('rq.Worker.heartbeat') as super_heartbeat, \
                patch('utilities.rqworker.register_worker') as register_set:
            NetBoxRQWorker.heartbeat(worker)
        worker.register_birth.assert_called_once()
        register_set.assert_not_called()
        super_heartbeat.assert_called_once()

    def test_registration_check_exception_still_delegates_to_super_heartbeat(self):
        # A Redis failure in the registration-check branch (sismember) must
        # not abort the heartbeat; the parent heartbeat must still be invoked
        # (whether it then succeeds against a degraded Redis is rq's concern,
        # not ours -- we patch it out here to isolate our wrapper's behavior).
        worker = self._make_subject(is_member=False)
        worker.connection.sismember.side_effect = RuntimeError('redis down')
        with patch('rq.Worker.heartbeat') as super_heartbeat:
            # Must not raise
            NetBoxRQWorker.heartbeat(worker)
        worker.register_birth.assert_not_called()
        super_heartbeat.assert_called_once()


class NetBoxRQWorkerBootstrapTestCase(TestCase):
    """
    The overridden bootstrap() must load the URLconf and then close any
    database connections before invoking super().bootstrap(), so that forked
    work horses inherit the URLconf but no open connections.
    """

    def _make_resolver(self, side_effect=None):
        resolver = MagicMock()
        url_patterns = PropertyMock(side_effect=side_effect)
        type(resolver).url_patterns = url_patterns
        return resolver, url_patterns

    def test_bootstrap_loads_urlconf_and_resets_connections_before_super(self):
        worker = NetBoxRQWorker.__new__(NetBoxRQWorker)
        calls = []
        resolver, _ = self._make_resolver(side_effect=lambda: calls.append('load_urlconf'))
        with patch('utilities.rqworker.get_resolver', return_value=resolver), \
                patch('utilities.rqworker.reset_db_connections') as reset_db_connections, \
                patch('rq.Worker.bootstrap') as super_bootstrap:
            reset_db_connections.side_effect = lambda: calls.append('reset_db_connections')
            super_bootstrap.side_effect = lambda *args, **kwargs: calls.append('super_bootstrap')
            NetBoxRQWorker.bootstrap(worker, 'DEBUG', date_format='%H')
        self.assertEqual(calls, ['load_urlconf', 'reset_db_connections', 'super_bootstrap'])
        super_bootstrap.assert_called_once_with('DEBUG', date_format='%H')

    def test_bootstrap_urlconf_error_aborts_before_registration(self):
        worker = NetBoxRQWorker.__new__(NetBoxRQWorker)
        resolver, _ = self._make_resolver(side_effect=ImproperlyConfigured('broken schema'))
        with patch('utilities.rqworker.get_resolver', return_value=resolver), \
                patch('utilities.rqworker.reset_db_connections'), \
                patch('rq.Worker.bootstrap') as super_bootstrap:
            with self.assertRaises(ImproperlyConfigured):
                NetBoxRQWorker.bootstrap(worker)
        super_bootstrap.assert_not_called()


class GetWorkersForQueueTestCase(TestCase):
    """
    get_workers_for_queue() must:
      * count workers servicing the queue (RQ filters by liveness for us)
      * exclude workers not listening on the requested queue
      * return 0 when no workers exist
    """

    def _patch_worker_all(self, workers):
        return patch('utilities.rqworker.Worker.all', return_value=workers)

    def _patch_get_connection(self):
        return patch('utilities.rqworker.get_connection', return_value=MagicMock())

    def test_returns_worker_for_queue(self):
        workers = [_make_worker(name='alive')]
        with self._patch_get_connection(), self._patch_worker_all(workers):
            result = get_workers_for_queue('default')
        self.assertEqual(result, 1)

    def test_excludes_worker_for_other_queue(self):
        workers = [_make_worker(name='other', queues=('high',))]
        with self._patch_get_connection(), self._patch_worker_all(workers):
            result = get_workers_for_queue('default')
        self.assertEqual(result, 0)

    def test_returns_zero_when_no_workers(self):
        with self._patch_get_connection(), self._patch_worker_all([]):
            result = get_workers_for_queue('default')
        self.assertEqual(result, 0)

    def test_includes_worker_listening_on_multiple_queues(self):
        workers = [_make_worker(name='multi', queues=('high', 'default', 'low'))]
        with self._patch_get_connection(), self._patch_worker_all(workers):
            result = get_workers_for_queue('default')
        self.assertEqual(result, 1)

    def test_includes_worker_with_custom_ttl(self):
        # A worker started with --worker-ttl != default is reconstructed by RQ with the default TTL (RQ does not persist
        # worker_ttl in the worker hash). The fact that Worker.all() returned the worker at all is RQ's confirmation
        # that the hash hasn't expired -- so we must include it regardless of how stale its heartbeat would look
        # measured against the default TTL.
        worker = _make_worker(name='long-ttl')
        worker.worker_ttl = 420  # rq's DEFAULT_WORKER_TTL, what find_by_key would produce
        worker.last_heartbeat = None  # heartbeat-derived freshness must not gate inclusion
        with self._patch_get_connection(), self._patch_worker_all([worker]):
            result = get_workers_for_queue('default')
        self.assertEqual(result, 1)

    def test_filters_to_queue_in_mixed_set(self):
        workers = [
            _make_worker(name='default-worker'),
            _make_worker(name='high-worker', queues=('high',)),
        ]
        with self._patch_get_connection(), self._patch_worker_all(workers):
            result = get_workers_for_queue('default')
        self.assertEqual(result, 1)


class AnyWorkersForQueueTestCase(TestCase):
    """
    any_workers_for_queue() must apply the same queue filter as
    get_workers_for_queue(), but short-circuit on the first live match.
    """

    def _patch_keys_and_lookup(self, workers):
        keys = [f'rq:worker:{w.name}' for w in workers]
        by_key = dict(zip(keys, workers))
        return (
            patch('utilities.rqworker.Worker.all_keys', return_value=keys),
            patch('utilities.rqworker.Worker.find_by_key', side_effect=lambda key, connection=None: by_key.get(key)),
        )

    def _patch_get_connection(self):
        return patch('utilities.rqworker.get_connection', return_value=MagicMock())

    def test_returns_true_when_worker_present(self):
        workers = [_make_worker(name='alive')]
        keys_patch, find_patch = self._patch_keys_and_lookup(workers)
        with self._patch_get_connection(), keys_patch, find_patch:
            self.assertTrue(any_workers_for_queue('default'))

    def test_returns_false_when_no_workers(self):
        keys_patch, find_patch = self._patch_keys_and_lookup([])
        with self._patch_get_connection(), keys_patch, find_patch:
            self.assertFalse(any_workers_for_queue('default'))

    def test_returns_false_when_only_other_queue(self):
        workers = [_make_worker(name='other', queues=('high',))]
        keys_patch, find_patch = self._patch_keys_and_lookup(workers)
        with self._patch_get_connection(), keys_patch, find_patch:
            self.assertFalse(any_workers_for_queue('default'))

    def test_short_circuits_on_first_live_worker(self):
        # The first key resolves to a live worker; subsequent keys must not
        # be fetched.
        workers = [
            _make_worker(name='alive'),
            _make_worker(name='other'),
        ]
        keys = [f'rq:worker:{w.name}' for w in workers]
        by_key = dict(zip(keys, workers))
        find = MagicMock(side_effect=lambda key, connection=None: by_key.get(key))
        with self._patch_get_connection(), \
                patch('utilities.rqworker.Worker.all_keys', return_value=keys), \
                patch('utilities.rqworker.Worker.find_by_key', find):
            self.assertTrue(any_workers_for_queue('default'))
        self.assertEqual(find.call_count, 1)

    def test_skips_missing_workers(self):
        # find_by_key returning None (stale registry entry pointing to a
        # vanished hash) must not raise; iteration continues to the next key.
        live = _make_worker(name='alive')
        keys = ['rq:worker:ghost', 'rq:worker:alive']
        find = MagicMock(side_effect=[None, live])
        with self._patch_get_connection(), \
                patch('utilities.rqworker.Worker.all_keys', return_value=keys), \
                patch('utilities.rqworker.Worker.find_by_key', find):
            self.assertTrue(any_workers_for_queue('default'))


class GetAllWorkersTestCase(TestCase):
    """
    get_all_workers() must return all live workers regardless of which queue
    they service. This preserves the queue-agnostic semantics of the
    dashboard / status API counters that previously used
    Worker.count(get_connection('default')).
    """

    def _patch_worker_all(self, workers):
        return patch('utilities.rqworker.Worker.all', return_value=workers)

    def _patch_get_connection(self):
        return patch('utilities.rqworker.get_connection', return_value=MagicMock())

    def test_returns_workers_across_all_queues(self):
        # Workers on non-default queues must still be counted -- the prior
        # contract (Worker.count(connection)) was queue-agnostic.
        workers = [
            _make_worker(name='default-worker'),
            _make_worker(name='high-worker', queues=('high',)),
            _make_worker(name='low-worker', queues=('low',)),
        ]
        with self._patch_get_connection(), self._patch_worker_all(workers):
            result = get_all_workers()
        self.assertEqual(result, {'default-worker', 'high-worker', 'low-worker'})

    def test_returns_empty_when_no_workers(self):
        with self._patch_get_connection(), self._patch_worker_all([]):
            result = get_all_workers()
        self.assertEqual(result, set())


class RecoverDeadJobsTestCase(RQQueueTestMixin, TestCase):
    """
    Test `NetBoxRQWorker.recover_dead_jobs()`, which terminates running jobs whose RQ job died (#23581).
    """

    def setUp(self):
        # Mute expected warnings about dead jobs.
        logger = logging.getLogger('netbox.jobs')
        original_level = logger.level
        logger.setLevel(logging.CRITICAL)
        self.addCleanup(logger.setLevel, original_level)

    @staticmethod
    def _recover(queue_name='default'):
        queue = get_queue(queue_name)
        NetBoxRQWorker([queue], connection=queue.connection).recover_dead_jobs()

    def _create_running_job(
        self, rq_status=RQJobStatus.FAILED, exc_string=None, interval=None, queue_name='default', **kwargs
    ):
        """
        Create a running Job with a real RQ job, set to the given RQ status.
        """
        job = Job.objects.create(
            name=DummyJobRunner.name,
            status=JobStatusChoices.STATUS_RUNNING,
            started=timezone.now() - timedelta(minutes=5),
            interval=interval,
            job_id=uuid.uuid4(),
            queue_name=queue_name,
        )
        rq_job = get_queue(queue_name).enqueue(DummyJobRunner.handle, job_id=str(job.job_id), job=job, **kwargs)
        rq_job.set_status(rq_status)
        if exc_string:
            Result.create_failure(rq_job, ttl=60, exc_string=exc_string)
        return job

    def test_failed_rq_job(self):
        exc_string = 'Work-horse terminated unexpectedly; waitpid returned 15 (signal 15); '
        job = self._create_running_job(exc_string=exc_string)
        # Without an RQ failure result, the error falls back to a message naming the RQ status.
        stopped_job = self._create_running_job(rq_status=RQJobStatus.STOPPED)

        self._recover()

        job.refresh_from_db()
        self.assertEqual(job.status, JobStatusChoices.STATUS_ERRORED)
        self.assertEqual(job.error, exc_string)
        self.assertIsNotNone(job.completed)
        self.assertIsNotNone(job.execution_time)

        stopped_job.refresh_from_db()
        self.assertEqual(stopped_job.status, JobStatusChoices.STATUS_ERRORED)
        self.assertIn(RQJobStatus.STOPPED.value, stopped_job.error)

    def test_live_rq_job_untouched(self):
        job = self._create_running_job(rq_status=RQJobStatus.STARTED)

        self._recover()

        job.refresh_from_db()
        self.assertEqual(job.status, JobStatusChoices.STATUS_RUNNING)
        self.assertIsNone(job.completed)

    def test_missing_rq_job_untouched(self):
        job = self._create_running_job()
        get_queue('default').connection.flushdb()

        self._recover()

        job.refresh_from_db()
        self.assertEqual(job.status, JobStatusChoices.STATUS_RUNNING)

    def test_claimed_by_another_worker(self):
        """
        A job that another worker claims between the query and the update must not be terminated twice.
        """
        self._create_running_job()
        original_get_rq_job = Job._get_rq_job

        def get_rq_job_and_steal(self):
            Job.objects.filter(pk=self.pk).update(status=JobStatusChoices.STATUS_ERRORED)
            return original_get_rq_job(self)

        with (
            patch.object(Job, '_get_rq_job', get_rq_job_and_steal),
            patch.object(Job, 'terminate') as terminate,
        ):
            self._recover()

        terminate.assert_not_called()

    def test_recurring_job_rescheduled(self):
        job = self._create_running_job(interval=60, make_fail=True)

        with patch.object(DummyJobRunner, 'enqueue', wraps=DummyJobRunner.enqueue) as enqueue:
            self._recover()

        job.refresh_from_db()
        self.assertEqual(job.status, JobStatusChoices.STATUS_ERRORED)
        successors = Job.objects.filter(name=DummyJobRunner.name, status=JobStatusChoices.STATUS_SCHEDULED)
        self.assertEqual(successors.count(), 1)
        successor = successors.first()
        self.assertEqual(successor.interval, 60)
        self.assertGreater(successor.scheduled, timezone.now())

        # The original runtime kwargs are carried over, less the dead job itself.
        enqueue.assert_called_once()
        self.assertIs(enqueue.call_args.kwargs['make_fail'], True)
        self.assertNotIn('job', enqueue.call_args.kwargs)
