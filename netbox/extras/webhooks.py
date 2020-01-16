import datetime

from django.contrib.contenttypes.models import ContentType

from extras.models import Webhook
from utilities.api import get_serializer_for_model
from .choices import *
from .constants import *


def enqueue_webhooks(instance, user, request_id, action):
    """
    Find Webhook(s) assigned to this instance + action and enqueue them
    to be processed
    """
    obj_type = ContentType.objects.get_for_model(instance.__class__)

    webhook_models = ContentType.objects.filter(WEBHOOK_MODELS)
    if obj_type not in webhook_models:
        return

    # Retrieve any applicable Webhooks
    action_flag = {
        ObjectChangeActionChoices.ACTION_CREATE: 'type_create',
        ObjectChangeActionChoices.ACTION_UPDATE: 'type_update',
        ObjectChangeActionChoices.ACTION_DELETE: 'type_delete',
    }[action]
    webhooks = Webhook.objects.filter(obj_type=obj_type, enabled=True, **{action_flag: True})

    if webhooks.exists():
        # Get the Model's API serializer class and serialize the object
        serializer_class = get_serializer_for_model(instance.__class__)
        serializer_context = {
            'request': None,
        }
        serializer = serializer_class(instance, context=serializer_context)

        # We must only import django_rq if the Webhooks feature is enabled.
        # Only if we have gotten to ths point, is the feature enabled
        from django_rq import get_queue
        webhook_queue = get_queue('default')

        # enqueue the webhooks:
        for webhook in webhooks:
            webhook_queue.enqueue(
                "extras.webhooks_worker.process_webhook",
                webhook,
                serializer.data,
                instance._meta.model_name,
                action,
                str(datetime.datetime.now()),
                user.username,
                request_id
            )
