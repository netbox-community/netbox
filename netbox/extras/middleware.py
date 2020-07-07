import random
import threading
import uuid
from copy import deepcopy
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.db.models.signals import pre_delete, post_save
from django.utils import timezone
from django_prometheus.models import model_deletes, model_inserts, model_updates
from redis.exceptions import RedisError

from extras.utils import is_taggable
from utilities.api import is_api_request
from utilities.querysets import DummyQuerySet
from .choices import ObjectChangeActionChoices
from .models import ObjectChange
from .signals import purge_changelog
from .webhooks import enqueue_webhooks

_thread_locals = threading.local()


def handle_changed_object(sender, instance, **kwargs):
    """
    Fires when an object is created or updated.
    """
    # Queue the object for processing once the request completes
    action = ObjectChangeActionChoices.ACTION_CREATE if kwargs['created'] else ObjectChangeActionChoices.ACTION_UPDATE
    _thread_locals.changed_objects.append(
        (instance, action)
    )


def handle_deleted_object(sender, instance, **kwargs):
    """
    Fires when an object is deleted.
    """
    # Cache custom fields prior to copying the instance
    if hasattr(instance, 'cache_custom_fields'):
        instance.cache_custom_fields()

    # Create a copy of the object being deleted
    copy = deepcopy(instance)

    # Preserve tags
    if is_taggable(instance):
        copy.tags = DummyQuerySet(instance.tags.all())

    # Queue the copy of the object for processing once the request completes
    _thread_locals.changed_objects.append(
        (copy, ObjectChangeActionChoices.ACTION_DELETE)
    )


def purge_objectchange_cache(sender, **kwargs):
    """
    Delete any queued object changes waiting to be written.
    """
    _thread_locals.changed_objects = []


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

        # Initialize an empty list to cache objects being saved.
        _thread_locals.changed_objects = []

        # Assign a random unique ID to the request. This will be used to associate multiple object changes made during
        # the same request.
        request.id = uuid.uuid4()

        # Connect our receivers to the post_save and post_delete signals.
        post_save.connect(handle_changed_object, dispatch_uid='handle_changed_object')
        pre_delete.connect(handle_deleted_object, dispatch_uid='handle_deleted_object')

        # Provide a hook for purging the change cache
        purge_changelog.connect(purge_objectchange_cache)

        # Process the request
        response = self.get_response(request)

        # If the change cache is empty, there's nothing more we need to do.
        if not _thread_locals.changed_objects:
            return response

        # Disconnect our receivers from the post_save and post_delete signals.
        post_save.disconnect(handle_changed_object, dispatch_uid='handle_changed_object')
        pre_delete.disconnect(handle_deleted_object, dispatch_uid='handle_deleted_object')

        # Create records for any cached objects that were changed.
        redis_failed = False
        for instance, action in _thread_locals.changed_objects:

            # Refresh cached custom field values
            if action in [ObjectChangeActionChoices.ACTION_CREATE, ObjectChangeActionChoices.ACTION_UPDATE]:
                if hasattr(instance, 'cache_custom_fields'):
                    instance.cache_custom_fields()

            # Record an ObjectChange if applicable
            if hasattr(instance, 'to_objectchange'):
                objectchange = instance.to_objectchange(action)
                objectchange.user = request.user
                objectchange.request_id = request.id
                objectchange.save()

            # Enqueue webhooks
            try:
                enqueue_webhooks(instance, request.user, request.id, action)
            except RedisError as e:
                if not redis_failed and not is_api_request(request):
                    messages.error(
                        request,
                        "There was an error processing webhooks for this request. Check that the Redis service is "
                        "running and reachable. The full error details were: {}".format(e)
                    )
                    redis_failed = True

            # Increment metric counters
            if action == ObjectChangeActionChoices.ACTION_CREATE:
                model_inserts.labels(instance._meta.model_name).inc()
            elif action == ObjectChangeActionChoices.ACTION_UPDATE:
                model_updates.labels(instance._meta.model_name).inc()
            elif action == ObjectChangeActionChoices.ACTION_DELETE:
                model_deletes.labels(instance._meta.model_name).inc()

        # Housekeeping: 1% chance of clearing out expired ObjectChanges. This applies only to requests which result in
        # one or more changes being logged.
        if settings.CHANGELOG_RETENTION and random.randint(1, 100) == 1:
            cutoff = timezone.now() - timedelta(days=settings.CHANGELOG_RETENTION)
            purged_count, _ = ObjectChange.objects.unrestricted().filter(
                time__lt=cutoff
            ).delete()

        return response
