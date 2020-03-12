import collections

from django.db.models import Q
from taggit.managers import _TaggableManager
from utilities.querysets import DummyQuerySet

from extras.constants import EXTRAS_FUNCTIONALITIES


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


class Registry:
    """
    Singleton object used to store important data
    """
    instance = None

    def __new__(cls):
        if cls.instance is not None:
            return cls.instance
        else:
            cls.instance = super().__new__(cls)
            cls.model_functionality_store = {f: collections.defaultdict(list) for f in EXTRAS_FUNCTIONALITIES}
            return cls.instance


class FunctionalityQueryset:
    """
    Helper class that delays evaluation of the registry contents for the functionaility store
    until it has been populated.
    """

    def __init__(self, functionality):
        self.functionality = functionality

    def __call__(self):
        return self.get_queryset()

    def get_queryset(self):
        """
        Given an extras functionality, return a Q object for content type lookup
        """
        query = Q()
        registry = Registry()
        for app_label, models in registry.model_functionality_store[self.functionality].items():
            query |= Q(app_label=app_label, model__in=models)

        return query


def extras_functionality(functionalities):
    """
    Decorator used to register extras provided functionalities to a model
    """
    def wrapper(model_class):
        if isinstance(functionalities, list) and functionalities:
            registry = Registry()
            model_class._extras_functionality = []
            for functionality in functionalities:
                if functionality in EXTRAS_FUNCTIONALITIES:
                    model_class._extras_functionality.append(functionality)
                    app_label, model_name = model_class._meta.label_lower.split('.')
                    registry.model_functionality_store[functionality][app_label].append(model_name)
        return model_class
    return wrapper
