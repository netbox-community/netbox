from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import m2m_changed, post_save, pre_delete
from django.dispatch import receiver

from core.events import *
from core.signals import job_end, job_start
from extras.events import EventContext, process_event_rules
from extras.models import EventRule, Notification, Subscription
from netbox.config import get_config
from netbox.models.features import has_feature
from netbox.signals import post_clean
from utilities.data import get_config_value_ci
from utilities.exceptions import AbortRequest

from .models import CustomField, TaggedItem
from .utils import run_validators

#
# Custom fields
#


def handle_cf_object_types_changed(instance, action, pk_set, reverse, **kwargs):
    """
    Handle the stored data of a CustomField as it is assigned to or unassigned from object types.

    Only the forward direction is handled: every action below operates on the CustomField, whereas
    the reverse of this relation (ContentType.custom_fields) reports the ContentType as the sender's
    instance. Nothing in NetBox assigns object types that way.
    """
    if reverse or action not in ('pre_clear', 'post_add', 'post_remove'):
        return

    if action == 'pre_clear':
        # clear() unassigns every object type at once. It must be handled before the fact: no
        # pk_set is reported for a clear, so the assignments have to be read while they still
        # exist. (Note that set() diffs via remove()/add() by default, so it does not land here.)
        instance.remove_stale_data(instance.object_types.all())
        return

    object_types = ContentType.objects.filter(pk__in=pk_set)

    if action == 'post_add':
        # Populate the field's default value (if any) on all existing objects
        instance.populate_initial_data(object_types)

    else:
        # Remove the field's stored data from objects to which it no longer applies
        instance.remove_stale_data(object_types)


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
m2m_changed.connect(handle_cf_object_types_changed, sender=CustomField.object_types.through)


#
# Custom validation
#

@receiver(post_clean)
def run_save_validators(sender, instance, **kwargs):
    """
    Run any custom validation rules for the model prior to calling save().
    """
    model_name = f'{sender._meta.app_label}.{sender._meta.model_name}'
    validators = get_config_value_ci(get_config().CUSTOM_VALIDATORS, model_name, default=[])

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
    # Retrieve any applied Tags that are restricted to certain object types
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
    event_rules = EventRule.objects.filter(
        event_types__contains=[JOB_STARTED],
        enabled=True,
        object_types=sender.object_type
    )
    event = EventContext(
        event_type=JOB_STARTED,
        data=sender.data,
        user=sender.user,
    )
    process_event_rules(event_rules, sender.object_type, event)


@receiver(job_end)
def process_job_end_event_rules(sender, **kwargs):
    """
    Process event rules for jobs terminating.
    """
    event_rules = EventRule.objects.filter(
        event_types__contains=[JOB_COMPLETED],
        enabled=True,
        object_types=sender.object_type
    )
    event = EventContext(
        event_type=JOB_COMPLETED,
        data=sender.data,
        user=sender.user,
    )
    process_event_rules(event_rules, sender.object_type, event)


#
# Notifications
#

@receiver((post_save, pre_delete))
def notify_object_changed(sender, instance, **kwargs):
    # Skip for newly-created objects
    if kwargs.get('created'):
        return

    # Determine event type
    if 'created' in kwargs:
        event_type = OBJECT_UPDATED
    else:
        event_type = OBJECT_DELETED

    # Skip unsupported object types
    if not has_feature(instance, 'notifications'):
        return

    ct = ContentType.objects.get_for_model(instance)

    # Find all subscribed Users
    subscribed_users = Subscription.objects.filter(
        object_type=ct,
        object_id=instance.pk
    ).values_list('user', flat=True)
    if not subscribed_users:
        return

    # Delete any existing Notifications for the object
    Notification.objects.filter(
        object_type=ct,
        object_id=instance.pk,
        user__in=subscribed_users
    ).delete()

    # Create Notifications for Subscribers
    Notification.objects.bulk_create([
        Notification(
            user_id=user,
            object=instance,
            object_repr=Notification.get_object_repr(instance),
            event_type=event_type
        )
        for user in subscribed_users
    ])
