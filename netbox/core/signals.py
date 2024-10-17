import logging

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models.fields.reverse_related import ManyToManyRel
from django.db.models.signals import m2m_changed, post_save, pre_delete
from django.dispatch import receiver, Signal
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import model_deletes, model_inserts, model_updates

from core.choices import ObjectChangeActionChoices
from core.events import *
from core.models import ObjectChange
from extras.events import enqueue_event
from extras.utils import run_validators
from netbox.config import get_config
from netbox.context import current_request, events_queue
from netbox.models.features import ChangeLoggingMixin
from utilities.exceptions import AbortRequest
from .models import ConfigRevision

__all__ = (
    'clear_events',
    'job_end',
    'job_start',
    'post_sync',
    'pre_sync',
)

# Job signals
job_start = Signal()
job_end = Signal()

# DataSource signals
pre_sync = Signal()
post_sync = Signal()

# Event signals
clear_events = Signal()


#
# Change logging & event handling
#

@receiver((post_save, m2m_changed))
def handle_changed_object(sender, instance, **kwargs):
    """
    Fires when an object is created or updated.
    """
    m2m_changed = False

    if not hasattr(instance, 'to_objectchange'):
        return

    # Get the current request, or bail if not set
    request = current_request.get()
    if request is None:
        return

    # Determine the type of change being made
    if kwargs.get('created'):
        event_type = OBJECT_CREATED
    elif 'created' in kwargs:
        event_type = OBJECT_UPDATED
    elif kwargs.get('action') in ['post_add', 'post_remove'] and kwargs['pk_set']:
        # m2m_changed with objects added or removed
        m2m_changed = True
        event_type = OBJECT_UPDATED
    else:
        return

    # Create/update an ObjectChange record for this change
    action = {
        OBJECT_CREATED: ObjectChangeActionChoices.ACTION_CREATE,
        OBJECT_UPDATED: ObjectChangeActionChoices.ACTION_UPDATE,
        OBJECT_DELETED: ObjectChangeActionChoices.ACTION_DELETE,
    }[event_type]
    objectchange = instance.to_objectchange(action)
    # If this is a many-to-many field change, check for a previous ObjectChange instance recorded
    # for this object by this request and update it
    if m2m_changed and (
        prev_change := ObjectChange.objects.filter(
            changed_object_type=ContentType.objects.get_for_model(instance),
            changed_object_id=instance.pk,
            request_id=request.id
        ).first()
    ):
        prev_change.postchange_data = objectchange.postchange_data
        prev_change.save()
    elif objectchange and objectchange.has_changes:
        objectchange.user = request.user
        objectchange.request_id = request.id
        objectchange.save()

    # Ensure that we're working with fresh M2M assignments
    if m2m_changed:
        instance.refresh_from_db()

    # Enqueue the object for event processing
    queue = events_queue.get()
    enqueue_event(queue, instance, request.user, request.id, event_type)
    events_queue.set(queue)

    # Increment metric counters
    if event_type == OBJECT_CREATED:
        model_inserts.labels(instance._meta.model_name).inc()
    elif event_type == OBJECT_UPDATED:
        model_updates.labels(instance._meta.model_name).inc()


@receiver(pre_delete)
def handle_deleted_object(sender, instance, **kwargs):
    """
    Fires when an object is deleted.
    """
    # Run any deletion protection rules for the object. Note that this must occur prior
    # to queueing any events for the object being deleted, in case a validation error is
    # raised, causing the deletion to fail.
    model_name = f'{sender._meta.app_label}.{sender._meta.model_name}'
    validators = get_config().PROTECTION_RULES.get(model_name, [])
    try:
        run_validators(instance, validators)
    except ValidationError as e:
        raise AbortRequest(
            _("Deletion is prevented by a protection rule: {message}").format(message=e)
        )

    # Get the current request, or bail if not set
    request = current_request.get()
    if request is None:
        return

    # Record an ObjectChange if applicable
    if hasattr(instance, 'to_objectchange'):
        if hasattr(instance, 'snapshot') and not getattr(instance, '_prechange_snapshot', None):
            instance.snapshot()
        objectchange = instance.to_objectchange(ObjectChangeActionChoices.ACTION_DELETE)
        objectchange.user = request.user
        objectchange.request_id = request.id
        objectchange.save()

    # Django does not automatically send an m2m_changed signal for the reverse direction of a
    # many-to-many relationship (see https://code.djangoproject.com/ticket/17688), so we need to
    # trigger one manually. We do this by checking for any reverse M2M relationships on the
    # instance being deleted, and explicitly call .remove() on the remote M2M field to delete
    # the association. This triggers an m2m_changed signal with the `post_remove` action type
    # for the forward direction of the relationship, ensuring that the change is recorded.
    for relation in instance._meta.related_objects:
        if type(relation) is not ManyToManyRel:
            continue
        related_model = relation.related_model
        related_field_name = relation.remote_field.name
        if not issubclass(related_model, ChangeLoggingMixin):
            # We only care about triggering the m2m_changed signal for models which support
            # change logging
            continue
        for obj in related_model.objects.filter(**{related_field_name: instance.pk}):
            obj.snapshot()  # Ensure the change record includes the "before" state
            getattr(obj, related_field_name).remove(instance)

    # Enqueue the object for event processing
    queue = events_queue.get()
    enqueue_event(queue, instance, request.user, request.id, OBJECT_DELETED)
    events_queue.set(queue)

    # Increment metric counters
    model_deletes.labels(instance._meta.model_name).inc()


@receiver(clear_events)
def clear_events_queue(sender, **kwargs):
    """
    Delete any queued events (e.g. because of an aborted bulk transaction)
    """
    logger = logging.getLogger('events')
    logger.info(f"Clearing {len(events_queue.get())} queued events ({sender})")
    events_queue.set({})


#
# DataSource handlers
#

@receiver(post_sync)
def auto_sync(instance, **kwargs):
    """
    Automatically synchronize any DataFiles with AutoSyncRecords after synchronizing a DataSource.
    """
    from .models import AutoSyncRecord

    for autosync in AutoSyncRecord.objects.filter(datafile__source=instance).prefetch_related('object'):
        autosync.object.sync(save=True)


@receiver(post_save, sender=ConfigRevision)
def update_config(sender, instance, **kwargs):
    """
    Update the cached NetBox configuration when a new ConfigRevision is created.
    """
    instance.activate()
