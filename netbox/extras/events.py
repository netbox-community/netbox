import logging
import sys

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django_rq import get_queue

from netbox.config import get_config
from netbox.constants import RQ_QUEUE_DEFAULT
from netbox.registry import registry
from utilities.api import get_serializer_for_model
from utilities.rqworker import get_rq_retry
from utilities.utils import serialize_object
from .choices import *
from .models import EventRule
from .utils import process_event_rules

logger = logging.getLogger('netbox.events_processor')


def serialize_for_event(instance):
    """
    Return a serialized representation of the given instance suitable for use in a queued event.
    """
    serializer_class = get_serializer_for_model(instance.__class__)
    serializer_context = {
        'request': None,
    }
    serializer = serializer_class(instance, context=serializer_context)

    return serializer.data


def get_snapshots(instance, action):
    snapshots = {
        'prechange': getattr(instance, '_prechange_snapshot', None),
        'postchange': None,
    }
    if action != ObjectChangeActionChoices.ACTION_DELETE:
        # Use model's serialize_object() method if defined; fall back to serialize_object() utility function
        if hasattr(instance, 'serialize_object'):
            snapshots['postchange'] = instance.serialize_object()
        else:
            snapshots['postchange'] = serialize_object(instance)

    return snapshots


def enqueue_object(queue, instance, user, request_id, action):
    """
    Enqueue a serialized representation of a created/updated/deleted object for the processing of
    events once the request has completed.
    """
    # Determine whether this type of object supports event rules
    app_label = instance._meta.app_label
    model_name = instance._meta.model_name
    if model_name not in registry['model_features']['webhooks'].get(app_label, []):
        return

    queue.append({
        'content_type': ContentType.objects.get_for_model(instance),
        'object_id': instance.pk,
        'event': action,
        'data': serialize_for_event(instance),
        'snapshots': get_snapshots(instance, action),
        'username': user.username,
        'request_id': request_id
    })


def process_event_queue(queue):
    """
    Flush a list of object representation to RQ for EventRule processing.
    """
    events_cache = {
        'type_create': {},
        'type_update': {},
        'type_delete': {},
    }

    for data in queue:
        action_flag = {
            ObjectChangeActionChoices.ACTION_CREATE: 'type_create',
            ObjectChangeActionChoices.ACTION_UPDATE: 'type_update',
            ObjectChangeActionChoices.ACTION_DELETE: 'type_delete',
        }[data['event']]
        content_type = data['content_type']

        # Cache applicable Event Rules
        if content_type not in events_cache[action_flag]:
            events_cache[action_flag][content_type] = EventRule.objects.filter(
                **{action_flag: True},
                content_types=content_type,
                enabled=True
            )
        event_rules = events_cache[action_flag][content_type]

        process_event_rules(event_rules, data['event'], data['data'], data['username'], data['snapshots'], data['request_id'])


def import_module(name):
    __import__(name)
    return sys.modules[name]


def module_member(name):
    mod, member = name.rsplit(".", 1)
    module = import_module(mod)
    return getattr(module, member)


def flush_events(queue):
    """
    Flush a list of object representation to RQ for webhook processing.
    """
    if queue:
        for name in settings.EVENTS_PIPELINE:
            try:
                func = module_member(name)
                func(queue)
            except Exception as e:
                logger.error(f"Cannot import events pipeline {name} error: {e}")
