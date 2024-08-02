from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import m2m_changed, post_save, pre_delete
from django.dispatch import receiver

from core.events import *
from core.models import ObjectType
from core.signals import job_end, job_start
from extras.events import process_event_rules
from extras.models import EventRule, Notification, Subscription
from netbox.config import get_config
from netbox.registry import registry
from netbox.signals import post_clean
from utilities.exceptions import AbortRequest
from .models import CustomField, TaggedItem
from .utils import run_validators


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
    ct = ObjectType.objects.get_for_model(instance)
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
    username = sender.user.username if sender.user else None
    process_event_rules(
        event_rules=event_rules,
        object_type=sender.object_type,
        event_type=JOB_STARTED,
        data=sender.data,
        username=username
    )


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
    username = sender.user.username if sender.user else None
    process_event_rules(
        event_rules=event_rules,
        object_type=sender.object_type,
        event_type=JOB_COMPLETED,
        data=sender.data,
        username=username
    )


#
# Notifications
#

@receiver(post_save)
def notify_object_changed(sender, instance, created, raw, **kwargs):
    if created or raw:
        return

    # Skip unsupported object types
    ct = ContentType.objects.get_for_model(instance)
    if ct.model not in registry['model_features']['notifications'].get(ct.app_label, []):
        return

    # Find all subscribed Users
    subscribed_users = Subscription.objects.filter(object_type=ct, object_id=instance.pk).values_list('user', flat=True)
    if not subscribed_users:
        return

    # Delete any existing Notifications for the object
    Notification.objects.filter(object_type=ct, object_id=instance.pk, user__in=subscribed_users).delete()

    # Create Notifications for Subscribers
    Notification.objects.bulk_create([
        Notification(user_id=user, object=instance, event_type=OBJECT_UPDATED)
        for user in subscribed_users
    ])
