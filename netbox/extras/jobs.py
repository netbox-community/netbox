import logging
import traceback
from contextlib import nullcontext

from django.db import transaction
from django.utils.translation import gettext as _

from core.signals import clear_events
from extras.models import Script as ScriptModel
from netbox.context_managers import event_tracking
from netbox.jobs import JobRunner
from utilities.exceptions import AbortScript, AbortTransaction
from .utils import is_report


class ScriptJob(JobRunner):
    """
    Script execution job.

    A wrapper for calling Script.run(). This performs error handling and provides a hook for committing changes. It
    exists outside the Script class to ensure it cannot be overridden by a script author.
    """

    class Meta:
        # An explicit job name is not set because it doesn't make sense in this context. Currently, there's no scenario
        # where jobs other than this one are used. Therefore, it is hidden, resulting in a cleaner job table overview.
        name = ''

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
                with transaction.atomic():
                    script.output = script.run(data, commit)
                    if not commit:
                        raise AbortTransaction()
            except AbortTransaction:
                script.log_info(message=_("Database changes have been reverted automatically."))
                if script.failed:
                    logger.warning(f"Script failed")
                    raise

        except Exception as e:
            if type(e) is AbortScript:
                msg = _("Script aborted with error: ") + str(e)
                if is_report(type(script)):
                    script.log_failure(message=msg)
                else:
                    script.log_failure(msg)
                logger.error(f"Script aborted with error: {e}")

            else:
                stacktrace = traceback.format_exc()
                script.log_failure(
                    message=_("An exception occurred: ") + f"`{type(e).__name__}: {e}`\n```\n{stacktrace}\n```"
                )
                logger.error(f"Exception raised during script execution: {e}")

            if type(e) is not AbortTransaction:
                script.log_info(message=_("Database changes have been reverted due to error."))

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
        script = ScriptModel.objects.get(pk=self.job.object_id).python_class()

        # Add files to form data
        if request:
            files = request.FILES
            for field_name, fileobj in files.items():
                data[field_name] = fileobj

        # Add the current request as a property of the script
        script.request = request

        # Execute the script. If commit is True, wrap it with the event_tracking context manager to ensure we process
        # change logging, event rules, etc.
        with event_tracking(request) if commit else nullcontext():
            self.run_script(script, request, data, commit)
