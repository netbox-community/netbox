import logging
from collections import UserDict, defaultdict

from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _

from core.events import *
from core.models import ObjectType
from netbox.models.features import has_feature
from utilities.api import get_serializer_for_model
from utilities.serialization import serialize_object

from .conditions import AbsentData
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

    if instance.pk is None:
        raise ValueError(
            _("Cannot enqueue an event for an unsaved {app_label}.{model} instance.").format(
                app_label=app_label,
                model=model_name,
            )
        )
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
        )

    # For delete events, eagerly serialize the payload before the row is gone.
    # This covers both first-time enqueues and coalesced update→delete promotions.
    if event_type == OBJECT_DELETED:
        queue[key].freeze_data(instance)


def process_event_rules(event_rules, object_type, event):
    """
    Process a list of EventRules against an event.

    Notes on event sources:
    - Object change events (created/updated/deleted) are enqueued via enqueue_event()
      during an HTTP request. These events include a request object, and their payload is
      always the serialized object.
    - Job lifecycle events (JOB_STARTED/JOB_COMPLETED) are emitted by job_start/job_end
      signal handlers and may not include a request context. Consumers must not assume
      that a request is always present. Their payload is the job's `data` field, which is
      nullable and (for a job which sets it directly) not guaranteed to be a dict.
    """
    if not event_rules:
        return

    # Normalize object_type onto the event context so that an action's enqueue() can always read
    # event_context['object_type']: job-lifecycle events pass it only as this parameter.
    event['object_type'] = object_type

    # Normalize the event payload to a dict or AbsentData once for all rules.
    data = event['data']
    if not isinstance(data, dict):
        if data is not None:
            logger.warning(
                _('Ignoring invalid data payload on {event_type} event (got {data_type})').format(
                    event_type=event['event_type'],
                    data_type=type(data).__name__,
                )
            )
        data = AbsentData()

    for event_rule in event_rules:

        # Merge snapshots and evaluate event rule conditions (if any).
        condition_data = data.copy()
        condition_data['snapshots'] = event.get('snapshots')
        if not event_rule.eval_conditions(condition_data):
            continue

        # Guard against action_data that is valid JSON but not a dict
        # (e.g. a bare string or number). Existing rows with bad data are
        # tolerated at runtime; validation on EventRule.clean() prevents
        # new ones.
        if event_rule.action_data is None:
            action_data = {}
        elif isinstance(event_rule.action_data, dict):
            action_data = event_rule.action_data
        else:
            logger.warning(
                _('Ignoring invalid action_data on event rule "{rule}" (got {data_type})').format(
                    rule=event_rule,
                    data_type=type(event_rule.action_data).__name__,
                )
            )
            action_data = {}

        # Merge rule-specific action_data with the event payload.
        # Copy to avoid mutating the rule's stored action_data dict.
        event_data = {**action_data, **data}

        action = event_rule.action_provider
        if action is None:
            # The plugin providing this action type may not be installed. Log and move on to the
            # next rule rather than raising: one rule's unavailable action must not prevent any
            # other rule in this batch from being processed.
            logger.warning(
                _('Skipping event rule "{rule}": action type "{action_type}" is not registered '
                  '(the providing plugin may not be installed).').format(
                    rule=event_rule, action_type=event_rule.action_type,
                )
            )
            continue

        try:
            action.enqueue(
                event_rule=event_rule,
                event_context=event,
                action_object=event_rule.action_object,
                action_data=event_data,
            )
        except Exception:
            # Isolate third-party bugs; a core action's own bugs should propagate instead.
            if not action.is_plugin_provided:
                raise
            logger.exception(
                _('Error processing event rule "{rule}" (action: {action_type})').format(
                    rule=event_rule, action_type=event_rule.action_type,
                )
            )


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
