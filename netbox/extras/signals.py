import random
from datetime import timedelta

from cacheops.signals import cache_invalidated, cache_read
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import DEFAULT_DB_ALIAS
from django.db.models.signals import m2m_changed, post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django_prometheus.models import model_deletes, model_inserts, model_updates
from prometheus_client import Counter

from netbox.signals import post_clean
from .choices import ObjectChangeActionChoices
from .models import CustomField, ObjectChange
from .webhooks import enqueue_object, get_snapshots, serialize_for_webhook


#
# Change logging/webhooks
#

def _handle_changed_object(request, webhook_queue, sender, instance, **kwargs):
    """
    Fires when an object is created or updated.
    """
    def is_same_object(instance, webhook_data):
        return (
            ContentType.objects.get_for_model(instance) == webhook_data['content_type'] and
            instance.pk == webhook_data['object_id'] and
            request.id == webhook_data['request_id']
        )

    if not hasattr(instance, 'to_objectchange'):
        return

    m2m_changed = False

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
    if m2m_changed and webhook_queue and is_same_object(instance, webhook_queue[-1]):
        instance.refresh_from_db()  # Ensure that we're working with fresh M2M assignments
        webhook_queue[-1]['data'] = serialize_for_webhook(instance)
        webhook_queue[-1]['snapshots']['postchange'] = get_snapshots(instance, action)['postchange']
    else:
        enqueue_object(webhook_queue, instance, request.user, request.id, action)

    # Increment metric counters
    if action == ObjectChangeActionChoices.ACTION_CREATE:
        model_inserts.labels(instance._meta.model_name).inc()
    elif action == ObjectChangeActionChoices.ACTION_UPDATE:
        model_updates.labels(instance._meta.model_name).inc()

    # Housekeeping: 0.1% chance of clearing out expired ObjectChanges
    if settings.CHANGELOG_RETENTION and random.randint(1, 1000) == 1:
        cutoff = timezone.now() - timedelta(days=settings.CHANGELOG_RETENTION)
        ObjectChange.objects.filter(time__lt=cutoff)._raw_delete(using=DEFAULT_DB_ALIAS)


def _handle_deleted_object(request, webhook_queue, sender, instance, **kwargs):
    """
    Fires when an object is deleted.
    """
    if not hasattr(instance, 'to_objectchange'):
        return

    # Record an ObjectChange if applicable
    if hasattr(instance, 'to_objectchange'):
        objectchange = instance.to_objectchange(ObjectChangeActionChoices.ACTION_DELETE)
        objectchange.user = request.user
        objectchange.request_id = request.id
        objectchange.save()

    # Enqueue webhooks
    enqueue_object(webhook_queue, instance, request.user, request.id, ObjectChangeActionChoices.ACTION_DELETE)

    # Increment metric counters
    model_deletes.labels(instance._meta.model_name).inc()


#
# Custom fields
#

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


m2m_changed.connect(handle_cf_removed_obj_types, sender=CustomField.content_types.through)
post_save.connect(handle_cf_renamed, sender=CustomField)
pre_delete.connect(handle_cf_deleted, sender=CustomField)


#
# Custom validation
#

@receiver(post_clean)
def run_custom_validators(sender, instance, **kwargs):
    model_name = f'{sender._meta.app_label}.{sender._meta.model_name}'
    validators = settings.CUSTOM_VALIDATORS.get(model_name, [])
    for validator in validators:
        validator(instance)


#
# Caching
#

cacheops_cache_hit = Counter('cacheops_cache_hit', 'Number of cache hits')
cacheops_cache_miss = Counter('cacheops_cache_miss', 'Number of cache misses')
cacheops_cache_invalidated = Counter('cacheops_cache_invalidated', 'Number of cache invalidations')


def cache_read_collector(sender, func, hit, **kwargs):
    if hit:
        cacheops_cache_hit.inc()
    else:
        cacheops_cache_miss.inc()


def cache_invalidated_collector(sender, obj_dict, **kwargs):
    cacheops_cache_invalidated.inc()


cache_read.connect(cache_read_collector)
cache_invalidated.connect(cache_invalidated_collector)
