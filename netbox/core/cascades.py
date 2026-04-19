"""
Declarative cascade registrations for core models.

Replaces imperative delete() overrides in core models with structured declarations.
"""
import django_rq
from rq.exceptions import InvalidJobOperation

from netbox.cascades import CascadeMethod, CascadeSpec, CascadeTiming, cascade_registry
from utilities.rqworker import get_queue_for_model


# ──────────────────────────────────────────────────────────────────────
# ManagedFile pre-delete → delete file from disk
# Replaces: imperative code in ManagedFile.delete()
# ──────────────────────────────────────────────────────────────────────

def _managedfile_delete_from_disk(instance, **kwargs):
    """Before deleting a ManagedFile, remove the underlying file from storage."""
    storage = instance.storage
    try:
        storage.delete(instance.full_path)
    except FileNotFoundError:
        pass


cascade_registry.register(
    CascadeSpec(
        source_model='core.managedfile',
        target_model='(filesystem)',
        timing=CascadeTiming.PRE_DELETE,
        method=CascadeMethod.CUSTOM,
        handler=_managedfile_delete_from_disk,
        skip_on_create=False,
        description='Delete managed file from disk before ManagedFile DB record is deleted',
    ),
)


# ──────────────────────────────────────────────────────────────────────
# Job post-delete → cancel RQ job
# Replaces: imperative code in Job.delete()
# Note: queue_name and job_id are still accessible on the instance
# after the DB row is gone because post_delete passes the in-memory object.
# ──────────────────────────────────────────────────────────────────────

def _job_cancel_rq(instance, **kwargs):
    """After deleting a Job, cancel the corresponding RQ background job."""
    rq_queue_name = instance.queue_name or get_queue_for_model(
        instance.object_type.model if instance.object_type else None
    )
    rq_job_id = str(instance.job_id)

    queue = django_rq.get_queue(rq_queue_name)
    job = queue.fetch_job(rq_job_id)
    if job:
        try:
            job.cancel()
        except InvalidJobOperation:
            pass


cascade_registry.register(
    CascadeSpec(
        source_model='core.job',
        target_model='(rq)',
        timing=CascadeTiming.POST_DELETE,
        method=CascadeMethod.CUSTOM,
        handler=_job_cancel_rq,
        skip_on_create=False,
        description='Cancel the RQ background job after Job DB record is deleted',
    ),
)


# ──────────────────────────────────────────────────────────────────────
# DataSource save → delete pending sync jobs when sync_interval cleared
# Replaces: imperative code in DataSource.save()
# ──────────────────────────────────────────────────────────────────────

def _datasource_clear_pending_jobs(instance, **kwargs):
    """When sync_interval is cleared, delete any pending sync jobs for this DataSource."""
    if kwargs.get('created', False):
        return
    if not instance.sync_interval:
        from core.choices import JobStatusChoices
        instance.jobs.filter(status=JobStatusChoices.STATUS_PENDING).delete()


cascade_registry.register(
    CascadeSpec(
        source_model='core.datasource',
        target_model='core.job',
        trigger_fields=frozenset({'sync_interval'}),
        method=CascadeMethod.CUSTOM,
        handler=_datasource_clear_pending_jobs,
        skip_on_create=True,
        description='Delete pending sync jobs when DataSource sync_interval is cleared',
    ),
)
