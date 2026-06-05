import logging

from django_rq.queues import get_connection
from rq import Retry, Worker
from rq.worker_registration import REDIS_WORKER_KEYS
from rq.worker_registration import register as register_worker

from netbox.config import get_config
from netbox.constants import RQ_QUEUE_DEFAULT

__all__ = (
    'NetBoxRQWorker',
    'any_workers_for_queue',
    'get_all_workers',
    'get_queue_for_model',
    'get_rq_retry',
    'get_workers_for_queue',
)

logger = logging.getLogger('netbox.rqworker')


class NetBoxRQWorker(Worker):
    """
    RQ worker subclass which self-heals its registration. If the worker's
    registration is missing from Redis (e.g. because the tasks Redis database
    was lost and rebuilt while the worker was running), the next heartbeat
    will re-register the worker so that Worker.all() / Worker.find_by_key()
    can locate it again.
    """

    def heartbeat(self, *args, **kwargs):
        try:
            if not self.connection.sismember(REDIS_WORKER_KEYS, self.key):
                logger.warning(f"Worker {self.name} not found in registry; re-registering.")
                # If the worker hash still exists (partial Redis data loss),
                # register_birth() would raise because rq treats an existing,
                # non-dead hash as an active worker. Re-add to the registry
                # sets directly in that case; the heartbeat below will refresh
                # the hash TTL.
                if self.connection.exists(self.key) and not self.connection.hexists(self.key, 'death'):
                    register_worker(self, self.connection)
                else:
                    self.register_birth()
        except Exception:
            logger.exception("Failed to verify worker registration.")
        super().heartbeat(*args, **kwargs)


def get_queue_for_model(model):
    """
    Return the configured queue name for jobs associated with the given model.
    """
    return get_config().QUEUE_MAPPINGS.get(model, RQ_QUEUE_DEFAULT)


def _is_live_worker(worker, queue_name):
    """
    Return True if the given Worker is currently servicing queue_name.

    Liveness itself is enforced by RQ: Worker.all() / Worker.find_by_key()
    only return workers whose Redis hash still exists, and RQ resets that
    hash's expiry to (worker_ttl + 60s) on every heartbeat. So any worker
    returned by RQ has heartbeat'd within its configured TTL -- we only need
    to confirm it's listening on the requested queue. (Reconstructing
    worker_ttl ourselves would be unsafe: RQ does not persist worker_ttl in
    the hash, so a worker started with a non-default --worker-ttl is
    reconstructed with DEFAULT_WORKER_TTL regardless of its real TTL.)
    """
    return queue_name in worker.queue_names()


def get_workers_for_queue(queue_name):
    """
    Return the number of live workers currently servicing the given queue.
    """
    connection = get_connection(queue_name)
    return sum(
        1 for worker in Worker.all(connection=connection)
        if _is_live_worker(worker, queue_name)
    )


def get_all_workers():
    """
    Return the set of worker names currently registered on the tasks Redis
    connection, regardless of which queue(s) each worker is servicing. Stale
    registrations (workers whose Redis hash has expired) are filtered out by
    RQ via Worker.all() -- see _is_live_worker() for details.

    Used for system-wide worker counts (dashboard, status API), where the
    intent is "are any RQ workers running" rather than "are workers handling
    a specific queue."
    """
    connection = get_connection(RQ_QUEUE_DEFAULT)
    return {worker.name for worker in Worker.all(connection=connection)}


def any_workers_for_queue(queue_name):
    """
    Return True if at least one live worker is currently servicing the given
    queue. Cheaper than get_workers_for_queue() when only a liveness check is
    needed: workers are fetched one at a time and iteration stops at the first
    live match.
    """
    connection = get_connection(queue_name)
    for key in Worker.all_keys(connection=connection):
        worker = Worker.find_by_key(key, connection=connection)
        if worker is None:
            continue
        if _is_live_worker(worker, queue_name):
            return True
    return False


def get_rq_retry():
    """
    If RQ_RETRY_MAX is defined and greater than zero, instantiate and return a Retry object to be
    used when queuing a job. Otherwise, return None.
    """
    retry_max = get_config().RQ_RETRY_MAX
    retry_interval = get_config().RQ_RETRY_INTERVAL
    if retry_max:
        return Retry(max=retry_max, interval=retry_interval)
    return None
