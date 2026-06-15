import json
import logging
import os
import traceback
from abc import ABC, abstractmethod
from datetime import timedelta
from io import BytesIO
from pathlib import Path
from urllib.parse import urlsplit

from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import ProtectedError, RestrictedError
from django.http import Http404
from django.utils import timezone
from django.utils.functional import classproperty
from django.utils.module_loading import import_string
from django_pglocks import advisory_lock
from rest_framework.exceptions import APIException
from rq.timeouts import JobTimeoutException

from core.choices import JobStatusChoices
from core.exceptions import JobFailed
from core.models import Job, ObjectType
from netbox.constants import ADVISORY_LOCK_KEYS
from netbox.registry import registry
from utilities.exceptions import AbortRequest
from utilities.request import apply_request_processors

__all__ = (
    'AsyncAPIJob',
    'AsyncViewJob',
    'JobRunner',
    'system_job',
)

# The installation root, e.g. "/opt/netbox/". Used to strip absolute path
# prefixes from traceback file paths before recording them in the job log.
# jobs.py lives at <root>/netbox/netbox/jobs.py, so parents[2] is the root.
_INSTALL_ROOT = str(Path(__file__).resolve().parents[2]) + os.sep


def system_job(interval):
    """
    Decorator for registering a `JobRunner` class as system background job.
    """
    if type(interval) is not int:
        raise ImproperlyConfigured("System job interval must be an integer (minutes).")

    def _wrapper(cls):
        registry['system_jobs'][cls] = {
            'interval': interval
        }
        return cls

    return _wrapper


