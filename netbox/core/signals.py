import logging
from threading import local

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models.fields.reverse_related import ManyToManyRel, ManyToOneRel
from django.db.models.signals import m2m_changed, post_migrate, post_save, pre_delete
from django.dispatch import receiver, Signal
from django.core.signals import request_finished
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import model_deletes, model_inserts, model_updates

from core.choices import JobStatusChoices, ObjectChangeActionChoices
from core.events import *
from core.models import ObjectType
from extras.events import enqueue_event
from extras.models import Tag
from extras.utils import run_validators
from netbox.config import get_config
from netbox.context import current_request, events_queue
from netbox.models.features import ChangeLoggingMixin, get_model_features, model_is_public
from utilities.exceptions import AbortRequest
from .models import ConfigRevision, DataSource, ObjectChange

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
# Object types
#

@receiver(post_migrate)
def update_object_types(sender, **kwargs):
    """
    Create or update the corresponding ObjectType for each model within the migrated app.
    """
    for model in sender.get_models():
        app_label, model_name = model._meta.label_lower.split('.')

        # Determine whether model is public and its supported features
        is_public = model_is_public(model)
        features = get_model_features(model)

        # Create/update the ObjectType for the model
        try:
            ot = ObjectType.objects.get_by_natural_key(app_label=app_label, model=model_name)
            ot.public = is_public
            ot.features = features
            ot.save()
        except ObjectDoesNotExist:
            ObjectType.objects.create(
                app_label=app_label,
                model=model_name,
                public=is_public,
                features=features,
            )


#
# Change logging & event handling
#

# Used to track received signals per object
_signals_received = local()


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
    elif kwargs.get('action') == 'post_clear':
        # Handle clearing of an M2M field
        if kwargs.get('model') == Tag and getattr(instance, '_prechange_snapshot', {}).get('tags'):
            # Handle generation of M2M changes for Tags which have a previous value (ignoring changes where the
            # prechange snapshot is empty)
            m2m_changed = True
            event_type = OBJECT_UPDATED
        else:
            # Other endpoints are unimpacted as they send post_add and post_remove
            # This will impact changes that utilize clear() however so we may want to give consideration for this branch
            return
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
    enqueue_event(queue, instance, request, event_type)
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

    # Check whether we've already processed a pre_delete signal for this object. (This can
    # happen e.g. when both a parent object and its child are deleted simultaneously, due
    # to cascading deletion.)
    if not hasattr(_signals_received, 'pre_delete'):
        _signals_received.pre_delete = set()
    signature = (ContentType.objects.get_for_model(instance), instance.pk)
    if signature in _signals_received.pre_delete:
        return
    _signals_received.pre_delete.add(signature)

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
    # Similarly, for many-to-one relationships, we set the value on the related object to None
    # and save it to trigger a change record on that object.
    for relation in instance._meta.related_objects:
        if type(relation) not in [ManyToManyRel, ManyToOneRel]:
            continue
        related_model = relation.related_model
        related_field_name = relation.remote_field.name
        if not issubclass(related_model, ChangeLoggingMixin):
            # We only care about triggering the m2m_changed signal for models which support
            # change logging
            continue
        for obj in related_model.objects.filter(**{related_field_name: instance.pk}):
            obj.snapshot()  # Ensure the change record includes the "before" state
            if type(relation) is ManyToManyRel:
                getattr(obj, related_field_name).remove(instance)
            elif type(relation) is ManyToOneRel and relation.field.null is True:
                setattr(obj, related_field_name, None)
                # make sure the object hasn't been deleted - in case of
                # deletion chaining of related objects
                try:
                    obj.refresh_from_db()
                except DoesNotExist:
                    continue
                obj.save()

    # Enqueue the object for event processing
    queue = events_queue.get()
    enqueue_event(queue, instance, request, OBJECT_DELETED)
    events_queue.set(queue)

    # Increment metric counters
    model_deletes.labels(instance._meta.model_name).inc()


@receiver(request_finished)
def clear_signal_history(sender, **kwargs):
    """
    Clear out the signals history once the request is finished.
    """
    _signals_received.pre_delete = set()


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

@receiver(post_save, sender=DataSource)
def enqueue_sync_job(instance, created, **kwargs):
    """
    When a DataSource is saved, check its sync_interval and enqueue a sync job if appropriate.
    """
    from .jobs import SyncDataSourceJob

    if instance.enabled and instance.sync_interval:
        SyncDataSourceJob.enqueue_once(instance, interval=instance.sync_interval)
    elif not created:
        # Delete any previously scheduled recurring jobs for this DataSource
        for job in SyncDataSourceJob.get_jobs(instance).defer('data').filter(
            interval__isnull=False,
            status=JobStatusChoices.STATUS_SCHEDULED
        ):
            # Call delete() per instance to ensure the associated background task is deleted as well
            job.delete()


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
