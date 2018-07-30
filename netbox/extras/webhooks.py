import datetime

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from extras.models import Webhook
from extras.constants import OBJECTCHANGE_ACTION_CREATE, OBJECTCHANGE_ACTION_DELETE, OBJECTCHANGE_ACTION_UPDATE
from utilities.api import get_serializer_for_model


def enqueue_webhooks(instance, action):
    """
    Find Webhook(s) assigned to this instance + action and enqueue them
    to be processed
    """
    type_create = action == OBJECTCHANGE_ACTION_CREATE
    type_update = action == OBJECTCHANGE_ACTION_UPDATE
    type_delete = action == OBJECTCHANGE_ACTION_DELETE

    # Find assigned webhooks
    obj_type = ContentType.objects.get_for_model(instance.__class__)
    webhooks = Webhook.objects.filter(
        Q(enabled=True) &
        (
            Q(type_create=type_create) |
            Q(type_update=type_update) |
            Q(type_delete=type_delete)
        ) &
        Q(obj_type=obj_type)
    )

    if webhooks:
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
