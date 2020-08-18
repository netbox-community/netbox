import collections

from django.db.models import Q
from django.utils.deconstruct import deconstructible
from taggit.managers import _TaggableManager

from extras.constants import EXTRAS_FEATURES
from extras.registry import registry


def is_taggable(obj):
    """
    Return True if the instance can have Tags assigned to it; False otherwise.
    """
    if hasattr(obj, 'tags'):
        if issubclass(obj.tags.__class__, _TaggableManager):
            return True
    return False


def image_upload(instance, filename):
    """
    Return a path for uploading image attchments.
    """
    path = 'image-attachments/'

    # Rename the file to the provided name, if any. Attempt to preserve the file extension.
    extension = filename.rsplit('.')[-1].lower()
    if instance.name and extension in ['bmp', 'gif', 'jpeg', 'jpg', 'png']:
        filename = '.'.join([instance.name, extension])
    elif instance.name:
        filename = instance.name

    return '{}{}_{}_{}'.format(path, instance.content_type.name, instance.object_id, filename)


@deconstructible
class FeatureQuery:
    """
    Helper class that delays evaluation of the registry contents for the functionality store
    until it has been populated.
    """
    def __init__(self, feature):
        self.feature = feature

    def __call__(self):
        return self.get_query()

    def get_query(self):
        """
        Given an extras feature, return a Q object for content type lookup
        """
        query = Q()
        for app_label, models in registry['model_features'][self.feature].items():
            query |= Q(app_label=app_label, model__in=models)

        return query


def extras_features(*features):
    """
    Decorator used to register extras provided features to a model
    """
    def wrapper(model_class):
        # Initialize the model_features store if not already defined
        if 'model_features' not in registry:
            registry['model_features'] = {
                f: collections.defaultdict(list) for f in EXTRAS_FEATURES
            }
        for feature in features:
            if feature in EXTRAS_FEATURES:
                app_label, model_name = model_class._meta.label_lower.split('.')
                registry['model_features'][feature][app_label].append(model_name)
            else:
                raise ValueError('{} is not a valid extras feature!'.format(feature))
        return model_class
    return wrapper
