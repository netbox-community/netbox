import logging

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models.fields.reverse_related import ManyToManyRel
from django.db.models.signals import m2m_changed, post_save, pre_delete
from django.dispatch import receiver, Signal
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import model_deletes, model_inserts, model_updates

from core.signals import job_end, job_start
from extras.constants import EVENT_JOB_END, EVENT_JOB_START
from extras.events import process_event_rules
from extras.models import EventRule
from extras.validators import run_validators
from netbox.config import get_config
from netbox.context import current_request, events_queue
from netbox.models.features import ChangeLoggingMixin
from netbox.signals import post_clean
from utilities.exceptions import AbortRequest
from .choices import ObjectChangeActionChoices
from .events import enqueue_object, get_snapshots, serialize_for_event
from .models import CustomField, ObjectChange, TaggedItem

#
# Change logging/webhooks
#

# Define a custom signal that can be sent to clear any queued events
clear_events = Signal()


def is_same_object(instance, webhook_data, request_id):
    """
    Compare the given instance to the most recent queued webhook object, returning True
    if they match. This check is used to avoid creating duplicate webhook entries.
    """
    return (
        ContentType.objects.get_for_model(instance) == webhook_data['content_type'] and
        instance.pk == webhook_data['object_id'] and
        request_id == webhook_data['request_id']
    )


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
        action = ObjectChangeActionChoices.ACTION_CREATE
    elif 'created' in kwargs:
        action = ObjectChangeActionChoices.ACTION_UPDATE
    elif kwargs.get('action') in ['post_add', 'post_remove'] and kwargs['pk_set']:
        # m2m_changed with objects added or removed
        m2m_changed = True
        action = ObjectChangeActionChoices.ACTION_UPDATE
    else:
        return

    # Create/update an ObjectChange record for this change
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

    # If this is an M2M change, update the previously queued webhook (from post_save)
    queue = events_queue.get()
    if m2m_changed and queue and is_same_object(instance, queue[-1], request.id):
        instance.refresh_from_db()  # Ensure that we're working with fresh M2M assignments
        queue[-1]['data'] = serialize_for_event(instance)
        queue[-1]['snapshots']['postchange'] = get_snapshots(instance, action)['postchange']
    else:
        enqueue_object(queue, instance, request.user, request.id, action)
    events_queue.set(queue)

    # Increment metric counters
    if action == ObjectChangeActionChoices.ACTION_CREATE:
        model_inserts.labels(instance._meta.model_name).inc()
    elif action == ObjectChangeActionChoices.ACTION_UPDATE:
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

    # Enqueue webhooks
    queue = events_queue.get()
    enqueue_object(queue, instance, request.user, request.id, ObjectChangeActionChoices.ACTION_DELETE)
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
    events_queue.set([])


#
# Custom fields
#

def handle_cf_added_obj_types(instance, action, pk_set, **kwargs):
    """
    Handle the population of default/null values when a CustomField is added to one or more ContentTypes.
    """
    if action == 'post_add':
        instance.populate_initial_data(ContentType.objects.filter(pk__in=pk_set))


def handle_cf_removed_obj_types(instance, action, pk_set, **kwargs):
    """
    Handle the cleanup of old custom field data when a CustomField is removed from one or more ContentTypes.
    """
    if action == 'post_remove':
        instance.remove_stale_data(ContentType.objects.filter(pk__in=pk_set))


def handle_cf_renamed(instance, created, **kwargs):
    """
    Handle the renaming of custom field data on objects when a CustomField is renamed.
    """
    if not created and instance.name != instance._name:
        instance.rename_object_data(old_name=instance._name, new_name=instance.name)


def handle_cf_deleted(instance, **kwargs):
    """
    Handle the cleanup of old custom field data when a CustomField is deleted.
    """
    instance.remove_stale_data(instance.object_types.all())


post_save.connect(handle_cf_renamed, sender=CustomField)
pre_delete.connect(handle_cf_deleted, sender=CustomField)
m2m_changed.connect(handle_cf_added_obj_types, sender=CustomField.object_types.through)
m2m_changed.connect(handle_cf_removed_obj_types, sender=CustomField.object_types.through)


#
# Custom validation
#

@receiver(post_clean)
def run_save_validators(sender, instance, **kwargs):
    """
    Run any custom validation rules for the model prior to calling save().
    """
    model_name = f'{sender._meta.app_label}.{sender._meta.model_name}'
    validators = get_config().CUSTOM_VALIDATORS.get(model_name, [])

    run_validators(instance, validators)


#
# Tags
#

@receiver(m2m_changed, sender=TaggedItem)
def validate_assigned_tags(sender, instance, action, model, pk_set, **kwargs):
    """
    Validate that any Tags being assigned to the instance are not restricted to non-applicable object types.
    """
    if action != 'pre_add':
        return
    ct = ContentType.objects.get_for_model(instance)
    # Retrieve any applied Tags that are restricted to certain object_types
    for tag in model.objects.filter(pk__in=pk_set, object_types__isnull=False).prefetch_related('object_types'):
        if ct not in tag.object_types.all():
            raise AbortRequest(f"Tag {tag} cannot be assigned to {ct.model} objects.")


#
# Event rules
#

@receiver(job_start)
def process_job_start_event_rules(sender, **kwargs):
    """
    Process event rules for jobs starting.
    """
    event_rules = EventRule.objects.filter(type_job_start=True, enabled=True, content_types=sender.object_type)
    username = sender.user.username if sender.user else None
    process_event_rules(event_rules, sender.object_type.model, EVENT_JOB_START, sender.data, username)


@receiver(job_end)
def process_job_end_event_rules(sender, **kwargs):
    """
    Process event rules for jobs terminating.
    """
    event_rules = EventRule.objects.filter(type_job_end=True, enabled=True, content_types=sender.object_type)
    username = sender.user.username if sender.user else None
    process_event_rules(event_rules, sender.object_type.model, EVENT_JOB_END, sender.data, username)
