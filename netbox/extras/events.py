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
    Dictionary-compatible wrapper for queued events that lazily serializes
    ``event['data']`` on first access.

    Backward-compatible with the plain-dict interface expected by existing
    EVENTS_PIPELINE consumers. When the same object is enqueued more than once
    in a single request, the serialization source is updated so consumers see
    the latest state.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Track which model instance should be serialized if/when `data` is
        # requested. This may be refreshed on duplicate enqueue, while leaving
        # the public `object` entry untouched for compatibility.
        self._serialization_source = None
        if 'object' in self:
            self._serialization_source = super().__getitem__('object')

    def refresh_serialization_source(self, instance):
        """
        Point lazy serialization at a fresher instance, invalidating any
        already-materialized ``data``.
        """
        self._serialization_source = instance
        # UserDict.__contains__ checks the backing dict directly, so `in`
        # does not trigger __getitem__'s lazy serialization.
        if 'data' in self:
            del self['data']

    def freeze_data(self, instance):
        """
        Eagerly serialize and cache the payload for delete events, where the
        object may become inaccessible after deletion.
        """
        super().__setitem__('data', serialize_for_event(instance))
        self._serialization_source = None

    def __getitem__(self, item):
        if item == 'data' and 'data' not in self:
            # Materialize the payload only when an event consumer asks for it.
            #
            # On coalesced events, use the latest explicitly queued instance so
            # webhooks/scripts/notifications observe the final queued state for
            # that object within the request.
            source = self._serialization_source or super().__getitem__('object')
            super().__setitem__('data', serialize_for_event(source))

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
    Enqueue (or coalesce) an event for a created/updated/deleted object.

    Events are processed after the request completes.
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

        # If the object is being deleted, convert any prior update event into a
        # delete event and freeze the payload before the object (or related
        # rows) become inaccessible.
        if event_type == OBJECT_DELETED:
            queue[key]['event_type'] = event_type
        else:
            # Keep the public `object` entry stable for compatibility.
            queue[key].refresh_serialization_source(instance)
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

    # For delete events, eagerly serialize the payload before the row is gone.
    # This covers both first-time enqueues and coalesced update→delete promotions.
    if event_type == OBJECT_DELETED:
        queue[key].freeze_data(instance)


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

        # Merge rule-specific action_data with the event payload.
        # Copy to avoid mutating the rule's stored action_data dict.
        event_data = {**(event_rule.action_data or {}), **event['data']}

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
