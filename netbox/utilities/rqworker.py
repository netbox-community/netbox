from django_rq.queues import get_connection
from rq import Retry, Worker

from netbox.config import get_config
from netbox.constants import RQ_QUEUE_DEFAULT

__all__ = (
    'get_queue_for_model',
    'get_rq_retry',
    'get_workers_for_queue',
)


def get_queue_for_model(model):
    """
    Return the configured queue name for jobs associated with the given model.
    """
    return get_config().QUEUE_MAPPINGS.get(model, RQ_QUEUE_DEFAULT)


def get_workers_for_queue(queue_name):
    """
    Returns True if a worker process is currently servicing the specified queue.
    """
    return Worker.count(get_connection(queue_name))


def get_rq_retry():
    """
    If RQ_RETRY_MAX is defined and greater than zero, instantiate and return a Retry object to be
    used when queuing a job. Otherwise, return None.
    """
    retry_max = get_config().RQ_RETRY_MAX
    retry_interval = get_config().RQ_RETRY_INTERVAL
    if retry_max:
        return Retry(max=retry_max, interval=retry_interval)
