from django_rq import get_queue
from django_rq.workers import get_worker
from rq import SimpleWorker

__all__ = (
    'RQQueueTestMixin',
)


class RQQueueTestMixin:
    """
    Clear RQ queues before and after each test.
    """
    rq_queue_names = ('default', 'high', 'low')

    @classmethod
    def clear_rq_queues(cls):
        for queue_name in cls.rq_queue_names:
            get_queue(queue_name).connection.flushall()

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
