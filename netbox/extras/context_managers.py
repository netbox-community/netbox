from contextlib import contextmanager

from django.db.models.signals import m2m_changed, pre_delete, post_save

from extras.signals import clear_webhooks, _clear_webhook_queue, _handle_changed_object, _handle_deleted_object
from utilities.utils import curry
from .webhooks import flush_webhooks


@contextmanager
def change_logging(request):
    """
    Enable change logging by connecting the appropriate signals to their receivers before code is run, and
    disconnecting them afterward.

    :param request: WSGIRequest object with a unique `id` set
    """
    webhook_queue = []

    # Curry signals receivers to pass the current request
    handle_changed_object = curry(_handle_changed_object, request, webhook_queue)
    handle_deleted_object = curry(_handle_deleted_object, request, webhook_queue)
    clear_webhook_queue = curry(_clear_webhook_queue, webhook_queue)

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
    flush_webhooks(webhook_queue)
    del webhook_queue
