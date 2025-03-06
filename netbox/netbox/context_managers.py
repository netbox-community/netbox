from contextlib import contextmanager

from netbox.context import current_request, events_queue
from netbox.utils import register_request_processor
from extras.events import flush_events


@register_request_processor
@contextmanager
def event_tracking(request):
    """
    Queue interesting events in memory while processing a request, then flush that queue for processing by the
    events pipline before returning the response.

    :param request: WSGIRequest object with a unique `id` set
    """
    current_request.set(request)
    events_queue.set({})

    yield

    # Flush queued webhooks to RQ
    if events := list(events_queue.get().values()):
        flush_events(events)

    # Clear context vars
    current_request.set(None)
    events_queue.set({})
