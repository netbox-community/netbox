from __future__ import unicode_literals

from datetime import timedelta
import random
import threading
import uuid

from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.utils import timezone
from django.utils.functional import curry

from extras.webhooks import enqueue_webhooks
from .constants import (
    OBJECTCHANGE_ACTION_CREATE, OBJECTCHANGE_ACTION_DELETE, OBJECTCHANGE_ACTION_UPDATE,
)
from .models import ObjectChange


_thread_locals = threading.local()


def cache_changed_object(instance, **kwargs):

    action = OBJECTCHANGE_ACTION_CREATE if kwargs['created'] else OBJECTCHANGE_ACTION_UPDATE

    # Cache the object for further processing was the response has completed.
    _thread_locals.changed_objects.append(
        (instance, action)
    )


def _record_object_deleted(request, instance, **kwargs):

    # Record that the object was deleted.
    if hasattr(instance, 'log_change'):
        instance.log_change(request.user, request.id, OBJECTCHANGE_ACTION_DELETE)

    enqueue_webhooks(instance, OBJECTCHANGE_ACTION_DELETE)


class ObjectChangeMiddleware(object):
    """
    This middleware performs two functions in response to an object being created, updated, or deleted:

        1. Create an ObjectChange to reflect the modification to the object in the changelog.
        2. Enqueue any relevant webhooks.

    The post_save and pre_delete signals are employed to catch object modifications, however changes are recorded a bit
    differently for each. Objects being saved are cached into thread-local storage for action *after* the response has
    completed. This ensures that serialization of the object is performed only after any related objects (e.g. tags)
    have been created. Conversely, deletions are acted upon immediately, so that the serialized representation of the
    object is recorded before it (and any related objects) are actually deleted from the database.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Initialize an empty list to cache objects being saved.
        _thread_locals.changed_objects = []

        # Assign a random unique ID to the request. This will be used to associate multiple object changes made during
        # the same request.
        request.id = uuid.uuid4()

        # Signals don't include the request context, so we're currying it into the pre_delete function ahead of time.
        record_object_deleted = curry(_record_object_deleted, request)

        # Connect our receivers to the post_save and pre_delete signals.
        post_save.connect(cache_changed_object, dispatch_uid='record_object_saved')
        post_delete.connect(record_object_deleted, dispatch_uid='record_object_deleted')

        # Process the request
        response = self.get_response(request)

        # Create records for any cached objects that were created/updated.
        for obj, action in _thread_locals.changed_objects:

            # Record the change
            if hasattr(obj, 'log_change'):
                obj.log_change(request.user, request.id, action)

            # Enqueue webhooks
            enqueue_webhooks(obj, action)

        # Housekeeping: 1% chance of clearing out expired ObjectChanges
        if _thread_locals.changed_objects and settings.CHANGELOG_RETENTION and random.randint(1, 100) == 1:
            cutoff = timezone.now() - timedelta(days=settings.CHANGELOG_RETENTION)
            purged_count, _ = ObjectChange.objects.filter(
                time__lt=cutoff
            ).delete()

        return response
