import hashlib
import hmac

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django_rq import get_queue

from utilities.api import get_serializer_for_model
from utilities.utils import serialize_object
from .choices import *
from .models import Webhook
from .registry import registry


def serialize_for_webhook(instance):
    """
    Return a serialized representation of the given instance suitable for use in a webhook.
    """
    serializer_class = get_serializer_for_model(instance.__class__)
    serializer_context = {
        'request': None,
    }
    serializer = serializer_class(instance, context=serializer_context)

    return serializer.data


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


def enqueue_object(queue, instance, user, request_id, action):
    """
    Enqueue a serialized representation of a created/updated/deleted object for the processing of
    webhooks once the request has completed.
    """
    # Determine whether this type of object supports webhooks
    app_label = instance._meta.app_label
    model_name = instance._meta.model_name
    if model_name not in registry['model_features']['webhooks'].get(app_label, []):
        return

    # Gather pre- and post-change snapshots
    snapshots = {
        'prechange': getattr(instance, '_prechange_snapshot', None),
        'postchange': serialize_object(instance) if action != ObjectChangeActionChoices.ACTION_DELETE else None,
    }

    queue.append({
        'content_type': ContentType.objects.get_for_model(instance),
        'object_id': instance.pk,
        'event': action,
        'data': serialize_for_webhook(instance),
        'snapshots': snapshots,
        'username': user.username,
        'request_id': request_id
    })


def flush_webhooks(queue):
    """
    Flush a list of object representation to RQ for webhook processing.
    """
    rq_queue = get_queue('default')

    for data in queue:

        # Collect Webhooks that apply for this object and action
        content_type = data['content_type']
        action_flag = {
            ObjectChangeActionChoices.ACTION_CREATE: 'type_create',
            ObjectChangeActionChoices.ACTION_UPDATE: 'type_update',
            ObjectChangeActionChoices.ACTION_DELETE: 'type_delete',
        }[data['event']]
        # TODO: Cache these so we're not calling multiple times for bulk operations
        webhooks = Webhook.objects.filter(content_types=content_type, enabled=True, **{action_flag: True})

        for webhook in webhooks:
            rq_queue.enqueue(
                "extras.webhooks_worker.process_webhook",
                webhook=webhook,
                model_name=content_type.model,
                event=data['event'],
                data=data['data'],
                snapshots=data['snapshots'],
                timestamp=str(timezone.now()),
                username=data['username'],
                request_id=data['request_id']
            )
