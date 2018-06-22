from __future__ import unicode_literals

from datetime import timedelta
import random
import uuid

from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.utils import timezone
from django.utils.functional import curry, SimpleLazyObject

from .constants import OBJECTCHANGE_ACTION_CREATE, OBJECTCHANGE_ACTION_DELETE, OBJECTCHANGE_ACTION_UPDATE
from .models import ObjectChange


def record_object_change(user, request_id, instance, **kwargs):
    """
    Create an ObjectChange in response to an object being created or deleted.
    """
    if not hasattr(instance, 'log_change'):
        return

    # Determine what action is being performed. The post_save signal sends a `created` boolean, whereas post_delete
    # does not.
    if 'created' in kwargs:
        action = OBJECTCHANGE_ACTION_CREATE if kwargs['created'] else OBJECTCHANGE_ACTION_UPDATE
    else:
        action = OBJECTCHANGE_ACTION_DELETE

    instance.log_change(user, request_id, action)

    # 1% chance of clearing out expired ObjectChanges
    if settings.CHANGELOG_RETENTION and random.randint(1, 100) == 1:
        cutoff = timezone.now() - timedelta(days=settings.CHANGELOG_RETENTION)
        purged_count, _ = ObjectChange.objects.filter(
            time__lt=cutoff
        ).delete()


class ChangeLoggingMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        def get_user(request):
            return request.user

        # DRF employs a separate authentication mechanism outside Django's normal request/response cycle, so calling
        # request.user in middleware will always return AnonymousUser for API requests. To work around this, we point
        # to a lazy object that doesn't resolve the user until after DRF's authentication has been called. For more
        # detail, see https://stackoverflow.com/questions/26240832/
        user = SimpleLazyObject(lambda: get_user(request))

        request_id = uuid.uuid4()

        # Django doesn't provide any request context with the post_save/post_delete signals, so we curry
        # record_object_change() to include the user associated with the current request.
        _record_object_change = curry(record_object_change, user, request_id)

        post_save.connect(_record_object_change, dispatch_uid='record_object_saved')
        post_delete.connect(_record_object_change, dispatch_uid='record_object_deleted')

        return self.get_response(request)
