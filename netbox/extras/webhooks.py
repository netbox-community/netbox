import hashlib
import hmac

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django_rq import get_queue

from utilities.api import get_serializer_for_model
from .choices import *
from .models import Webhook
from .registry import registry


def generate_signature(request_body, secret):
    """
    Return a cryptographic signature that can be used to verify the authenticity of webhook data.
    """
    hmac_prep = hmac.new(
        key=secret.encode('utf8'),
        msg=request_body,
        digestmod=hashlib.sha512
    )
    return hmac_prep.hexdigest()


def enqueue_webhooks(instance, user, request_id, action):
    """
    Find Webhook(s) assigned to this instance + action and enqueue them
    to be processed
    """
    # Determine whether this type of object supports webhooks
    app_label = instance._meta.app_label
    model_name = instance._meta.model_name
    if model_name not in registry['model_features']['webhooks'].get(app_label, []):
        return

    # Retrieve any applicable Webhooks
    content_type = ContentType.objects.get_for_model(instance)
    action_flag = {
        ObjectChangeActionChoices.ACTION_CREATE: 'type_create',
        ObjectChangeActionChoices.ACTION_UPDATE: 'type_update',
        ObjectChangeActionChoices.ACTION_DELETE: 'type_delete',
    }[action]
    webhooks = Webhook.objects.filter(content_types=content_type, enabled=True, **{action_flag: True})

    if webhooks.exists():
        # Get the Model's API serializer class and serialize the object
        serializer_class = get_serializer_for_model(instance.__class__)
        serializer_context = {
            'request': None,
        }
        serializer = serializer_class(instance, context=serializer_context)

        # Enqueue the webhooks
        webhook_queue = get_queue('default')
        for webhook in webhooks:
            webhook_queue.enqueue(
                "extras.webhooks_worker.process_webhook",
                webhook,
                serializer.data,
                instance._meta.model_name,
                action,
                str(timezone.now()),
                user.username,
                request_id
            )
