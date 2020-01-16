from taggit.managers import _TaggableManager
from utilities.querysets import DummyQuerySet


def is_taggable(obj):
    """
    Return True if the instance can have Tags assigned to it; False otherwise.
    """
    if hasattr(obj, 'tags'):
        if issubclass(obj.tags.__class__, _TaggableManager):
            return True
        # TaggableManager has been replaced with a DummyQuerySet prior to object deletion
        if isinstance(obj.tags, DummyQuerySet):
            return True
    return False
