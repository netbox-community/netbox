import logging
import traceback
from contextlib import ExitStack

from django.db import DEFAULT_DB_ALIAS, router, transaction
from django.utils.translation import gettext as _
from django_pglocks import advisory_lock

from core.models import ObjectType
from core.signals import clear_events
from dcim.models import Device
from extras.choices import CustomFieldStatusChoices
from extras.constants import CUSTOMFIELD_JOB_TIMEOUT
from extras.models import CustomField
from extras.models import Script as ScriptModel
from netbox.context_managers import event_tracking
from netbox.jobs import JobRunner
from netbox.registry import registry
from utilities.exceptions import AbortScript, AbortTransaction

from .utils import is_report

__all__ = (
    'CustomFieldDataJob',
    'CustomFieldProvisioningJob',
    'CustomFieldPurgeJob',
    'ScriptJob',
    'provision_custom_field',
    'purge_custom_field',
)


#
# Custom fields
#


def provision_custom_field(pk, object_type_pks=None, skip_locked=False):
    """
    Populate a new custom field's default value across the objects of the given types, then bring
    the field live. Returns True if the field was provisioned.

    The backfill is committed in batches, so an interruption leaves the field provisioning with some
    of its objects already updated. Running again completes it.

    Args:
        pk: The primary key of the CustomField to provision
        object_type_pks: The primary keys of the object types to provision, or None to provision
            every type currently assigned to the field. The housekeeping backstop passes None, as it
            has no record of which assignments deferred the work; that provisions more types than the
            deferred job would have, but is preferable to leaving the field offline indefinitely.
        skip_locked: Return False rather than waiting if the field's data lock is already held by
            another caller
    """
    # Taken on the connection the field is written on, as CustomField.delete() takes it, so that
    # the two are actually exclusive of one another.
    using = router.db_for_write(CustomField)
    with advisory_lock(CustomField.data_lock_key(pk), wait=not skip_locked, using=using) as acquired:
        if not acquired:
            return False

        # Rechecked now that the lock is held: whichever of this job and the housekeeping backstop
        # arrived first has left the field in a state the other no longer matches.
        custom_field = CustomField.objects.filter(pk=pk, status=CustomFieldStatusChoices.STATUS_PROVISIONING).first()
        if custom_field is None:
            return False

        if object_type_pks is None:
            object_types = custom_field.object_types.all()
        else:
            object_types = ObjectType.objects.filter(pk__in=object_type_pks)
        custom_field.populate_initial_data(object_types, commit_per_batch=True)

        # Applied via the queryset so that bringing the field live does not record a change of its
        # own, and cannot trip the guard in CustomField.clean().
        CustomField.objects.filter(pk=pk).update(status=CustomFieldStatusChoices.STATUS_ACTIVE)

    return True


def purge_custom_field(pk, skip_locked=False):
    """
    Remove a deleted custom field's data from all applicable objects, then remove the field itself.
    Returns True if the field was purged.

    The row is dropped only once its data is gone: until then it reserves the field's name against a
    new field which would otherwise inherit the orphaned values. The removal is committed in batches,
    so an interruption leaves data behind for a later run to finish removing.

    Args:
        pk: The primary key of the CustomField to purge
        skip_locked: Return False rather than waiting if the field's data lock is already held by
            another caller
    """
    # Taken on the connection the field is written on, as CustomField.delete() takes it, so that
    # the two are actually exclusive of one another.
    using = router.db_for_write(CustomField)
    with advisory_lock(CustomField.data_lock_key(pk), wait=not skip_locked, using=using) as acquired:
        if not acquired:
            return False

        # Rechecked now that the lock is held: whichever of this job and the housekeeping backstop
        # arrived first has left the field in a state the other no longer matches.
        custom_field = CustomField.objects.filter(pk=pk, status=CustomFieldStatusChoices.STATUS_DELETING).first()
        if custom_field is None:
            return False

        custom_field.remove_stale_data(custom_field.object_types.all(), commit_per_batch=True)
        custom_field._delete_row()

    return True


class CustomFieldDataJob(JobRunner):
    """
    Base class for the jobs which rewrite a custom field's stored data in bulk.

    The field is passed by primary key rather than assigned to the job as its object. Job.clean()
    permits only models with the jobs feature there, and granting CustomField that feature would
    give it a cascading relation to its jobs -- so the purge job, whose last act is to remove the
    row, would delete the record of its own execution as it ran.

    skip_locked is set where the job was enqueued by the housekeeping backstop, for which the field
    is only a candidate: the job properly responsible for it may still be working through it, and
    must be left to finish rather than blocking a worker here for its duration.
    """
    @classmethod
    def enqueue_for(cls, custom_field, **kwargs):
        """
        Enqueue this job for the given custom field, naming the field in the job's name and raising
        its timeout from the default (see CUSTOMFIELD_JOB_TIMEOUT).
        """
        return cls.enqueue(
            name=f'{cls.name}: {custom_field}',
            custom_field_pk=custom_field.pk,
            job_timeout=CUSTOMFIELD_JOB_TIMEOUT,
            **kwargs,
        )


class CustomFieldProvisioningJob(CustomFieldDataJob):
    """
    Populate the default value of a newly created custom field.
    """
    class Meta:
        name = 'Custom Field Provisioning'

    def run(self, custom_field_pk, *args, object_type_pks=None, skip_locked=False, **kwargs):
        if provision_custom_field(custom_field_pk, object_type_pks, skip_locked=skip_locked):
            self.logger.info("Custom field provisioned")
        else:
            self.logger.info("Custom field is no longer awaiting provisioning; skipping")


class CustomFieldPurgeJob(CustomFieldDataJob):
    """
    Purge the stored data of a deleted custom field, then delete the field.
    """
    class Meta:
        name = 'Custom Field Purge'

    def run(self, custom_field_pk, *args, skip_locked=False, **kwargs):
        if purge_custom_field(custom_field_pk, skip_locked=skip_locked):
            self.logger.info("Custom field data purged")
        else:
            self.logger.info("Custom field is no longer awaiting deletion; skipping")


#
# Scripts
#


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
