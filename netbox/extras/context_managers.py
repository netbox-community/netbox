from contextlib import contextmanager

from netbox.context import current_request, events_queue
from .events import flush_events


@contextmanager
def event_tracking(request):
    """
    Enable event tracking by connecting the appropriate signals to their receivers before code is run, and
    disconnecting them afterward.

    :param request: WSGIRequest object with a unique `id` set
    """
    current_request.set(request)
    events_queue.set([])

    yield

    # Flush queued webhooks to RQ
    flush_events(events_queue.get())

    # Clear context vars
    current_request.set(None)
    events_queue.set([])
