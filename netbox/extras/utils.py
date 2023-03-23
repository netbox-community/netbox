import inspect
import sys
import threading

from django.db.models import Q
from django.utils.deconstruct import deconstructible
from taggit.managers import _TaggableManager

from netbox.registry import registry

lock = threading.Lock()


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
    Return a path for uploading image attachments.
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


def register_features(model, features):
    """
    Register model features in the application registry.
    """
    app_label, model_name = model._meta.label_lower.split('.')
    for feature in features:
        try:
            registry['model_features'][feature][app_label].add(model_name)
        except KeyError:
            raise KeyError(
                f"{feature} is not a valid model feature! Valid keys are: {registry['model_features'].keys()}"
            )


def get_modules(queryset, litmus_func, ordering_attr):
    """
    Returns a list of tuples:

    [
        (module_name, (child, child, ...)),
        (module_name, (child, child, ...)),
        ...
    ]
    """
    results = {}

    modules = [mf.get_module_info() for mf in queryset]
    modules_bases = set([name.split(".")[0] for _, name, _ in modules])

    # Deleting from sys.modules needs to done behind a lock to prevent race conditions where a module is
    # removed from sys.modules while another thread is importing
    with lock:
        for module_name in list(sys.modules.keys()):
            # Everything sharing a base module path with a module in the script folder is removed.
            # We also remove all modules with a base module called "scripts". This allows modifying imported
            # non-script modules without having to reload the RQ worker.
            module_base = module_name.split(".")[0]
            if module_base in ('reports', 'scripts', *modules_bases):
                del sys.modules[module_name]

    for importer, module_name, _ in modules:
        module = importer.find_module(module_name).load_module(module_name)
        child_order = getattr(module, ordering_attr, ())
        ordered_children = [cls() for cls in child_order if litmus_func(cls)]
        unordered_children = [cls() for _, cls in inspect.getmembers(module, litmus_func) if cls not in child_order]

        children = {}

        for cls in [*ordered_children, *unordered_children]:
            # For child objects in submodules use the full import path w/o the root module as the name
            child_name = cls.full_name.split(".", maxsplit=1)[1]
            children[child_name] = cls

        if children:
            results[module_name] = children

    return results
