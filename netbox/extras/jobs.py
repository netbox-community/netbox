import logging
import traceback
from contextlib import ExitStack

from django.core.exceptions import ValidationError
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

        # Add the current request as a property of the script
        script.request = request
        self.logger.debug(f"Request ID: {request.id if request else None}")

        # Normalize incoming payload for the form: API callers submit variables under "data".
        payload = data or {}
        if isinstance(payload, dict) and 'data' in payload:
            payload = payload['data'] or {}

        files = request.FILES if request else None
        if files:
            for field_name, fileobj in files.items():
                # merge into payload so script.run receives the uploaded files in data
                payload[field_name] = fileobj

        # Validate & clean using the script's form so ObjectVar/MultiObjectVar IDs become model instances
        if hasattr(script, 'as_form') and callable(getattr(script, 'as_form')):
            try:
                form = script.as_form(data=payload, files=files)
                if not form.is_valid():
                    raise AbortScript(f"Script input validation failed: {form.errors.as_json()}")

                cleaned = form.cleaned_data

                # Remove execution parameters
                for key in list(cleaned.keys()):
                    if key.startswith('_'):
                        cleaned.pop(key)

                # Preserve uploaded files that were merged into the payload so scripts still see them
                # even if the Script's form doesn't declare file fields.
                if files:
                    for fname, fobj in files.items():
                        if fname not in cleaned:
                            cleaned[fname] = fobj

                # Use cleaned form data as the data passed into the script
                data = cleaned
            except AbortScript:
                # Re-raise for run_script() to log/handle
                raise
            except (ValidationError, TypeError, ValueError) as e:
                raise AbortScript(f"Error validating script input: {e!s}")
        else:
            # Script doesn't provide as_form (e.g., lightweight test double); keep `data` as-is.
            data = payload

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
