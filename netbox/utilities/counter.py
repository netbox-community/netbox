from django.db.models import F
from django.db.models.signals import post_delete, post_save, pre_save

from .fields import CounterCacheField

counters = {}


class Counter(object):
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

        self.connect()

    def validate(self):
        counter_field, _, _, _ = self.parent_model._meta.get_field_by_name(self.counter_name)
        if not isinstance(counter_field, CounterCacheField):
            raise TypeError(
                f"{self.counter_name} should be a CounterCacheField on {self.parent_model}, but is {type(counter_field)}"
            )

    def connect(self):
        """
        Hook up post_save, post_delete signal handlers to the fk field to change the count
        """
        name = f"{self.parent_model._meta.model_name}.{self.child_model._meta.model_name}.{self.foreign_key_field.name}"
        counted_name = f"{name}-{self.counter_name}"

        def post_save_receiver_counter(sender, instance, **kwargs):
            self.increment(instance, 1)

        post_save.connect(
            post_save_receiver_counter, sender=self.child_model, weak=False, dispatch_uid=f'{counted_name}_post_save'
        )

        def post_delete_receiver_counter(sender, instance, **kwargs):
            self.increment(instance, -1)

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

    def increment(self, child, amount):
        parent_id = self.parent_id(child)
        return self.set_counter_field(parent_id, F(self.counter_name) + amount)


def connect_counter(counter_name, foreign_key_field):
    return Counter(counter_name, foreign_key_field)
