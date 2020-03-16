import hashlib
import hmac

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from extras.models import Webhook
from utilities.api import get_serializer_for_model
from .choices import *
from .constants import *
from .utils import FeatureQuery


def generate_signature(request_body, secret):
    """
    Return a cryptographic signature that can be used to verify the authenticity of webhook data.
    """
    hmac_prep = hmac.new(
        key=secret.encode('utf8'),
        msg=request_body.encode('utf8'),
        digestmod=hashlib.sha512
    )
    return hmac_prep.hexdigest()


def enqueue_webhooks(instance, user, request_id, action):
    """
    Find Webhook(s) assigned to this instance + action and enqueue them
    to be processed
    """
    obj_type = ContentType.objects.get_for_model(instance.__class__)

    webhook_models = ContentType.objects.filter(FeatureQuery('webhooks').get_query())
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
                str(timezone.now()),
                user.username,
                request_id
            )
