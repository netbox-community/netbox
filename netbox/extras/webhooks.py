import time
from importlib import import_module

from django.db.models.signals import post_save, post_delete
from django.conf import settings
from django.core.cache import caches
from django.db.models import Q
from django.dispatch import Signal
from django.contrib.contenttypes.models import ContentType

from utilities.utils import dynamic_import
from extras.models import Webhook


def enqueue_webhooks(webhooks, model_class, data, event, signal_received_timestamp):
    """
    Serialize data and enqueue webhooks
    """
    serializer_context = {
        'request': None,
    }

    if isinstance(data, list):
        serializer_property = data[0].serializer
        serializer_cls = dynamic_import(serializer_property)
        serialized_data = serializer_cls(data, context=serializer_context, many=True)
    else:
        serializer_property = data.serializer
        serializer_cls = dynamic_import(serializer_property)
        serialized_data = serializer_cls(data, context=serializer_context)

    from django_rq import get_queue
    webhook_queue = get_queue('default')

    for webhook in webhooks:
        webhook_queue.enqueue("extras.webhooks_worker.process_webhook",
                              webhook,
                              serialized_data.data,
                              model_class,
                              event,
                              signal_received_timestamp)


def post_save_receiver(sender, instance, created, **kwargs):
    """
    Receives post_save signals from registered models. If the webhook
    backend is enabled, queue any webhooks that apply to the event.
    """
    if settings.WEBHOOKS_ENABLED:
        signal_received_timestamp = time.time()
        # look for any webhooks that match this event
        updated = not created
        obj_type = ContentType.objects.get_for_model(sender)
        webhooks = Webhook.objects.filter(
            Q(enabled=True) &
            (
                Q(type_create=created) |
                Q(type_update=updated)
            ) &
            Q(obj_type=obj_type)
        )
        event = 'created' if created else 'updated'
        if webhooks:
            enqueue_webhooks(webhooks, sender, instance, event, signal_received_timestamp)


def post_delete_receiver(sender, instance, **kwargs):
    """
    Receives post_delete signals from registered models. If the webhook
    backend is enabled, queue any webhooks that apply to the event.
    """
    if settings.WEBHOOKS_ENABLED:
        signal_received_timestamp = time.time()
        obj_type = ContentType.objects.get_for_model(sender)
        # look for any webhooks that match this event
        webhooks = Webhook.objects.filter(enabled=True, type_delete=True, obj_type=obj_type)
        if webhooks:
            enqueue_webhooks(webhooks, sender, instance, 'deleted', signal_received_timestamp)


def bulk_operation_receiver(sender, **kwargs):
    """
    Receives bulk_operation_signal signals from registered models. If the webhook
    backend is enabled, queue any webhooks that apply to the event.
    """
    if settings.WEBHOOKS_ENABLED:
        signal_received_timestamp = time.time()
        event = kwargs['event']
        obj_type = ContentType.objects.get_for_model(sender)
        # look for any webhooks that match this event
        if event == 'created':
            webhooks = Webhook.objects.filter(enabled=True, type_create=True, obj_type=obj_type)
        elif event == 'updated':
            webhooks = Webhook.objects.filter(enabled=True, type_update=True, obj_type=obj_type)
        elif event == 'deleted':
            webhooks = Webhook.objects.filter(enabled=True, type_delete=True, obj_type=obj_type)
        else:
            webhooks = None

        if webhooks:
            enqueue_webhooks(webhooks, sender, list(kwargs['instances']), event, signal_received_timestamp)


# the bulk operation signal is used to overcome signals not being sent for bulk model changes
bulk_operation_signal = Signal(providing_args=["instances", "event"])
bulk_operation_signal.connect(bulk_operation_receiver)


def register_signals(senders):
    """
    Take a list of senders (Models) and register them to the post_save
    and post_delete signal receivers.
    """
    if settings.WEBHOOKS_ENABLED:
        # only register signals if the backend is enabled
        # this reduces load by not firing signals if the
        # webhook backend feature is disabled

        for sender in senders:
            post_save.connect(post_save_receiver, sender=sender)
            post_delete.connect(post_delete_receiver, sender=sender)
