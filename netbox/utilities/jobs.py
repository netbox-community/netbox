from django.contrib import messages
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from netbox.jobs import AsyncViewJob
from utilities.request import copy_safe_request

__all__ = (
    'is_background_request',
    'process_request_as_job',
)


def is_background_request(request):
    """
    Return True if the request is being processed as a background job.
    """
    return hasattr(request, 'job')


def process_request_as_job(view, request, name=None):
    """
    Process a request using a view as a background job.
    """

    # Check that the request that is not already being processed as a background job (would be a loop)
    if is_background_request(request):
        return

    # Create a serializable copy of the original request
    request_copy = copy_safe_request(request)

    # Enqueue a job to perform the work in the background
    job = AsyncViewJob.enqueue(
        name=name,
        user=request.user,
        view_cls=view,
        request=request_copy,
    )

    # Record a message on the original request indicating deferral to a background job
    msg = _('Created background job {id}: <a href="{url}">{name}</a>').format(
        id=job.pk,
        url=job.get_absolute_url(),
        name=job.name
    )
    messages.info(request, mark_safe(msg))

    return job
