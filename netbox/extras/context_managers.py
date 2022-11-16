from contextlib import contextmanager

from netbox.context import current_request, webhooks_queue
from .webhooks import flush_webhooks


@contextmanager
def change_logging(request):
    """
    Enable change logging by connecting the appropriate signals to their receivers before code is run, and
    disconnecting them afterward.

    :param request: WSGIRequest object with a unique `id` set
    """
    current_request.set(request)
    webhooks_queue.set([])

    yield

    # Flush queued webhooks to RQ
    flush_webhooks(webhooks_queue.get())

    # Clear context vars
    current_request.set(None)
    webhooks_queue.set([])
