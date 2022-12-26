import importlib
import logging

from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import m2m_changed, post_save, pre_delete
from django.dispatch import receiver, Signal
from django_prometheus.models import model_deletes, model_inserts, model_updates

from extras.validators import CustomValidator
from netbox.config import get_config
from netbox.context import current_request, webhooks_queue
from netbox.signals import post_clean
from .choices import ObjectChangeActionChoices
from .models import ConfigRevision, CustomField, ObjectChange
from .webhooks import enqueue_object, get_snapshots, serialize_for_webhook

#
# Change logging/webhooks
#

# Define a custom signal that can be sent to clear any queued webhooks
clear_webhooks = Signal()


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

    # Record an ObjectChange if applicable
    if hasattr(instance, 'to_objectchange'):
        if m2m_changed:
            ObjectChange.objects.filter(
                changed_object_type=ContentType.objects.get_for_model(instance),
                changed_object_id=instance.pk,
                request_id=request.id
            ).update(
                postchange_data=instance.to_objectchange(action).postchange_data
            )
        else:
            objectchange = instance.to_objectchange(action)
            objectchange.user = request.user
            objectchange.request_id = request.id
            objectchange.save()

    # If this is an M2M change, update the previously queued webhook (from post_save)
    queue = webhooks_queue.get()
    if m2m_changed and queue and is_same_object(instance, queue[-1], request.id):
        instance.refresh_from_db()  # Ensure that we're working with fresh M2M assignments
        queue[-1]['data'] = serialize_for_webhook(instance)
        queue[-1]['snapshots']['postchange'] = get_snapshots(instance, action)['postchange']
    else:
        enqueue_object(queue, instance, request.user, request.id, action)
    webhooks_queue.set(queue)

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

    # Enqueue webhooks
    queue = webhooks_queue.get()
    enqueue_object(queue, instance, request.user, request.id, ObjectChangeActionChoices.ACTION_DELETE)
    webhooks_queue.set(queue)

    # Increment metric counters
    model_deletes.labels(instance._meta.model_name).inc()


@receiver(clear_webhooks)
def clear_webhook_queue(sender, **kwargs):
    """
    Delete any queued webhooks (e.g. because of an aborted bulk transaction)
    """
    logger = logging.getLogger('webhooks')
    logger.info(f"Clearing {len(webhooks_queue.get())} queued webhooks ({sender})")
    webhooks_queue.set([])


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
    instance.remove_stale_data(instance.content_types.all())


post_save.connect(handle_cf_renamed, sender=CustomField)
pre_delete.connect(handle_cf_deleted, sender=CustomField)
m2m_changed.connect(handle_cf_added_obj_types, sender=CustomField.content_types.through)
m2m_changed.connect(handle_cf_removed_obj_types, sender=CustomField.content_types.through)


#
# Custom validation
#

@receiver(post_clean)
def run_custom_validators(sender, instance, **kwargs):
    config = get_config()
    model_name = f'{sender._meta.app_label}.{sender._meta.model_name}'
    validators = config.CUSTOM_VALIDATORS.get(model_name, [])

    for validator in validators:

        # Loading a validator class by dotted path
        if type(validator) is str:
            module, cls = validator.rsplit('.', 1)
            validator = getattr(importlib.import_module(module), cls)()

        # Constructing a new instance on the fly from a ruleset
        elif type(validator) is dict:
            validator = CustomValidator(validator)

        validator(instance)


#
# Dynamic configuration
#

@receiver(post_save, sender=ConfigRevision)
def update_config(sender, instance, **kwargs):
    """
    Update the cached NetBox configuration when a new ConfigRevision is created.
    """
    instance.activate()
