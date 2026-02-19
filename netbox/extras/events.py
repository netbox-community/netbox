import logging
from collections import UserDict, defaultdict

from django.conf import settings
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _
from django_rq import get_queue

from core.events import *
from core.models import ObjectType
from netbox.config import get_config
from netbox.constants import RQ_QUEUE_DEFAULT
from netbox.models.features import has_feature
from utilities.api import get_serializer_for_model
from utilities.request import copy_safe_request
from utilities.rqworker import get_rq_retry
from utilities.serialization import serialize_object

from .choices import EventRuleActionChoices
from .models import EventRule

logger = logging.getLogger('netbox.events_processor')


class EventContext(UserDict):
    """
    A custom dictionary that automatically serializes its associated object on demand.
    """

    # We're emulating a dictionary here (rather than using a custom class) because prior to NetBox v4.5.2, events were
    # queued as dictionaries for processing by handles in EVENTS_PIPELINE. We need to avoid introducing any breaking
    # changes until a suitable minor release.
    def __getitem__(self, item):
        if item == 'data' and 'data' not in self:
            data = serialize_for_event(self['object'])
            self.__setitem__('data', data)
        return super().__getitem__(item)


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


def get_snapshots(instance, event_type):
    """
    Return a dictionary of pre- and post-change snapshots for the given instance.
    """
    if event_type == OBJECT_DELETED:
        # Post-change snapshot must be empty for deleted objects
        postchange_snapshot = None
    elif hasattr(instance, '_postchange_snapshot'):
        # Use the cached post-change snapshot if one is available
        postchange_snapshot = instance._postchange_snapshot
    elif hasattr(instance, 'serialize_object'):
        # Use model's serialize_object() method if defined
        postchange_snapshot = instance.serialize_object()
    else:
        # Fall back to the serialize_object() utility function
        postchange_snapshot = serialize_object(instance)

    return {
        'prechange': getattr(instance, '_prechange_snapshot', None),
        'postchange': postchange_snapshot,
    }


def enqueue_event(queue, instance, request, event_type):
    """
    Enqueue a serialized representation of a created/updated/deleted object for the processing of
    events once the request has completed.
    """
    # Bail if this type of object does not support event rules
    if not has_feature(instance, 'event_rules'):
        return

    app_label = instance._meta.app_label
    model_name = instance._meta.model_name

    assert instance.pk is not None
    key = f'{app_label}.{model_name}:{instance.pk}'
    if key in queue:
        queue[key]['snapshots']['postchange'] = get_snapshots(instance, event_type)['postchange']
        # If the object is being deleted, update any prior "update" event to "delete"
        if event_type == OBJECT_DELETED:
            queue[key]['event_type'] = event_type
    else:
        queue[key] = EventContext(
            object_type=ObjectType.objects.get_for_model(instance),
            object_id=instance.pk,
            object=instance,
            event_type=event_type,
            snapshots=get_snapshots(instance, event_type),
            request=request,
            user=request.user,
            # Legacy request attributes for backward compatibility
            username=request.user.username,  # DEPRECATED, will be removed in NetBox v4.7.0
            request_id=request.id,           # DEPRECATED, will be removed in NetBox v4.7.0
        )
    # Force serialization of objects prior to them actually being deleted
    if event_type == OBJECT_DELETED:
        queue[key]['data'] = serialize_for_event(instance)


def process_event_rules(event_rules, object_type, event):
    """
    Process a list of EventRules against an event.

    Notes on event sources:
    - Object change events (created/updated/deleted) are enqueued via
      enqueue_event() during an HTTP request.
      These events include a request object and legacy request
      attributes (e.g. username, request_id) for backward compatibility.
    - Job lifecycle events (JOB_STARTED/JOB_COMPLETED) are emitted by
      job_start/job_end signal handlers and may not include a request
      context.
      Consumers must not assume that fields like `username` are always
      present.
    """

    for event_rule in event_rules:

        # Evaluate event rule conditions (if any)
        if not event_rule.eval_conditions(event['data']):
            continue

        # Compile event data
        event_data = event_rule.action_data or {}
        event_data.update(event['data'])

        # Webhooks
        if event_rule.action_type == EventRuleActionChoices.WEBHOOK:

            # Select the appropriate RQ queue
            queue_name = get_config().QUEUE_MAPPINGS.get('webhook', RQ_QUEUE_DEFAULT)
            rq_queue = get_queue(queue_name)

            # For job lifecycle events, `username` may be absent because
            # there is no request context.
            # Prefer the associated user object when present, falling
            # back to the legacy username attribute.
            username = getattr(event.get('user'), 'username', None) or event.get('username')

            # Compile the task parameters
            params = {
                'event_rule': event_rule,
                'object_type': object_type,
                'event_type': event['event_type'],
                'data': event_data,
                'snapshots': event.get('snapshots'),
                'timestamp': timezone.now().isoformat(),
                'username': username,
                'retry': get_rq_retry(),
            }
            if 'request' in event:
                # Exclude FILES - webhooks don't need uploaded files,
                # which can cause pickle errors with Pillow.
                params['request'] = copy_safe_request(event['request'], include_files=False)

            # Enqueue the task
            rq_queue.enqueue('extras.webhooks.send_webhook', **params)

        # Scripts
        elif event_rule.action_type == EventRuleActionChoices.SCRIPT:
            # Resolve the script from action parameters
            script = event_rule.action_object.python_class()

            # Enqueue a Job to record the script's execution
            from extras.jobs import ScriptJob

            params = {
                'instance': event_rule.action_object,
                'name': script.name,
                'user': event['user'],
                'data': event_data,
            }
            if 'snapshots' in event:
                params['snapshots'] = event['snapshots']
            if 'request' in event:
                params['request'] = copy_safe_request(event['request'])

            # Enqueue the job
            ScriptJob.enqueue(**params)

        # Notification groups
        elif event_rule.action_type == EventRuleActionChoices.NOTIFICATION:
            # Bulk-create notifications for all members of the notification group
            event_rule.action_object.notify(
                object_type=object_type,
                object_id=event_data['id'],
                object_repr=event_data.get('display'),
                event_type=event['event_type'],
            )

        else:
            raise ValueError(_("Unknown action type for an event rule: {action_type}").format(
                action_type=event_rule.action_type
            ))


def process_event_queue(events):
    """
    Flush a list of object representation to RQ for EventRule processing.

    This is the default processor listed in EVENTS_PIPELINE.
    """
    events_cache = defaultdict(dict)

    for event in events:
        event_type = event['event_type']
        object_type = event['object_type']

        # Cache applicable Event Rules
        if object_type not in events_cache[event_type]:
            events_cache[event_type][object_type] = EventRule.objects.filter(
                event_types__contains=[event['event_type']],
                object_types=object_type,
                enabled=True
            )
        event_rules = events_cache[event_type][object_type]

        process_event_rules(
            event_rules=event_rules,
            object_type=object_type,
            event=event,
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
            except ImportError as e:
                logger.error(_("Cannot import events pipeline {name} error: {error}").format(name=name, error=e))
