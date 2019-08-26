import random
import threading
import uuid
from datetime import timedelta

from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.utils import timezone
from django_prometheus.models import model_deletes, model_inserts, model_updates

from .constants import (
    OBJECTCHANGE_ACTION_CREATE, OBJECTCHANGE_ACTION_DELETE, OBJECTCHANGE_ACTION_UPDATE,
)
from .models import ObjectChange
from .signals import purge_changelog
from .webhooks import enqueue_webhooks

_thread_locals = threading.local()


def cache_changed_object(sender, instance, **kwargs):
    """
    Cache an object being created or updated for the changelog.
    """
    if hasattr(instance, 'to_objectchange'):
        action = OBJECTCHANGE_ACTION_CREATE if kwargs['created'] else OBJECTCHANGE_ACTION_UPDATE
        objectchange = instance.to_objectchange(action)
        _thread_locals.changed_objects.append(
            (instance, objectchange)
        )


def cache_deleted_object(sender, instance, **kwargs):
    """
    Cache an object being deleted for the changelog.
    """
    if hasattr(instance, 'to_objectchange'):
        objectchange = instance.to_objectchange(OBJECTCHANGE_ACTION_DELETE)
        _thread_locals.changed_objects.append(
            (instance, objectchange)
        )


def purge_objectchange_cache(sender, **kwargs):
    """
    Delete any queued object changes waiting to be written.
    """
    _thread_locals.changed_objects = None


class ObjectChangeMiddleware(object):
    """
    This middleware performs three functions in response to an object being created, updated, or deleted:

        1. Create an ObjectChange to reflect the modification to the object in the changelog.
        2. Enqueue any relevant webhooks.
        3. Increment metric counter for the event type

    The post_save and post_delete signals are employed to catch object modifications, however changes are recorded a bit
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

        # Connect our receivers to the post_save and post_delete signals.
        post_save.connect(cache_changed_object, dispatch_uid='cache_changed_object')
        post_delete.connect(cache_deleted_object, dispatch_uid='cache_deleted_object')

        # Provide a hook for purging the change cache
        purge_changelog.connect(purge_objectchange_cache)

        # Process the request
        response = self.get_response(request)

        # If the change cache has been purged (e.g. due to an exception) abort the logging of all changes resulting from
        # this request.
        if _thread_locals.changed_objects is None:
            return response

        # Create records for any cached objects that were created/updated.
        for obj, objectchange in _thread_locals.changed_objects:

            # Record the change
            objectchange.user = request.user
            objectchange.request_id = request.id
            objectchange.save()

            # Enqueue webhooks
            enqueue_webhooks(obj, request.user, request.id, objectchange.action)

            # Increment metric counters
            if objectchange.action == OBJECTCHANGE_ACTION_CREATE:
                model_inserts.labels(obj._meta.model_name).inc()
            elif objectchange.action == OBJECTCHANGE_ACTION_UPDATE:
                model_updates.labels(obj._meta.model_name).inc()
            elif objectchange.action == OBJECTCHANGE_ACTION_DELETE:
                model_deletes.labels(obj._meta.model_name).inc()

        # Housekeeping: 1% chance of clearing out expired ObjectChanges
        if _thread_locals.changed_objects and settings.CHANGELOG_RETENTION and random.randint(1, 100) == 1:
            cutoff = timezone.now() - timedelta(days=settings.CHANGELOG_RETENTION)
            purged_count, _ = ObjectChange.objects.filter(
                time__lt=cutoff
            ).delete()

        return response
