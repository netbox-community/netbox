import logging
import traceback
from contextlib import ExitStack

import django_rq
from django.contrib.contenttypes.models import ContentType
from django.db import DEFAULT_DB_ALIAS, router, transaction
from django.utils.translation import gettext as _

from core.choices import JobStatusChoices
from core.models import Job
from core.signals import clear_events
from dcim.models import Device
from extras.models import CustomField
from extras.models import Script as ScriptModel
from netbox.context import current_request
from netbox.context_managers import event_tracking
from netbox.jobs import JobRunner
from netbox.registry import registry
from utilities.exceptions import AbortScript, AbortTransaction
from utilities.rqworker import get_queue_for_model

from .constants import CUSTOMFIELD_DATA_JOB_KEY, CUSTOMFIELD_DATA_JOB_TIMEOUT
from .utils import is_report


class CustomFieldDataJob(JobRunner):
    """
    Purge stored data for a custom field which has been deleted, or unassigned from one or more
    object types.

    This runs in the background because it must touch every object of each affected type, which can
    outlast the request on a large installation. Deferring it is safe: the field is already gone as
    far as every read path is concerned, so the leftover keys are inert until this job removes them
    (CustomFieldsMixin.clean() also prunes them opportunistically on save).

    The one thing deferral does jeopardize is reuse of the field's name -- a new field created with
    the same name before this job completes would inherit the old field's values. See
    get_pending_purges(), which is consulted before a name is assigned to any object type or a
    field is renamed.
    """

    class Meta:
        name = 'Custom field data cleanup'

    @classmethod
    def enqueue_purge(cls, name, object_types, user=None):
        """
        Schedule removal of the named custom field's data from the given object types.

        Keyed on the name rather than a CustomField instance because the field itself is typically
        gone by the time this runs.

        The job is attributed to the user responsible for the change where one can be determined,
        so that they are notified once the purge completes: the name cannot be reused until then,
        and they are the party being asked to wait.
        """
        object_type_ids = sorted(ot.pk for ot in object_types)
        if not object_type_ids:
            return None

        if user is None:
            request = current_request.get()
            if request and (request_user := getattr(request, 'user', None)):
                user = request_user if request_user.is_authenticated else None

        kwargs = {
            'custom_field_name': name,
            'object_type_ids': object_type_ids,
        }
        job = cls.enqueue(
            name=_('Purge custom field data ({name})').format(name=name),
            user=user,
            job_timeout=CUSTOMFIELD_DATA_JOB_TIMEOUT,
            **kwargs
        )

        # Record the target on the job itself so that get_pending_purges() can identify outstanding
        # work without having to inspect the RQ queue. Namespaced under its own key, as Job.data is
        # shared with other job types (e.g. script output).
        job.data = {
            CUSTOMFIELD_DATA_JOB_KEY: kwargs,
        }
        job.save(update_fields=['data'])

        return job

    @classmethod
    def get_pending_purges(cls, name, object_types):
        """
        Return any purge job for the named custom field which may have left data on one or more of
        the given object types.

        A purge counts as outstanding until it has actually completed: a job which errored or was
        never picked up (no worker running) has left data behind just as surely as one still
        queued, and reusing the name at that point would silently resurrect it.
        """
        object_type_ids = {ot.pk for ot in object_types}
        if not object_type_ids:
            return []

        pending = Job.objects.filter(**{
            f'data__{CUSTOMFIELD_DATA_JOB_KEY}__custom_field_name': name,
        }).exclude(status=JobStatusChoices.STATUS_COMPLETED)

        return [
            job for job in pending.iterator()
            if object_type_ids & set(job.data[CUSTOMFIELD_DATA_JOB_KEY].get('object_type_ids') or [])
        ]

    @classmethod
    def requeue_stalled_purges(cls, jobs):
        """
        Re-submit any of the given purge jobs which has stopped without completing, and return
        those which were resubmitted.

        Without this, a purge which errored or timed out would block reuse of the field's name
        indefinitely: NetBox offers no way to re-run a job, and deleting the job record would lift
        the guard while the stale data remained.

        The existing job is resubmitted rather than replaced with a new one because the caller
        aborts the request immediately afterward, rolling back the transaction (and with it any new
        Job record). Enqueuing in Redis survives that rollback, and the job record in the database
        is left untouched.
        """
        requeued = []

        for job in jobs:
            if job.status not in (JobStatusChoices.STATUS_ERRORED, JobStatusChoices.STATUS_FAILED):
                # Still queued, scheduled, or running: it will get there on its own
                continue

            # Clear the previous attempt's execution state on the instance handed to RQ. Job.start()
            # returns early for a job which already carries a start time, so without this the
            # resubmitted job would never be marked as running, and Job.terminate() would report the
            # earlier failure's error against a successful run. This cannot be persisted here, as
            # the caller's transaction is about to be rolled back; it takes effect when the worker
            # picks the job up, as Job.start() writes the whole row from this instance. The job's
            # log is left intact as a record of the failed attempt.
            job.status = JobStatusChoices.STATUS_PENDING
            job.started = None
            job.completed = None
            job.error = ''

            queue = django_rq.get_queue(job.queue_name or get_queue_for_model(None))
            queue.enqueue(
                cls.handle,
                job_id=str(job.job_id),
                job=job,
                job_timeout=CUSTOMFIELD_DATA_JOB_TIMEOUT,
                **job.data[CUSTOMFIELD_DATA_JOB_KEY]
            )
            requeued.append(job)

        return requeued

    def run(self, custom_field_name, object_type_ids, **kwargs):
        content_types = ContentType.objects.filter(pk__in=object_type_ids)
        self.logger.info(
            f"Purging data for custom field '{custom_field_name}' from "
            f"{len(object_type_ids)} object type(s)"
        )

        CustomField.purge_object_data(custom_field_name, content_types)

        self.logger.info("Purge completed successfully")


