from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _
from django_rq import get_queue

from core.models import Job
from netbox.config import get_config
from netbox.constants import RQ_QUEUE_DEFAULT
from netbox.registry import registry
from utilities.api import get_serializer_for_model
from utilities.rqworker import get_rq_retry
from utilities.serialization import serialize_object
from .choices import *
from .models import EventRule

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
    if model_name not in registry['model_features']['event_rules'].get(app_label, []):
        return

    assert instance.pk is not None
    key = f'{app_label}.{model_name}:{instance.pk}'
    if key in queue:
        queue[key]['data'] = serialize_for_event(instance)
        queue[key]['snapshots']['postchange'] = get_snapshots(instance, action)['postchange']
    else:
        queue[key] = {
            'content_type': ContentType.objects.get_for_model(instance),
            'object_id': instance.pk,
            'event': action,
            'data': serialize_for_event(instance),
            'snapshots': get_snapshots(instance, action),
            'username': user.username,
            'request_id': request_id
        }


def process_event_rules(event_rules, model_name, event, data, username=None, snapshots=None, request_id=None):
    if username:
        user = get_user_model().objects.get(username=username)
    else:
        user = None

    for event_rule in event_rules:

        # Evaluate event rule conditions (if any)
        if not event_rule.eval_conditions(data):
            continue

        # Webhooks
        if event_rule.action_type == EventRuleActionChoices.WEBHOOK:

            # Select the appropriate RQ queue
            queue_name = get_config().QUEUE_MAPPINGS.get('webhook', RQ_QUEUE_DEFAULT)
            rq_queue = get_queue(queue_name)

            # Compile the task parameters
            params = {
                "event_rule": event_rule,
                "model_name": model_name,
                "event": event,
                "data": data,
                "snapshots": snapshots,
                "timestamp": timezone.now().isoformat(),
                "username": username,
                "retry": get_rq_retry()
            }
            if snapshots:
                params["snapshots"] = snapshots
            if request_id:
                params["request_id"] = request_id

            # Enqueue the task
            rq_queue.enqueue(
                "extras.webhooks.send_webhook",
                **params
            )

        # Scripts
        elif event_rule.action_type == EventRuleActionChoices.SCRIPT:
            # Resolve the script from action parameters
            script = event_rule.action_object.python_class()

            # Enqueue a Job to record the script's execution
            Job.enqueue(
                "extras.scripts.run_script",
                instance=event_rule.action_object,
                name=script.name,
                user=user,
                data=data
            )

        else:
            raise ValueError(_("Unknown action type for an event rule: {action_type}").format(
                action_type=event_rule.action_type
            ))


def process_event_queue(events):
    """
    Flush a list of object representation to RQ for EventRule processing.
    """
    events_cache = {
        'type_create': {},
        'type_update': {},
        'type_delete': {},
    }

    for data in events:
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
                object_types=content_type,
                enabled=True
            )
        event_rules = events_cache[action_flag][content_type]

        process_event_rules(
            event_rules, content_type.model, data['event'], data['data'], data['username'],
            snapshots=data['snapshots'], request_id=data['request_id']
        )


def flush_events(events):
    """
    Flush a list of object representations to RQ for event processing.
    """
    if events:
        for name in settings.EVENTS_PIPELINE:
            try:
                func = import_string(name)
                func(events)
            except Exception as e:
                logger.error(_("Cannot import events pipeline {name} error: {error}").format(name=name, error=e))
