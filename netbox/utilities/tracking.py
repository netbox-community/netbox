from django.db.models.query_utils import DeferredAttribute

from netbox.registry import registry


class Tracker:
    """
    An ephemeral instance employed to record which tracked fields on an instance have been modified.
    """
    def __init__(self):
        self._changed_fields = {}

    def __contains__(self, item):
        return item in self._changed_fields

    def set(self, name, value):
        """
        Mark an attribute as having been changed and record its original value.
        """
        self._changed_fields[name] = value

    def get(self, name):
        """
        Return the original value of a changed field. Raises KeyError if name is not found.
        """
        return self._changed_fields[name]

    def clear(self, *names):
        """
        Clear any fields that were recorded as having been changed.
        """
        for name in names:
            self._changed_fields.pop(name, None)
        else:
            self._changed_fields = {}


class TrackingModelMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Mark the instance as initialized, to enable our custom __setattr__()
        self._initialized = True

    @property
    def tracker(self):
        """
        Return the Tracker instance for this instance, first creating it if necessary.
        """
        if not hasattr(self._state, "_tracker"):
            self._state._tracker = Tracker()
        return self._state._tracker

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Clear any tracked fields now that changes have been saved
        update_fields = kwargs.get('update_fields', [])
        self.tracker.clear(*update_fields)

    def __setattr__(self, name, value):
        if hasattr(self, "_initialized"):
            # Record any changes to a tracked field
            if name in registry['counter_fields'][self.__class__]:
                if name not in self.tracker:
                    # The attribute has been created or changed
                    if name in self.__dict__:
                        old_value = getattr(self, name)
                        if value != old_value:
                            self.tracker.set(name, old_value)
                    else:
                        self.tracker.set(name, DeferredAttribute)
                elif value == self.tracker.get(name):
                    # A previously changed attribute has been restored
                    self.tracker.clear(name)

        super().__setattr__(name, value)
