import logging
import traceback
from contextlib import ExitStack

from django.apps import apps
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

RENDER_CONFIG_CONTEXT_CHUNK_SIZE = 500

# Safety bound on the number of re-scan passes performed by RenderConfigContextJob.run() (see the
# loop there). Each pass re-queries for NULL caches, so any finite burst of concurrent
# invalidations is drained well within this limit; the cap only guards against an object whose
# cache is being invalidated faster than it can be rendered (pathological, unbounded churn).
RENDER_CONFIG_CONTEXT_MAX_PASSES = 100


class RenderConfigContextJob(JobRunner):
    """
    Recompute the pre-rendered `_config_context_data` cache for a set of Devices or
    VirtualMachines. Enqueued (coalesced) by the invalidation helpers in extras/cache.py whenever
    an upstream change (ConfigContext, related object, or the object itself) NULLs a cache.

    This is *not* a recurring system job: the initial post-upgrade population is handled by the
    `rebuild_config_context_cache` management command, and steady-state freshness is maintained by
    the invalidation signals.
    """

    class Meta:
        name = 'Render config context'

    def run(self, model_label=None, pks=None, **kwargs):
        """
        Args:
            model_label: 'dcim.device' or 'virtualization.virtualmachine'. If None, both are processed.
            pks: An iterable of object PKs to refresh. If None, refresh all objects whose cache is null.
        """
        labels = (model_label,) if model_label is not None else ('dcim.device', 'virtualization.virtualmachine')
        pks = list(pks) if pks is not None else None

        # Re-scan until a full pass renders nothing. An invalidation that commits while this job is
        # already RUNNING coalesces into this job — JobRunner.enqueue_once() treats RUNNING as an
        # enqueued state — so it will NOT schedule a follow-up job. If we rendered in a single pass,
        # any cache NULLed after the iterator moved past its row (or after the pass for its model
        # completed) would be left populated by no one, stranding it on the on-demand read path
        # indefinitely. Looping until a pass finds no renderable NULL caches guarantees those late
        # invalidations are picked up before this job finishes.
        total = 0
        for _pass in range(RENDER_CONFIG_CONTEXT_MAX_PASSES):
            rendered = sum(self._render_for_model(label, pks=pks) for label in labels)
            total += rendered
            # No progress this pass means either nothing is NULL or the only NULL rows are churning
            # under concurrent invalidation (each such invalidation enqueues its own follow-up), so
            # there is nothing more for us to safely do.
            if not rendered:
                break
        else:
            # The loop ran every pass without ever rendering nothing, meaning caches are being
            # invalidated about as fast as we can render them. This is pathological churn worth
            # surfacing: each lingering invalidation enqueues its own follow-up job, so the caches
            # are not stranded, but the sustained rate warrants investigation.
            self.logger.warning(
                f"Reached the maximum of {RENDER_CONFIG_CONTEXT_MAX_PASSES} render passes with caches "
                f"still being invalidated; config context caches may be churning under sustained "
                f"concurrent invalidation."
            )

        self.logger.info(f"Rendered config context for {total} object(s)")

    def _render_for_model(self, model_label, pks):
        """
        Render and cache config context for every object of the given model whose cache is
        currently NULL (optionally restricted to `pks`). Returns the number of objects written.
        """
        Model = apps.get_model(model_label)
        qs = Model.objects.filter(_config_context_data__isnull=True)
        if pks is not None:
            qs = qs.filter(pk__in=list(pks))

        # Annotate so each instance's render() uses the same aggregated subquery the on-demand
        # path would use, avoiding N additional queries.
        qs = qs.annotate_config_context_data()

        rendered = 0
        for obj in qs.iterator(chunk_size=RENDER_CONFIG_CONTEXT_CHUNK_SIZE):
            # Capture the generation we rendered against, then write the result back only if no
            # invalidation has bumped it in the meantime (compare-and-set). If a fresh invalidation
            # won the race, the row stays NULL with a higher generation and the follow-up job it
            # enqueued will re-render it — we never persist a stale value.
            generation = obj._config_context_generation
            data = obj.render_config_context()
            updated = Model.objects.filter(
                pk=obj.pk,
                _config_context_generation=generation,
            ).update(_config_context_data=data)
            rendered += updated

        return rendered


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
