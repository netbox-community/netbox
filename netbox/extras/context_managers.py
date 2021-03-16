from contextlib import contextmanager

from django.db.models.signals import m2m_changed, pre_delete, post_save

from extras.signals import _handle_changed_object, _handle_deleted_object
from utilities.utils import curry


@contextmanager
def change_logging(request):
    """
    Enable change logging by connecting the appropriate signals to their receivers before code is run, and
    disconnecting them afterward.

    :param request: WSGIRequest object with a unique `id` set
    """
    # Curry signals receivers to pass the current request
    handle_changed_object = curry(_handle_changed_object, request)
    handle_deleted_object = curry(_handle_deleted_object, request)

    # Connect our receivers to the post_save and post_delete signals.
    post_save.connect(handle_changed_object, dispatch_uid='handle_changed_object')
    m2m_changed.connect(handle_changed_object, dispatch_uid='handle_changed_object')
    pre_delete.connect(handle_deleted_object, dispatch_uid='handle_deleted_object')

    yield

    # Disconnect change logging signals. This is necessary to avoid recording any errant
    # changes during test cleanup.
    post_save.disconnect(handle_changed_object, dispatch_uid='handle_changed_object')
    m2m_changed.disconnect(handle_changed_object, dispatch_uid='handle_changed_object')
    pre_delete.disconnect(handle_deleted_object, dispatch_uid='handle_deleted_object')
