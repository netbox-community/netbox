from contextlib import contextmanager

from django.db.models.signals import m2m_changed, pre_delete, post_save

from extras.signals import clear_webhooks, clear_webhook_queue, handle_changed_object, handle_deleted_object
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

    # Connect our receivers to the post_save and post_delete signals.
    post_save.connect(handle_changed_object, dispatch_uid='handle_changed_object')
    m2m_changed.connect(handle_changed_object, dispatch_uid='handle_changed_object')
    pre_delete.connect(handle_deleted_object, dispatch_uid='handle_deleted_object')
    clear_webhooks.connect(clear_webhook_queue, dispatch_uid='clear_webhook_queue')

    yield

    # Disconnect change logging signals. This is necessary to avoid recording any errant
    # changes during test cleanup.
    post_save.disconnect(handle_changed_object, dispatch_uid='handle_changed_object')
    m2m_changed.disconnect(handle_changed_object, dispatch_uid='handle_changed_object')
    pre_delete.disconnect(handle_deleted_object, dispatch_uid='handle_deleted_object')
    clear_webhooks.disconnect(clear_webhook_queue, dispatch_uid='clear_webhook_queue')

    # Flush queued webhooks to RQ
    flush_webhooks(webhooks_queue.get())

    # Clear context vars
    current_request.set(None)
    webhooks_queue.set([])
