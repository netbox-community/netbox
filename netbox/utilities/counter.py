from django.apps import apps
from django.db.models import F
from django.db.models.signals import post_delete, post_save
from functools import partial

from netbox.registry import registry
from .fields import CounterCacheField


def post_save_receiver_counter(counter_instance, sender, instance, created, **kwargs):
    if created:
        counter_instance.adjust_count(counter_instance.parent_id(instance), 1)
        return

    # not created so check if field has changed
    field_name = f"{counter_instance.foreign_key_field.name}_id"
    if field_name in instance.tracker.changed:
        new_value = getattr(instance, field_name, None)
        old_value = instance.tracker.changed[field_name]
        if (new_value is not None) and (new_value != old_value):
            counter_instance.adjust_count(new_value, 1)
            counter_instance.adjust_count(old_value, -1)


def post_delete_receiver_counter(counter_instance, sender, instance, **kwargs):
    counter_instance.adjust_count(counter_instance.parent_id(instance), -1)


class Counter:
    """
    Used with CounterCacheField to add signals to track related model counts.
    """
    counter_name = None
    foreign_key_field = None
    child_model = None
    parent_model = None

    def __init__(self, counter_name, foreign_key_field):
        self.counter_name = counter_name
        self.foreign_key_field = foreign_key_field.field
        self.child_model = self.foreign_key_field.model
        self.parent_model = self.foreign_key_field.related_model

        # add the field to be tracked for changes in case of update
        change_tracking_fields = registry['counter_fields'][self.child_model]
        change_tracking_fields.add(f"{self.foreign_key_field.name}_id")

        self.connect()

    def connect(self):
        """
        Hook up post_save, post_delete signal handlers to the fk field to change the count
        """
        name = f"{self.parent_model._meta.model_name}.{self.child_model._meta.model_name}.{self.foreign_key_field.name}"
        counted_name = f"{name}-{self.counter_name}"

        post_save_receiver = partial(post_save_receiver_counter, counter_instance=self)
        post_save.connect(
            post_save_receiver, sender=self.child_model, weak=False, dispatch_uid=f'{counted_name}_post_save'
        )

        post_delete_receiver = partial(post_delete_receiver_counter, counter_instance=self)
        post_delete.connect(
            post_delete_receiver,
            sender=self.child_model,
            weak=False,
            dispatch_uid=f'{counted_name}_post_delete',
        )

    def parent_id(self, child):
        return getattr(child, self.foreign_key_field.attname)

    def set_counter_field(self, parent_id, value):
        return self.parent_model.objects.filter(pk=parent_id).update(**{self.counter_name: value})

    def adjust_count(self, parent_id, amount):
        return self.set_counter_field(parent_id, F(self.counter_name) + amount)


def connect_counters(models):
    for model in models:
        fields = model._meta.get_fields()
        for field in fields:
            if type(field) is CounterCacheField:
                to_model = apps.get_model(field.to_model_name)
                to_field = getattr(to_model, field.to_field_name)
                Counter(field.name, to_field)
