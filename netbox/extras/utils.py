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
    The registry is a place to hook into for data storage across components
    """

    def add_store(self, store_name, initial_value=None):
        """
        Given the name of some new data parameter and an optional initial value, setup the registry store
        """
        if not hasattr(Registry, store_name):
            setattr(Registry, store_name, initial_value)

registry = Registry()


#
# Dynamic feature registration
#

class FeatureQuerySet:
    """
    Helper class that delays evaluation of the registry contents for the functionaility store
    until it has been populated.
    """

    def __init__(self, feature):
        self.feature = feature

    def __call__(self):
        return self.get_queryset()

    def get_queryset(self):
        """
        Given an extras feature, return a Q object for content type lookup
        """
        query = Q()
        #registry = Registry()
        for app_label, models in registry.model_feature_store[self.feature].items():
            query |= Q(app_label=app_label, model__in=models)

        return query


registry.add_store('model_feature_store', {f: collections.defaultdict(list) for f in EXTRAS_FUNCTIONALITIES})


def extras_features(features):
    """
    Decorator used to register extras provided features to a model
    """
    def wrapper(model_class):
        if isinstance(features, list) and features:
            #registry = Registry()
            model_class._extras_feature = []
            for feature in features:
                if feature in EXTRAS_FUNCTIONALITIES:
                    app_label, model_name = model_class._meta.label_lower.split('.')
                    registry.model_feature_store[feature][app_label].append(model_name)
        return model_class
    return wrapper
