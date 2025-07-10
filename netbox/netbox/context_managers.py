import traceback
from contextlib import contextmanager

from netbox.context import current_request, events_queue
from netbox.utils import register_request_processor


@register_request_processor
@contextmanager
def event_tracking(request):
    """
    Queue interesting events in memory while processing a request, then flush that queue for processing by the
    events pipline before returning the response.

    :param request: WSGIRequest object with a unique `id` set
    """
    from extras.events import flush_events

    current_request.set(request)
    events_queue.set({})

    yield

    # Flush queued webhooks to RQ
    if events := list(events_queue.get().values()):
        flush_events(events)

    # Clear context vars
    current_request.set(None)
    events_queue.set({})


@contextmanager
def suppress_event_exp(logger=None):
    """
    Suppress exceptions that may occur during event handling.
    """
    try:
        yield
    except Exception as e:
        if logger:
            tb = e.__traceback__
            last_frame = tb.tb_frame if tb else None
            filename = last_frame.f_code.co_filename if last_frame else 'unknown'
            lineno = tb.tb_lineno if tb else 0
            logger.error(f"Error {e.__class__.__name__} in {e.__class__.__name__} at {filename}:{lineno} - {str(e)}")
