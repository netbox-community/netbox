import datetime

from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from extras.models import Webhook
from extras.constants import OBJECTCHANGE_ACTION_CREATE, OBJECTCHANGE_ACTION_DELETE, OBJECTCHANGE_ACTION_UPDATE
from utilities.api import get_serializer_for_model
from .constants import WEBHOOK_MODELS


def enqueue_webhooks(instance, action):
    """
    Find Webhook(s) assigned to this instance + action and enqueue them
    to be processed
    """
    if not settings.WEBHOOKS_ENABLED or instance._meta.model_name not in WEBHOOK_MODELS:
        return

    # Retrieve any applicable Webhooks
    action_flag = {
        OBJECTCHANGE_ACTION_CREATE: 'type_create',
        OBJECTCHANGE_ACTION_UPDATE: 'type_update',
        OBJECTCHANGE_ACTION_DELETE: 'type_delete',
    }[action]
    obj_type = ContentType.objects.get_for_model(instance.__class__)
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
                instance.__class__,
                action,
                str(datetime.datetime.now())
            )
