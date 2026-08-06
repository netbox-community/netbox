import logging
import traceback
from contextlib import ExitStack

from django.db import DEFAULT_DB_ALIAS, router, transaction
from django.utils.translation import gettext as _

from core.signals import clear_events
from dcim.models import Device
from extras.models import Script as ScriptModel
from netbox.context_managers import event_tracking
from netbox.jobs import JobRunner
from netbox.registry import registry
from utilities.exceptions import AbortScript, AbortTransaction

from .utils import is_report


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
