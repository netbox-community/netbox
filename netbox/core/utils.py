from django.db import DatabaseError, connection
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from django_rq.queues import get_queue, get_queue_by_index, get_redis_connection
from django_rq.settings import get_queues_list, get_queues_map
from django_rq.utils import get_jobs, stop_jobs
from rq import requeue_job
from rq.exceptions import NoSuchJobError
from rq.job import Job as RQ_Job
from rq.job import JobStatus as RQJobStatus
from rq.registry import (
    DeferredJobRegistry,
    FailedJobRegistry,
    FinishedJobRegistry,
    ScheduledJobRegistry,
    StartedJobRegistry,
)

__all__ = (
    'delete_rq_job',
    'enqueue_rq_job',
    'get_db_schema',
    'get_rq_jobs',
    'get_rq_jobs_from_status',
    'requeue_rq_job',
    'stop_rq_job',
)


def get_rq_jobs():
    """
    Return a list of all RQ jobs.
    """
    jobs = set()

    for queue in get_queues_list():
        queue = get_queue(queue['name'])
        jobs.update(queue.get_jobs())

    return list(jobs)


def get_rq_jobs_from_status(queue, status):
    """
    Return the RQ jobs with the given status.
    """
    jobs = []

    try:
        registry_cls = {
            RQJobStatus.STARTED: StartedJobRegistry,
            RQJobStatus.DEFERRED: DeferredJobRegistry,
            RQJobStatus.FINISHED: FinishedJobRegistry,
            RQJobStatus.FAILED: FailedJobRegistry,
            RQJobStatus.SCHEDULED: ScheduledJobRegistry,
        }[status]
    except KeyError:
        raise Http404
    registry = registry_cls(queue.name, queue.connection)

    job_ids = registry.get_job_ids()
    if status != RQJobStatus.DEFERRED:
        jobs = get_jobs(queue, job_ids, registry)
    else:
        # Deferred jobs require special handling
        for job_id in job_ids:
            try:
                jobs.append(RQ_Job.fetch(job_id, connection=queue.connection, serializer=queue.serializer))
            except NoSuchJobError:
                pass

    if jobs and status == RQJobStatus.SCHEDULED:
        for job in jobs:
            job.scheduled_at = registry.get_scheduled_time(job)

    return jobs


def delete_rq_job(job_id):
    """
    Delete the specified RQ job.
    """
    config = get_queues_list()[0]
    try:
        job = RQ_Job.fetch(job_id, connection=get_redis_connection(config['connection_config']),)
    except NoSuchJobError:
        raise Http404(_("Job {job_id} not found").format(job_id=job_id))

    queue_index = get_queues_map()[job.origin]
    queue = get_queue_by_index(queue_index)

    # Remove job id from queue and delete the actual job
    queue.connection.lrem(queue.key, 0, job.id)
    job.delete()


def requeue_rq_job(job_id):
    """
    Requeue the specified RQ job.
    """
    config = get_queues_list()[0]
    try:
        job = RQ_Job.fetch(job_id, connection=get_redis_connection(config['connection_config']),)
    except NoSuchJobError:
        raise Http404(_("Job {id} not found.").format(id=job_id))

    queue_index = get_queues_map()[job.origin]
    queue = get_queue_by_index(queue_index)

    requeue_job(job_id, connection=queue.connection, serializer=queue.serializer)


def enqueue_rq_job(job_id):
    """
    Enqueue the specified RQ job.
    """
    config = get_queues_list()[0]
    try:
        job = RQ_Job.fetch(job_id, connection=get_redis_connection(config['connection_config']),)
    except NoSuchJobError:
        raise Http404(_("Job {id} not found.").format(id=job_id))

    queue_index = get_queues_map()[job.origin]
    queue = get_queue_by_index(queue_index)

    try:
        # _enqueue_job is new in RQ 1.14, this is used to enqueue
        # job regardless of its dependencies
        queue._enqueue_job(job)
    except AttributeError:
        queue.enqueue_job(job)

    # Remove job from correct registry if needed
    if job.get_status() == RQJobStatus.DEFERRED:
        registry = DeferredJobRegistry(queue.name, queue.connection)
        registry.remove(job)
    elif job.get_status() == RQJobStatus.FINISHED:
        registry = FinishedJobRegistry(queue.name, queue.connection)
        registry.remove(job)
    elif job.get_status() == RQJobStatus.SCHEDULED:
        registry = ScheduledJobRegistry(queue.name, queue.connection)
        registry.remove(job)


def stop_rq_job(job_id):
    """
    Stop the specified RQ job.
    """
    config = get_queues_list()[0]
    try:
        job = RQ_Job.fetch(job_id, connection=get_redis_connection(config['connection_config']),)
    except NoSuchJobError:
        raise Http404(_("Job {job_id} not found").format(job_id=job_id))

    queue_index = get_queues_map()[job.origin]
    queue = get_queue_by_index(queue_index)

    return stop_jobs(queue, job_id)[0]


def get_db_schema():
    """
    Query the current PostgreSQL schema and return a list of tables, each with its columns and
    indexes. Returns an empty list if the database is not accessible.
    """
    db_schema = []
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name, column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = current_schema()
                ORDER BY table_name, ordinal_position
            """)
            columns_by_table = {}
            for table_name, column_name, data_type, is_nullable, column_default in cursor.fetchall():
                columns_by_table.setdefault(table_name, []).append({
                    'name': column_name,
                    'type': data_type,
                    'nullable': is_nullable == 'YES',
                    'default': column_default,
                })

            cursor.execute("""
                SELECT tablename, indexname, indexdef
                FROM pg_indexes
                WHERE schemaname = current_schema()
                ORDER BY tablename, indexname
            """)
            indexes_by_table = {}
            for table_name, index_name, index_def in cursor.fetchall():
                indexes_by_table.setdefault(table_name, []).append({
                    'name': index_name,
                    'definition': index_def,
                })

        for table_name in sorted(columns_by_table.keys()):
            db_schema.append({
                'name': table_name,
                'columns': columns_by_table[table_name],
                'indexes': indexes_by_table.get(table_name, []),
            })
    except DatabaseError:
        pass
    return db_schema