class JobLogHandler(logging.Handler):
    """
    A logging handler which records entries on a Job.
    """
    def __init__(self, job, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job = job

    def emit(self, record):
        # Enter the record in the log of the associated Job
        self.job.log(record)


class JobRunner(ABC):
    """
    Background Job helper class.

    This class handles the execution of a background job. It is responsible for maintaining its state, reporting errors,
    and scheduling recurring jobs.
    """

    class Meta:
        pass

    def __init__(self, job):
        """
        Args:
            job: The specific `Job` this `JobRunner` is executing.
        """
        self.job = job

        # Initiate the system logger
        self.logger = logging.getLogger(f"netbox.jobs.{self.__class__.__name__}")
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(JobLogHandler(job))

    @classproperty
    def name(cls):
        return getattr(cls.Meta, 'name', cls.__name__)

    @abstractmethod
    def run(self, *args, **kwargs):
        """
        Run the job.

        A `JobRunner` class needs to implement this method to execute all commands of the job.
        """
        pass

    @classmethod
    def handle(cls, job, *args, **kwargs):
        """
        Handle the execution of a `Job`.

        This method is called by the Job Scheduler to handle the execution of all job commands. It will maintain the
        job's metadata and handle errors. For periodic jobs, a new job is automatically scheduled using its `interval`.
        """
        logger = logging.getLogger('netbox.jobs')

        try:
            job.start()
            cls(job).run(*args, **kwargs)
            job.terminate()

        except JobFailed:
            logger.warning(f"Job {job} failed")
            job.terminate(status=JobStatusChoices.STATUS_FAILED)

        except Exception as e:
            tb_str = traceback.format_exc().replace(_INSTALL_ROOT, '')
            tb_record = logging.makeLogRecord({
                'levelno': logging.ERROR,
                'levelname': 'ERROR',
                'msg': tb_str,
            })
            job.log(tb_record)
            job.terminate(status=JobStatusChoices.STATUS_ERRORED, error=repr(e))
            if type(e) is JobTimeoutException:
                logger.error(e)

        # If the executed job is a periodic job, schedule its next execution at the specified interval.
        finally:
            if job.interval:
                # Determine the new scheduled time. Cannot be earlier than one minute in the future.
                new_scheduled_time = max(
                    (job.scheduled or job.started) + timedelta(minutes=job.interval),
                    timezone.now() + timedelta(minutes=1)
                )
                if job.object and getattr(job.object, "python_class", None):
                    kwargs["job_timeout"] = job.object.python_class.job_timeout

                enqueue_kwargs = dict(
                    instance=job.object,
                    name=job.name,
                    user=job.user,
                    schedule_at=new_scheduled_time,
                    interval=job.interval,
                    notifications=job.notifications,
                    **kwargs,
                )

                if cls in registry['system_jobs']:
                    # System jobs are also scheduled by `enqueue_once()` at worker startup,
                    # which races with this finally block and can produce duplicate schedules
                    # (see #22232). Acquire the same advisory lock used by `enqueue_once()`
                    # and skip rescheduling if a successor is already enqueued.
                    #
                    # This branch is limited to system jobs because generic recurring jobs
                    # (e.g. scheduled scripts) may have multiple legitimate schedules sharing
                    # the same runner/object/interval but differing in their runtime kwargs.
                    with advisory_lock(ADVISORY_LOCK_KEYS['job-schedules']):
                        successor_exists = Job.objects.filter(
                            name=cls.name,
                            object_id__isnull=True,
                            status__in=JobStatusChoices.ENQUEUED_STATE_CHOICES,
                            interval=job.interval,
                        ).exclude(pk=job.pk).exists()
                        if not successor_exists:
                            cls.enqueue(**enqueue_kwargs)
                else:
                    cls.enqueue(**enqueue_kwargs)

    @classmethod
    def get_jobs(cls, instance=None):
        """
        Get all jobs of this `JobRunner` related to a specific instance.
        """
        jobs = Job.objects.filter(name=cls.name)

        if instance:
            object_type = ObjectType.objects.get_for_model(instance, for_concrete_model=False)
            jobs = jobs.filter(
                object_type=object_type,
                object_id=instance.pk,
            )

        return jobs

    @classmethod
    def enqueue(cls, *args, **kwargs):
        """
        Enqueue a new `Job`.

        This method is a wrapper of `Job.enqueue()` using `handle()` as function callback. See its documentation for
        parameters.
        """
        name = kwargs.pop('name', None) or cls.name
        return Job.enqueue(cls.handle, name=name, *args, **kwargs)

    @classmethod
    @advisory_lock(ADVISORY_LOCK_KEYS['job-schedules'])
    def enqueue_once(cls, instance=None, schedule_at=None, interval=None, *args, **kwargs):
        """
        Enqueue a new `Job` once, i.e. skip duplicate jobs.

        Like `enqueue()`, this method adds a new `Job` to the job queue. However, if there's already a job of this
        class scheduled for `instance`, the existing job will be updated if necessary. This ensures that a particular
        schedule is only set up once at any given time, i.e. multiple calls to this method are idempotent.

        Note that this does not forbid running additional jobs with the `enqueue()` method, e.g. to schedule an
        immediate synchronization job in addition to a periodic synchronization schedule.

        For additional parameters see `enqueue()`.

        Args:
            instance: The NetBox object to which this job pertains (optional)
            schedule_at: Schedule the job to be executed at the passed date and time
            interval: Recurrence interval (in minutes)
        """
        job = cls.get_jobs(instance).filter(status__in=JobStatusChoices.ENQUEUED_STATE_CHOICES).first()
        if job:
            # If the job parameters haven't changed, don't schedule a new job and keep the current schedule. Otherwise,
            # delete the existing job and schedule a new job instead.
            if (not schedule_at or job.scheduled == schedule_at) and (job.interval == interval):
                return job
            job.delete()

        return cls.enqueue(instance=instance, schedule_at=schedule_at, interval=interval, *args, **kwargs)


class AsyncViewJob(JobRunner):
    """
    Execute a view as a background job.
    """
    class Meta:
        name = 'Async View'

    def run(self, view_cls, request, **kwargs):
        view = view_cls.as_view()
        request.job = self

        # Apply all registered request processors (e.g. event_tracking)
        with apply_request_processors(request):
            view(request)

        if self.job.error:
            raise JobFailed()


class AsyncAPIJob(JobRunner):
    """
    Execute a REST API bulk write (create/update/delete) as a background job.

    The viewset's action method is re-invoked inside the worker against a reconstructed
    request, so the synchronous and background code paths are identical (validation,
    transaction semantics, object permissions, and change logging all behave the same).
    The action's serialized Response is captured into the job's data.
    """
    class Meta:
        name = 'Async API Request'

    @staticmethod
    def _build_request(payload, method, request_id, scheme, host):
        """
        Reconstruct a minimal WSGIRequest carrying the original JSON payload. DRF's Request
        wrapper requires a real HttpRequest, and the original scheme/host are applied so that
        absolute URLs in the captured result (serializer hyperlink fields) point at the real
        server. The host is passed via HTTP_HOST verbatim (request.get_host() already formats
        it correctly, including bracketed IPv6, and Django's get_host() prefers it);
        SERVER_NAME/SERVER_PORT are populated only to satisfy WSGI, parsed via urlsplit so
        host:port and [::1]:port split correctly.
        """
        parsed_host = urlsplit(f'//{host}')
        body = json.dumps(payload).encode('utf-8')
        request = WSGIRequest({
            'REQUEST_METHOD': method.upper(),
            'PATH_INFO': '/',
            'CONTENT_TYPE': 'application/json',
            'CONTENT_LENGTH': str(len(body)),
            'wsgi.input': BytesIO(body),
            'wsgi.url_scheme': scheme,
            'HTTP_HOST': host,
            'SERVER_NAME': parsed_host.hostname or 'localhost',
            'SERVER_PORT': str(parsed_host.port) if parsed_host.port else ('443' if scheme == 'https' else '80'),
            'SERVER_PROTOCOL': 'HTTP/1.1',
        })
        request.id = request_id
        return request

    def run(
        self, viewset_class, action, payload, user_pk, request_id, method,
        action_kwargs=None, scheme='http', host='localhost', **kwargs
    ):
        # Imported here to avoid a circular import (netbox.api.viewsets imports from this module).
        from netbox.api.viewsets import HTTP_ACTIONS

        action_kwargs = action_kwargs or {}
        viewset_class = import_string(viewset_class)

        # Re-fetch the requesting user. If the user no longer exists or is inactive, fail
        # the job rather than running with stale identity (execution-time identity check).
        User = get_user_model()
        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            self.job.error = "The requesting user no longer exists."
            self.job.save()
            raise JobFailed()
        if not user.is_active:
            self.job.error = "The requesting user is no longer active."
            self.job.save()
            raise JobFailed()

        django_request = self._build_request(payload, method, request_id, scheme, host)

        # Instantiate the viewset and apply the minimal scaffolding that DRF's as_view()
        # normally sets, so initialize_request() can wire up parsers, etc.
        viewset = viewset_class()
        viewset.action_map = {method.lower(): action}
        viewset.kwargs = {}
        viewset.args = ()
        viewset.action = action
        viewset.format_kwarg = None

        drf_request = viewset.initialize_request(django_request)
        # Carry the authenticated user forward; we do not re-authenticate in the worker.
        # Setting .user populates the request's user cache, so DRF never lazily invokes
        # authentication (and nothing on the action path reads the authenticator/auth).
        drf_request.user = user
        drf_request.id = request_id
        viewset.request = drf_request

        # Re-apply object-level permission restriction exactly as BaseViewSet.initial() does.
        if perm_action := HTTP_ACTIONS[method.upper()]:
            viewset.queryset = viewset.queryset.restrict(user, perm_action)

        # Execute the action method within the registered request processors so change
        # logging and event rules fire (and are attributed to the original request_id).
        #
        # The synchronous path relies on NetBoxModelViewSet.dispatch() and DRF's
        # handle_exception() to translate exceptions into HTTP responses. Because we invoke
        # the action method directly (bypassing dispatch), we reproduce that translation here
        # so the captured result matches what the synchronous API would have returned:
        #   - APIException (incl. ValidationError, PermissionDenied, Http404) -> handle_exception()
        #   - AbortRequest / ProtectedError / RestrictedError -> exception_to_response()
        with apply_request_processors(drf_request):
            try:
                response = getattr(viewset, action)(drf_request, **action_kwargs)
            except (APIException, Http404, PermissionDenied) as e:
                response = viewset.handle_exception(e)
            except (AbortRequest, ProtectedError, RestrictedError) as e:
                response = viewset.exception_to_response(e)
                if response is None:
                    raise

        # Capture the action's result for the polling client, in the same shape for both
        # success and failure.
        self.job.data = {
            'status_code': response.status_code,
            'data': response.data,
        }

        if response.status_code >= 400:
            # A handled rejection (4xx), not a worker crash: record a concise summary and
            # mark the job failed (JobRunner.handle reserves "errored" for unhandled crashes).
            detail = response.data.get('detail') if isinstance(response.data, dict) else None
            self.job.error = str(detail) if detail else f"Request failed with status {response.status_code}."
            self.job.save()
            raise JobFailed()

        # On success, job.data is persisted by JobRunner.handle() -> job.terminate().
