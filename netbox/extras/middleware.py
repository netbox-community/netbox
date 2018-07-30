from __future__ import unicode_literals

from datetime import timedelta
import random
import threading
import uuid

from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.utils import timezone

from extras.webhooks import enqueue_webhooks
from .constants import (
    OBJECTCHANGE_ACTION_CREATE, OBJECTCHANGE_ACTION_DELETE, OBJECTCHANGE_ACTION_UPDATE,
    WEBHOOK_MODELS
)
from .models import ObjectChange


_thread_locals = threading.local()


def mark_object_changed(instance, **kwargs):
    """
    Mark an object as having been created, saved, or updated. At the end of the request, this change will be recorded
    and/or associated webhooks fired. We have to wait until the *end* of the request to the serialize the object,
    because related fields like tags and custom fields have not yet been updated when the post_save signal is emitted.
    """

    # Determine what action is being performed. The post_save signal sends a `created` boolean, whereas post_delete
    # does not.
    if 'created' in kwargs:
        action = OBJECTCHANGE_ACTION_CREATE if kwargs['created'] else OBJECTCHANGE_ACTION_UPDATE
    else:
        action = OBJECTCHANGE_ACTION_DELETE

    _thread_locals.changed_objects.append((instance, action))


class ObjectChangeMiddleware(object):
    """
    This middleware intercepts all requests to connects object signals to the Django runtime. The signals collect all
    changed objects into a local thread by way of the `mark_object_changed()` receiver. At the end of the request,
    the middleware iterates over the objects to process change events like Change Logging and Webhooks.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Initialize the list of changed objects
        _thread_locals.changed_objects = []

        # Assign a random unique ID to the request. This will be used to associate multiple object changes made during
        # the same request.
        request.id = uuid.uuid4()

        # Connect mark_object_changed to the post_save and post_delete receivers
        post_save.connect(mark_object_changed, dispatch_uid='record_object_saved')
        post_delete.connect(mark_object_changed, dispatch_uid='record_object_deleted')

        # Process the request
        response = self.get_response(request)

        # Perform change logging and fire Webhook signals
        for obj, action in _thread_locals.changed_objects:
            # Log object changes
            if obj.pk and hasattr(obj, 'log_change'):
                obj.log_change(request.user, request.id, action)

            # Enqueue Webhooks if they are enabled
            if settings.WEBHOOKS_ENABLED and obj.__class__.__name__.lower() in WEBHOOK_MODELS:
                enqueue_webhooks(obj, action)

        # Housekeeping: 1% chance of clearing out expired ObjectChanges
        if _thread_locals.changed_objects and settings.CHANGELOG_RETENTION and random.randint(1, 100) == 1:
            cutoff = timezone.now() - timedelta(days=settings.CHANGELOG_RETENTION)
            purged_count, _ = ObjectChange.objects.filter(
                time__lt=cutoff
            ).delete()

        return response
