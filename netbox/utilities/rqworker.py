from django_rq.queues import get_connection
from rq import Worker

from netbox.config import get_config
from netbox.constants import RQ_QUEUE_DEFAULT

__all__ = (
    'get_queue_for_model',
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
