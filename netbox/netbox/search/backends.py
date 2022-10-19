from collections import defaultdict
from importlib import import_module

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db.models import F, Window
from django.db.models.functions import window
from django.db.models.signals import post_delete, post_save

from extras.models import CachedValue, CustomField
from extras.registry import registry
from utilities.querysets import RestrictedPrefetch
from utilities.templatetags.builtins.filters import bettertitle
from . import FieldTypes, LookupTypes, get_indexer

DEFAULT_LOOKUP_TYPE = LookupTypes.PARTIAL
MAX_RESULTS = 1000


class SearchBackend:
    """A search engine capable of performing multi-table searches."""
    _search_choice_options = tuple()

    def __init__(self):

        # Connect handlers to the appropriate model signals
        post_save.connect(self.caching_handler)
        post_delete.connect(self.removal_handler)

    def get_object_types(self):
        """Return the set of choices for individual object types, organized by category."""
        if not self._search_choice_options:

            # Organize choices by category
            categories = defaultdict(dict)
            for app_label, models in registry['search'].items():
                for name, cls in models.items():
                    title = bettertitle(cls.model._meta.verbose_name)
                    value = f'{app_label}.{name}'
                    categories[cls.get_category()][value] = title

            # Compile a nested tuple of choices for form rendering
            results = (
                ('', 'All Objects'),
                *[(category, list(choices.items())) for category, choices in categories.items()]
            )

            self._search_choice_options = results

        return self._search_choice_options

    def search(self, request, value, object_types=None, lookup=DEFAULT_LOOKUP_TYPE):
        """
        Search cached object representations for the given value.
        """
        raise NotImplementedError

    @classmethod
    def caching_handler(cls, sender, instance, **kwargs):
        """
        Receiver for the post_save signal, responsible for caching object creation/changes.
        """
        cls.cache(instance)

    @classmethod
    def removal_handler(cls, sender, instance, **kwargs):
        """
        Receiver for the post_delete signal, responsible for caching object deletion.
        """
        cls.remove(instance)

    @classmethod
    def cache(cls, instance, indexer=None):
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

    @classmethod
    def clear(cls, instance):
        """
        Delete *all* cached data.
        """
        raise NotImplementedError

    @property
    def size(self):
        """
        Return a total number of cached entries. The meaning of this value will be
        backend-dependent.
        """
        return None


class CachedValueSearchBackend(SearchBackend):

    def search(self, request, value, object_types=None, lookup=None):
        if not lookup:
            lookup = DEFAULT_LOOKUP_TYPE

        # Define the search parameters
        params = {
            f'value__{lookup}': value
        }
        if lookup != LookupTypes.EXACT:
            # Partial matches are valid only on string values
            params['type'] = FieldTypes.STRING
        if object_types:
            params['object_type__in'] = object_types

        # Construct the base queryset to retrieve matching results
        queryset = CachedValue.objects.filter(**params).annotate(
            # Annotate the rank of each result for its object according to its weight
            row_number=Window(
                expression=window.RowNumber(),
                partition_by=[F('object_type'), F('object_id')],
                order_by=[F('weight').asc()],
            )
        )[:MAX_RESULTS]

        # Construct a Prefetch to pre-fetch only those related objects for which the
        # user has permission to view.
        prefetch = RestrictedPrefetch('object', request.user, 'view')

        # Wrap the base query to return only the lowest-weight result for each object
        # Hat-tip to https://blog.oyam.dev/django-filter-by-window-function/ for the solution
        sql, params = queryset.query.sql_with_params()
        results = CachedValue.objects.prefetch_related(prefetch, 'object_type').raw(
            f"SELECT * FROM ({sql}) t WHERE row_number = 1",
            params
        )

        # Omit any results pertaining to an object the user does not have permission to view
        return [
            r for r in results if r.object is not None
        ]

    @classmethod
    def cache(cls, instances, indexer=None, remove_existing=True):
        content_type = None
        custom_fields = None

        # Convert a single instance to an iterable
        if not hasattr(instances, '__iter__'):
            instances = [instances]

        buffer = []
        counter = 0
        for instance in instances:

            # Wipe out any previously cached values for the object
            if remove_existing:
                cls.remove(instance)

            # Determine the indexer
            if indexer is None:
                try:
                    indexer = get_indexer(instance)
                    content_type = ContentType.objects.get_for_model(indexer.model)
                    custom_fields = CustomField.objects.filter(content_types=content_type).exclude(search_weight=0)
                except KeyError:
                    # No indexer has been registered for this model
                    continue

            # Generate cache data
            for field in indexer.to_cache(instance, custom_fields=custom_fields):
                buffer.append(
                    CachedValue(
                        object_type=content_type,
                        object_id=instance.pk,
                        field=field.name,
                        type=field.type,
                        weight=field.weight,
                        value=field.value
                    )
                )

            # Check whether the buffer needs to be flushed
            if len(buffer) >= 2000:
                counter += len(CachedValue.objects.bulk_create(buffer))
                buffer = []

        # Final buffer flush
        if buffer:
            counter += len(CachedValue.objects.bulk_create(buffer))

        return counter

    @classmethod
    def remove(cls, instance):
        # Avoid attempting to query for non-cacheable objects
        try:
            get_indexer(instance)
        except KeyError:
            return

        ct = ContentType.objects.get_for_model(instance)
        CachedValue.objects.filter(object_type=ct, object_id=instance.pk).delete()

    @classmethod
    def clear(cls, object_types=None):
        if object_types:
            del_count, _ = CachedValue.objects.filter(object_type__in=object_types).delete()
        else:
            del_count, _ = CachedValue.objects.all().delete()
        return del_count

    @property
    def size(self):
        return CachedValue.objects.count()


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