class ScriptJob(JobRunner):
    """
    Script execution job.

    A wrapper for calling Script.run(). This performs error handling and provides a hook for committing changes. It
    exists outside the Script class to ensure it cannot be overridden by a script author.
    """

    class Meta:
        name = 'Run Script'

    def run_script(self, script, request, data, commit):
        """
        Core script execution task. We capture this within a method to allow for conditionally wrapping it with the
        event_tracking context manager (which is bypassed if commit == False).

        Args:
            request: The WSGI request associated with this execution (if any)
            data: A dictionary of data to be passed to the script upon execution
            commit: Passed through to Script.run()
        """
        logger = logging.getLogger(f"netbox.scripts.{script.full_name}")
        logger.info(f"Running script (commit={commit})")

        try:
            try:
                # A script can modify multiple models so need to do an atomic lock on
                # both the default database (for non ChangeLogged models) and potentially
                # any other database (for ChangeLogged models)
                changeloged_db = router.db_for_write(Device)
                with transaction.atomic(using=DEFAULT_DB_ALIAS):
                    # If branch database is different from default, wrap in a second atomic transaction
                    # Note: Don't add any extra code between the two atomic transactions,
                    # otherwise the changes might get committed to the default database
                    # if there are any raised exceptions.
                    if changeloged_db != DEFAULT_DB_ALIAS:
                        with transaction.atomic(using=changeloged_db):
                            script.output = script.run(data, commit)
                            if not commit:
                                raise AbortTransaction()
                    else:
                        script.output = script.run(data, commit)
                        if not commit:
                            raise AbortTransaction()
            except AbortTransaction:
                script.log_info(message=_("Database changes have been reverted automatically."))
                if script.failed:
                    logger.warning("Script failed")

        except Exception as e:
            if type(e) is AbortScript:
                msg = _("Script aborted with error: ") + str(e)
                if is_report(type(script)):
                    script.log_failure(message=msg)
                else:
                    script.log_failure(msg)
                logger.error(f"Script aborted with error: {e}")
                self.logger.error(f"Script aborted with error: {e}")

            else:
                stacktrace = traceback.format_exc()
                script.log_failure(
                    message=_("An exception occurred: ") + f"`{type(e).__name__}: {e}`\n```\n{stacktrace}\n```"
                )
                logger.error(f"Exception raised during script execution: {e}")
                self.logger.error(f"Exception raised during script execution: {e}")

            if type(e) is not AbortTransaction:
                script.log_info(message=_("Database changes have been reverted due to error."))
                self.logger.info("Database changes have been reverted due to error.")

            # Clear all pending events. Job termination (including setting the status) is handled by the job framework.
            if request:
                clear_events.send(request)
            raise

        # Update the job data regardless of the execution status of the job. Successes should be reported as well as
        # failures.
        finally:
            self.job.data = script.get_job_data()

    def run(self, data, request=None, commit=True, **kwargs):
        """
        Run the script.

        Args:
            job: The Job associated with this execution
            data: A dictionary of data to be passed to the script upon execution
            request: The WSGI request associated with this execution (if any)
            commit: Passed through to Script.run()
        """
        script_model = ScriptModel.objects.get(pk=self.job.object_id)
        self.logger.debug(f"Found ScriptModel ID {script_model.pk}")
        script = script_model.python_class()
        self.logger.debug(f"Loaded script {script.full_name}")

        # Add files to form data
        if request:
            files = request.FILES
            for field_name, fileobj in files.items():
                data[field_name] = fileobj

        # Add the current request as a property of the script
        script.request = request
        self.logger.debug(f"Request ID: {request.id if request else None}")

        if commit:
            self.logger.info("Executing script (commit enabled)")
        else:
            self.logger.warning("Executing script (commit disabled)")

        with ExitStack() as stack:
            for request_processor in registry['request_processors']:
                if not commit and request_processor is event_tracking:
                    continue
                stack.enter_context(request_processor(request))
            self.run_script(script, request, data, commit)
