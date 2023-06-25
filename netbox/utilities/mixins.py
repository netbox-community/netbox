from django.db.models.query_utils import DeferredAttribute


class Tracker(object):
    def __init__(self, instance):
        self.instance = instance
        self.newly_created = False
        self.changed = {}
        self.tracked_fields = self.instance.change_tracking_fields


class TrackingModelMixin(object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.change_tracking_fields = []
        self._initialized = True

    @property
    def tracker(self):
        if hasattr(self._state, "_tracker"):
            tracker = self._state._tracker
        else:
            tracker = self._state._tracker = Tracker(self)
        return tracker

    def save(self, *args, **kwargs):
        if not self.change_tracking_fields:
            return super().save(*args, **kwargs)

        self.tracker.newly_created = self._state.adding
        super().save(*args, **kwargs)
        if self.tracker.changed:
            if update_fields := kwargs.get('update_fields', None):
                for field in update_fields:
                    self.tracker.changed.pop(field, None)
            else:
                self.tracker.changed = {}

    def __setattr__(self, name, value):
        if hasattr(self, "_initialized") and self.change_tracking_fields:
            if name in self.tracker.tracked_fields:
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
