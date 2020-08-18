import uuid

from django.db.models.signals import m2m_changed, pre_delete, post_save

from utilities.utils import curry
from .signals import _handle_changed_object, _handle_deleted_object


class ObjectChangeMiddleware(object):
    """
    This middleware performs three functions in response to an object being created, updated, or deleted:

        1. Create an ObjectChange to reflect the modification to the object in the changelog.
        2. Enqueue any relevant webhooks.
        3. Increment the metric counter for the event type.

    The post_save and post_delete signals are employed to catch object modifications, however changes are recorded a bit
    differently for each. Objects being saved are cached into thread-local storage for action *after* the response has
    completed. This ensures that serialization of the object is performed only after any related objects (e.g. tags)
    have been created. Conversely, deletions are acted upon immediately, so that the serialized representation of the
    object is recorded before it (and any related objects) are actually deleted from the database.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Assign a random unique ID to the request. This will be used to associate multiple object changes made during
        # the same request.
        request.id = uuid.uuid4()

        # Curry signals receivers to pass the current request
        handle_changed_object = curry(_handle_changed_object, request)
        handle_deleted_object = curry(_handle_deleted_object, request)

        # Connect our receivers to the post_save and post_delete signals.
        post_save.connect(handle_changed_object, dispatch_uid='handle_changed_object')
        m2m_changed.connect(handle_changed_object, dispatch_uid='handle_changed_object')
        pre_delete.connect(handle_deleted_object, dispatch_uid='handle_deleted_object')

        # Process the request
        response = self.get_response(request)

        # Disconnect change logging signals. This is necessary to avoid recording any errant
        # changes during test cleanup.
        post_save.disconnect(handle_changed_object, dispatch_uid='handle_changed_object')
        m2m_changed.disconnect(handle_changed_object, dispatch_uid='handle_changed_object')
        pre_delete.disconnect(handle_deleted_object, dispatch_uid='handle_deleted_object')

        return response
