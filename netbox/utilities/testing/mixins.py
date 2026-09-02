from django.test.testcases import SerializeMixin
from django_rq import get_queue
from django_rq.workers import get_worker
from rq import SimpleWorker

__all__ = (
    'RQQueueTestMixin',
)


class RQQueueTestMixin(SerializeMixin):
    """
    Clear RQ queues before and after each test.

    Test classes using this mixin share a single RQ (Redis) instance. Under the parallel
    test runner that Redis is not isolated per worker (unlike the database), so concurrent
    classes that enqueue and assert exact queue counts race each other. SerializeMixin
    holds an exclusive lock on `lockfile`, so no two classes using this mixin run at the
    same time, which removes that cross-worker contention.
    """
    lockfile = __file__
    rq_queue_names = ('default', 'high', 'low')

    @classmethod
    def clear_rq_queues(cls):
        for queue_name in cls.rq_queue_names:
            # Flush only the queue's own database. FLUSHALL would empty every database on the Redis
            # server, including the caching database, whose keys (e.g. the cached config revision)
            # are shared by the other parallel test workers.
            get_queue(queue_name).connection.flushdb()

    def run_rq_jobs(self, *queue_names, burst=True):
        """
        Process queued RQ jobs synchronously for the given queue(s) (defaulting to 'default').

        Uses a non-forking SimpleWorker: the default RQ worker forks a work horse which would
        inherit the test's open database connection. Two processes sharing one connection
        corrupts it — on an SSL-encrypted connection this surfaces as "bad record mac" and
        closes the connection for every subsequent test. SimpleWorker runs jobs in-process,
        so the connection is never shared.
        """
        worker = get_worker(*(queue_names or ('default',)), worker_class=SimpleWorker)
        worker.work(burst=burst)

    def setUp(self):
        super().setUp()

        # Clear all queues before running each test
        self.clear_rq_queues()

    def tearDown(self):
        try:
            # Clear all queues after each test so no leftover jobs leak into the next test suite
            self.clear_rq_queues()
        finally:
            super().tearDown()
