from django.db.models.query_utils import DeferredAttribute

from netbox.registry import registry


class Tracker:
    def __init__(self, instance):
        self.instance = instance
        self.changed = {}


class TrackingModelMixin:

    @property
    def tracker(self):
        if not hasattr(self._state, "_tracker"):
            self._state._tracker = Tracker(self)
        return self._state._tracker

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.tracker.changed:
            if update_fields := kwargs.get('update_fields', None):
                for field in update_fields:
                    self.tracker.changed.pop(field, None)
            else:
                self.tracker.changed = {}

    def __setattr__(self, name, value):
        change_tracking_fields = registry['counter_fields'][self.__class__]
        if name in change_tracking_fields:
            if name not in self.tracker.changed:
                if name in self.__dict__:
                    old_value = getattr(self, name)
                    if value != old_value:
                        self.tracker.changed[name] = old_value
                else:
                    self.tracker.changed[name] = DeferredAttribute
            else:
                if value == self.tracker.changed[name]:
                    self.tracker.changed.pop(name)

        super().__setattr__(name, value)
