from django.apps import apps
from django.db.models import Count, F, OuterRef, QuerySet, Subquery
from django.db.models.signals import post_delete, post_save, pre_delete

from netbox.registry import registry

from .fields import CounterCacheField


def get_counters_for_model(model):
    """
    Return field mappings for all counters registered to the given model.
    """
    return registry['counter_fields'][model].items()


def update_counter(model, pk, counter_name, value):
    """
    Increment or decrement a counter field on an object identified by its model and primary key (PK). Positive values
    will increment; negative values will decrement.
    """
    model.objects.filter(pk=pk).update(
        **{counter_name: F(counter_name) + value}
    )


def update_counts(model, field_name, related_query):
    """
    Perform a bulk update for the given model and counter field. For example,

        update_counts(Device, '_interface_count', 'interfaces')

    will effectively set

        Device.objects.update(_interface_count=Count('interfaces'))
    """
    subquery = Subquery(
        model.objects.filter(pk=OuterRef('pk')).annotate(_count=Count(related_query)).values('_count')
    )
    return model.objects.update(**{
        field_name: subquery
    })


#
# Signal handlers
#

def post_save_receiver(sender, instance, created, **kwargs):
    """
    Update counter fields on related objects when a TrackingModelMixin subclass is created or modified.
    """
    for field_name, counter_name in get_counters_for_model(sender):
        parent_model = sender._meta.get_field(field_name).related_model
        new_pk = getattr(instance, field_name, None)
        has_old_field = field_name in instance.tracker
        old_pk = instance.tracker.get(field_name) if has_old_field else None

        # Update the counters on the old and/or new parents as needed
        if old_pk is not None:
            update_counter(parent_model, old_pk, counter_name, -1)
        if new_pk is not None and (has_old_field or created):
            update_counter(parent_model, new_pk, counter_name, 1)


def _parent_is_being_deleted(origin, parent_model, parent_pk):
    """
    Return True if `origin` (the object or queryset that `delete()` was called on) indicates that
    the parent identified by (parent_model, parent_pk) is itself being deleted as part of the same
    operation. In that case, decrementing its counter is wasted work: the parent row is going away,
    so the UPDATE would be a no-op. Skipping it avoids an N+1 storm of pointless UPDATEs when a
    parent with many tracked children is deleted (e.g. a Device with thousands of Interfaces).
    """
    if origin is None:
        return False
    if isinstance(origin, QuerySet):
        # A bulk delete; every collected child belongs to an object in this queryset by construction
        return origin.model is parent_model
    # A single object delete
    return isinstance(origin, parent_model) and origin.pk == parent_pk


def pre_delete_receiver(sender, instance, origin, **kwargs):
    """
    Before a tracked object is deleted, check whether its row has already been removed (e.g. by an
    earlier cascade) and, if so, flag it so post_delete_receiver skips the now-redundant counter
    update. The existence check is skipped when the tracked parent is itself being deleted, since
    the counter update would be skipped regardless — this avoids a SELECT per cascaded child.
    """
    for field_name, counter_name in get_counters_for_model(sender):
        parent_model = sender._meta.get_field(field_name).related_model
        parent_pk = getattr(instance, field_name, None)
        if parent_pk is None or _parent_is_being_deleted(origin, parent_model, parent_pk):
            continue
        # A tracked parent will survive this operation, so the double-delete guard is needed
        if not sender.objects.filter(pk=instance.pk).exists():
            instance._previously_removed = True
        return


def post_delete_receiver(sender, instance, origin, **kwargs):
    """
    Update counter fields on related objects when a TrackingModelMixin subclass is deleted.
    """
    if hasattr(instance, '_previously_removed'):
        return

    for field_name, counter_name in get_counters_for_model(sender):
        parent_model = sender._meta.get_field(field_name).related_model
        parent_pk = getattr(instance, field_name, None)

        # Decrement the parent's counter by one, unless the parent is itself being deleted
        if parent_pk is not None and not _parent_is_being_deleted(origin, parent_model, parent_pk):
            update_counter(parent_model, parent_pk, counter_name, -1)


#
# Registration
#

def connect_counters(*models):
    """
    Register counter fields and connect signal handlers for their child models.
    Ensures exactly one receiver per child (sender), even when multiple counters
    reference the same sender (e.g., Device).
    """
    connected = set()  # child models we've already connected

    for model in models:
        # Find all CounterCacheFields on the model
        counter_fields = [field for field in model._meta.get_fields() if isinstance(field, CounterCacheField)]

        for field in counter_fields:
            to_model = apps.get_model(field.to_model_name)

            # Register the counter in the registry
            change_tracking_fields = registry['counter_fields'][to_model]
            change_tracking_fields[f'{field.to_field_name}_id'] = field.name

            # Connect signals once per child model
            if to_model in connected:
                continue

            # Ensure dispatch_uid is unique per model (sender), not per field
            uid_base = f'countercache.{to_model._meta.label_lower}'

            # Connect the post_save and post_delete handlers
            post_save.connect(
                post_save_receiver,
                sender=to_model,
                weak=False,
                dispatch_uid=f'{uid_base}.post_save',
            )
            pre_delete.connect(
                pre_delete_receiver,
                sender=to_model,
                weak=False,
                dispatch_uid=f'{uid_base}.pre_delete',
            )
            post_delete.connect(
                post_delete_receiver,
                sender=to_model,
                weak=False,
                dispatch_uid=f'{uid_base}.post_delete',
            )

            connected.add(to_model)
