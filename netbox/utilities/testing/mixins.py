from django_rq import get_queue

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
