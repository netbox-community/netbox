from django.db.models import F
from django.db.models.signals import post_delete, post_save, pre_save

from .fields import CounterCacheField
from .mixins import TrackingModelMixin

counters = {}


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

        # add the field to be tracked for changes incase of update
        field_name = f"{self.foreign_key_field.name}_id"
        if hasattr(self.child_model, 'change_tracking_fields') and field_name not in self.child_model.change_tracking_fields:
            self.child_model.change_tracking_fields.append(field_name)

        self.connect()

    def validate(self):
        counter_field, _, _, _ = self.parent_model._meta.get_field_by_name(self.counter_name)
        if not isinstance(counter_field, CounterCacheField):
            raise TypeError(
                f"{self.counter_name} should be a CounterCacheField on {self.parent_model}, but is {type(counter_field)}"
            )
        if not isinstance(self.parent_model, TrackingModelMixin):
            raise TypeError(
                f"{self.parent_model} should be derived from TrackingModelMixin"
            )

    def connect(self):
        """
        Hook up post_save, post_delete signal handlers to the fk field to change the count
        """
        name = f"{self.parent_model._meta.model_name}.{self.child_model._meta.model_name}.{self.foreign_key_field.name}"
        counted_name = f"{name}-{self.counter_name}"

        def post_save_receiver_counter(sender, instance, created, **kwargs):
            if created:
                self.adjust_count(self.parent_id(instance), 1)
                return

            # not created so check if field has changed
            field_name = f"{self.foreign_key_field.name}_id"
            if field_name in instance.tracker.changed:
                new_value = getattr(instance, field_name, None)
                old_value = instance.tracker.changed[field_name]
                if (new_value is not None) and (new_value != old_value):
                    self.adjust_count(new_value, 1)
                    self.adjust_count(old_value, -1)

        post_save.connect(
            post_save_receiver_counter, sender=self.child_model, weak=False, dispatch_uid=f'{counted_name}_post_save'
        )

        def post_delete_receiver_counter(sender, instance, **kwargs):
            self.adjust_count(self.parent_id(instance), -1)

        post_delete.connect(
            post_delete_receiver_counter,
            sender=self.child_model,
            weak=False,
            dispatch_uid=f'{counted_name}_post_delete',
        )

        counters[counted_name] = self

    def parent_id(self, child):
        return getattr(child, self.foreign_key_field.attname)

    def set_counter_field(self, parent_id, value):
        return self.parent_model.objects.filter(pk=parent_id).update(**{self.counter_name: value})

    def adjust_count(self, parent_id, amount):
        return self.set_counter_field(parent_id, F(self.counter_name) + amount)


def connect_counter(counter_name, foreign_key_field):
    return Counter(counter_name, foreign_key_field)
