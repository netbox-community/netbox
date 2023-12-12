from django.apps import apps
from django.db.models import F, Count, OuterRef, Subquery
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


def pre_delete_receiver(sender, instance, origin, **kwargs):
    model = instance._meta.model
    if not model.objects.filter(pk=instance.pk).exists():
        instance._previously_removed = True


def post_delete_receiver(sender, instance, origin, **kwargs):
    """
    Update counter fields on related objects when a TrackingModelMixin subclass is deleted.
    """
    for field_name, counter_name in get_counters_for_model(sender):
        parent_model = sender._meta.get_field(field_name).related_model
        parent_pk = getattr(instance, field_name, None)

        # Decrement the parent's counter by one
        if parent_pk is not None and not hasattr(instance, "_previously_removed"):
            update_counter(parent_model, parent_pk, counter_name, -1)


#
# Registration
#

def connect_counters(*models):
    """
    Register counter fields and connect post_save & post_delete signal handlers for the affected models.
    """
    for model in models:

        # Find all CounterCacheFields on the model
        counter_fields = [
            field for field in model._meta.get_fields() if type(field) is CounterCacheField
        ]

        for field in counter_fields:
            to_model = apps.get_model(field.to_model_name)

            # Register the counter in the registry
            change_tracking_fields = registry['counter_fields'][to_model]
            change_tracking_fields[f"{field.to_field_name}_id"] = field.name

            # Connect the post_save and post_delete handlers
            post_save.connect(
                post_save_receiver,
                sender=to_model,
                weak=False,
                dispatch_uid=f'{model._meta.label}.{field.name}'
            )
            pre_delete.connect(
                pre_delete_receiver,
                sender=to_model,
                weak=False,
                dispatch_uid=f'{model._meta.label}.{field.name}'
            )
            post_delete.connect(
                post_delete_receiver,
                sender=to_model,
                weak=False,
                dispatch_uid=f'{model._meta.label}.{field.name}'
            )
