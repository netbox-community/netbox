from collections import defaultdict
from contextlib import contextmanager

from extras.events import flush_events
from netbox.context import current_request, events_queue, query_cache
from netbox.utils import register_request_processor


@register_request_processor
@contextmanager
def event_tracking(request):
    """
    Queue interesting events in memory while processing a request, then flush that queue for processing by the
    events pipline before returning the response.

    :param request: WSGIRequest object with a unique `id` set
    """
    request_token = current_request.set(request)
    queue_token = events_queue.set({})
    cache_token = query_cache.set(defaultdict(dict))

    try:
        yield

        # Flush queued webhooks to RQ. This is done only if the wrapped block completed successfully; events
        # queued by a failed request or job must not be dispatched.
        if events := list(events_queue.get().values()):
            flush_events(events)

    finally:
        # Restore the previous context vars, whether or not the wrapped block raised an exception
        current_request.reset(request_token)
        events_queue.reset(queue_token)
        query_cache.reset(cache_token)
