from collections import defaultdict
from importlib import import_module

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import post_delete, post_save

from extras.models import CachedValue
from extras.registry import registry
from netbox.constants import SEARCH_MAX_RESULTS
from . import SearchResult

# The cache for the initialized backend.
_backends_cache = {}


def get_indexer(model):
    app_label = model._meta.app_label
    model_name = model._meta.model_name

    return registry['search'][app_label][model_name]


class SearchEngineError(Exception):
    """Something went wrong with a search engine."""
    pass


class SearchBackend:
    """A search engine capable of performing multi-table searches."""
    _search_choice_options = tuple()

    def __init__(self):

        # Connect handlers to the appropriate model signals
        post_save.connect(self.caching_handler)
        post_delete.connect(self.removal_handler)

    def get_registry(self):
        r = {}
        for app_label, models in registry['search'].items():
            r.update(**models)

        return r

    def get_search_choices(self):
        """Return the set of choices for individual object types, organized by category."""
        if not self._search_choice_options:

            # Organize choices by category
            categories = defaultdict(dict)
            for app_label, models in registry['search'].items():
                for name, cls in models.items():
                    title = cls.model._meta.verbose_name.title()
                    categories[cls.get_category()][name] = title

            # Compile a nested tuple of choices for form rendering
            results = (
                ('', 'All Objects'),
                *[(category, choices.items()) for category, choices in categories.items()]
            )

            self._search_choice_options = results

        return self._search_choice_options

    def search(self, request, value, **kwargs):
        """
        Search cached object representations for the given value.
        """
        raise NotImplementedError

    @classmethod
    def caching_handler(cls, sender, instance, **kwargs):
        """
        Receiver for the post_save signal, responsible for caching object creation/changes.
        """
        try:
            indexer = get_indexer(instance)
        except KeyError:
            # No indexer has been registered for this model
            return
        data = indexer.to_cache(instance)
        cls.cache(instance, data)

    @classmethod
    def removal_handler(cls, sender, instance, **kwargs):
        """
        Receiver for the post_delete signal, responsible for caching object deletion.
        """
        cls.remove(instance)

    @classmethod
    def cache(cls, instance, data):
        """
        Create or update the cached representation of an instance.
        """
        raise NotImplementedError

    @classmethod
    def remove(cls, instance):
        """
        Delete any cached representation of an instance.
        """
        raise NotImplementedError


class FilterSetSearchBackend(SearchBackend):
    """
    Legacy search backend. Performs a discrete database query for each registered object type, using the FilterSet
    class specified by the index for each.
    """
    def search(self, request, value, **kwargs):
        results = []

        search_registry = self.get_registry()
        for obj_type in search_registry.keys():

            queryset = getattr(search_registry[obj_type], 'queryset', None)
            if not queryset:
                continue

            # Restrict the queryset for the current user
            if hasattr(queryset, 'restrict'):
                queryset = queryset.restrict(request.user, 'view')

            filterset = getattr(search_registry[obj_type], 'filterset', None)
            if not filterset:
                # This backend requires a FilterSet class for the model
                continue

            queryset = filterset({'q': value}, queryset=queryset).qs[:SEARCH_MAX_RESULTS]

            results.extend([
                SearchResult(obj) for obj in queryset
            ])

        return results

    @classmethod
    def cache(cls, instance, data):
        # This backend does not utilize a cache
        pass

    @classmethod
    def remove(cls, instance):
        # This backend does not utilize a cache
        pass


class CachedValueSearchBackend(SearchBackend):

    def search(self, request, value, **kwargs):
        return CachedValue.objects.filter(value__icontains=value).prefetch_related('object')

    @classmethod
    def cache(cls, instance, data):
        for field in data:
            if not field.value:
                continue
            ct = ContentType.objects.get_for_model(instance)
            CachedValue.objects.update_or_create(
                defaults={
                    'value': field.value,
                    'weight': field.weight,
                },
                object_type=ct,
                object_id=instance.pk,
                field=field.name,
                type=field.type
            )

    @classmethod
    def remove(cls, instance):
        ct = ContentType.objects.get_for_model(instance)
        CachedValue.objects.filter(object_type=ct, object_id=instance.pk).delete()


def get_backend():
    """Initializes and returns the configured search backend."""
    backend_name = settings.SEARCH_BACKEND

    # Load the backend class
    backend_module_name, backend_cls_name = backend_name.rsplit('.', 1)
    backend_module = import_module(backend_module_name)
    try:
        backend_cls = getattr(backend_module, backend_cls_name)
    except AttributeError:
        raise ImproperlyConfigured(f"Could not find a class named {backend_module_name} in {backend_cls_name}")

    # Initialize and return the backend instance
    return backend_cls()


search_backend = get_backend()
