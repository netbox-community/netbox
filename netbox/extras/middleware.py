from __future__ import unicode_literals

import json

from django.core.serializers import serialize
from django.db.models.signals import post_delete, post_save
from django.utils.functional import curry, SimpleLazyObject

from utilities.models import ChangeLoggedModel
from .constants import OBJECTCHANGE_ACTION_CREATE, OBJECTCHANGE_ACTION_DELETE, OBJECTCHANGE_ACTION_UPDATE
from .models import ObjectChange


def record_object_change(user, instance, **kwargs):
    """
    Create an ObjectChange in response to an object being created or deleted.
    """
    if not isinstance(instance, ChangeLoggedModel):
        return

    # Determine what action is being performed. The post_save signal sends a `created` boolean, whereas post_delete
    # does not.
    if 'created' in kwargs:
        action = OBJECTCHANGE_ACTION_CREATE if kwargs['created'] else OBJECTCHANGE_ACTION_UPDATE
    else:
        action = OBJECTCHANGE_ACTION_DELETE

    # Serialize the object using Django's built-in JSON serializer, then extract only the `fields` dict.
    json_str = serialize('json', [instance])
    object_data = json.loads(json_str)[0]['fields']

    ObjectChange(
        user=user,
        changed_object=instance,
        action=action,
        object_data=object_data
    ).save()


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

        # Django doesn't provide any request context with the post_save/post_delete signals, so we curry
        # record_object_change() to include the user associated with the current request.
        _record_object_change = curry(record_object_change, user)

        post_save.connect(_record_object_change, dispatch_uid='record_object_saved')
        post_delete.connect(_record_object_change, dispatch_uid='record_object_deleted')

        return self.get_response(request)
