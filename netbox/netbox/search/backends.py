import logging
from collections import defaultdict

import netaddr
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import ProgrammingError
from django.db.models import F, Q, Window, prefetch_related_objects
from django.db.models.fields.related import ForeignKey
from django.db.models.functions import window
from django.db.models.signals import post_delete, post_save
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from netaddr.core import AddrFormatError

from core.models import ObjectType
from extras.models import CachedValue, CustomField
from netbox.registry import registry
from utilities.object_types import object_type_identifier
from utilities.querysets import RestrictedPrefetch
from utilities.string import title

from . import FieldTypes, LookupTypes, get_indexer
from .deferred import OP_CACHE, OP_REMOVE, mark_for_deferred_indexing

DEFAULT_LOOKUP_TYPE = LookupTypes.PARTIAL
MAX_RESULTS = 1000

logger = logging.getLogger(__name__)


class SearchBackend:
    """
    Base class for search backends. Subclasses must extend the `cache()`, `remove()`, and `clear()` methods below.
    """
    _object_types = None

    def get_object_types(self):
        """
        Return a list of all registered object types, organized by category, suitable for populating a form's
        ChoiceField.
        """
        if not self._object_types:

            # Organize choices by category
            categories = defaultdict(dict)
            for label, idx in registry['search'].items():
                categories[idx.get_category()][label] = _(title(idx.model._meta.verbose_name))

            # Compile a nested tuple of choices for form rendering
            results = (
                ('', 'All Objects'),
                *[(category, list(choices.items())) for category, choices in categories.items()]
            )

            self._object_types = results

        return self._object_types

    def search(self, value, user=None, object_types=None, lookup=DEFAULT_LOOKUP_TYPE):
        """
        Search cached object representations for the given value.
        """
        raise NotImplementedError

    def caching_handler(self, sender, instance, created, using=None, **kwargs):
        """
        Receiver for the post_save signal, responsible for caching object creation/changes.
        """
        # Skip non-cacheable objects without scheduling any deferred work.
        try:
            indexer = get_indexer(instance)
        except KeyError:
            return

        try:
            object_type = ObjectType.objects.get_for_model(indexer.model)
        except ProgrammingError as e:
            # The schema may be incomplete during migrations; skip caching.
            logger.warning(f"Skipping search cache update due to schema error: {e}")
            return

        mark_for_deferred_indexing(object_type.pk, instance.pk, OP_CACHE, using=using)

    def removal_handler(self, sender, instance, using=None, **kwargs):
        """
        Receiver for the post_delete signal, responsible for caching object deletion.
        """
        # Skip non-cacheable objects without scheduling any deferred work.
        try:
            indexer = get_indexer(instance)
        except KeyError:
            return

        try:
            object_type = ObjectType.objects.get_for_model(indexer.model)
        except ProgrammingError as e:
            # The schema may be incomplete during migrations; skip caching.
            logger.warning(f"Skipping search cache update due to schema error: {e}")
            return

        mark_for_deferred_indexing(object_type.pk, instance.pk, OP_REMOVE, using=using)

    def cache(self, instances, indexer=None, remove_existing=True):
        """
        Create or update the cached representation of an instance.
        """
        raise NotImplementedError

    def remove(self, instance):
        """
        Delete any cached representation of an instance.
        """
        raise NotImplementedError

    def clear(self, object_types=None):
        """
        Delete *all* cached data (optionally filtered by object type).
        """
        raise NotImplementedError

    def count(self, object_types=None):
        """
        Return a count of all cache entries (optionally filtered by object type).
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

    def search(self, value, user=None, object_types=None, lookup=DEFAULT_LOOKUP_TYPE):

        # Build the filter used to find relevant CachedValue records
        query_filter = Q(**{f'value__{lookup}': value})
        if object_types:
            # Limit results by object type
            query_filter &= Q(object_type__in=object_types)
        if lookup in (LookupTypes.STARTSWITH, LookupTypes.ENDSWITH):
            # "Starts/ends with" matches are valid only on string values
            query_filter &= Q(type=FieldTypes.STRING)
        elif lookup in (LookupTypes.PARTIAL, LookupTypes.EXACT):
            try:
                # If the value looks like an IP address, add extra filters for CIDR/INET values
                address = str(netaddr.IPNetwork(value.strip()).cidr)
                query_filter |= Q(type=FieldTypes.INET) & Q(value__net_host=address)
                if lookup == LookupTypes.PARTIAL:
                    query_filter |= Q(type=FieldTypes.CIDR) & Q(value__net_contains_or_equals=address)
            except (AddrFormatError, ValueError):
                pass

        # Construct the base queryset to retrieve matching results
        queryset = CachedValue.objects.filter(query_filter).annotate(
            # Annotate the rank of each result for its object according to its weight
            row_number=Window(
                expression=window.RowNumber(),
                partition_by=[F('object_type'), F('object_id')],
                order_by=[F('weight').asc()],
            )
        )[:MAX_RESULTS]

        # Gather all ObjectTypes present in the search results (used for prefetching related
        # objects). This must be done before generating the final results list, which returns
        # a RawQuerySet.
        object_type_ids = set(queryset.values_list('object_type', flat=True))
        object_types = ObjectType.objects.filter(pk__in=object_type_ids)

        # Construct a Prefetch to pre-fetch only those related objects for which the
        # user has permission to view.
        if user:
            prefetch = (RestrictedPrefetch('object', user, 'view'), 'object_type')
        else:
            prefetch = ('object', 'object_type')

        # Wrap the base query to return only the lowest-weight result for each object
        # Hat-tip to https://blog.oyam.dev/django-filter-by-window-function/ for the solution
        sql, params = queryset.query.sql_with_params()
        results = CachedValue.objects.prefetch_related(*prefetch).raw(
            f"SELECT * FROM ({sql}) t WHERE row_number = 1",
            params
        )

        # Iterate through each ObjectType represented in the search results and prefetch any
        # related objects necessary to render the prescribed display attributes (display_attrs).
        for object_type in object_types:
            model = object_type.model_class()
            indexer = registry['search'].get(object_type_identifier(object_type))
            if not (display_attrs := getattr(indexer, 'display_attrs', None)):
                continue

            # Add ForeignKey fields to prefetch list
            prefetch_fields = []
            for attr in display_attrs:
                field = model._meta.get_field(attr)
                if type(field) is ForeignKey:
                    prefetch_fields.append(f'object__{attr}')

            # Compile a list of all CachedValues referencing this object type, and prefetch
            # any related objects
            if prefetch_fields:
                objects = [r for r in results if r.object_type == object_type]
                prefetch_related_objects(objects, *prefetch_fields)

        # Omit any results pertaining to an object the user does not have permission to view
        ret = []
        for r in results:
            if r.object is not None:
                r.name = str(r.object)
                ret.append(r)

        return ret

    def cache(self, instances, indexer=None, remove_existing=True, using=None):
        custom_fields = None

        # Convert a single instance to an iterable
        if not hasattr(instances, '__iter__'):
            instances = [instances]

        # Determine the queryset manager used to write cache entries. When a
        # database alias is provided (e.g. by a deferred task replaying the alias
        # the originating write used), entries are written to that connection;
        # otherwise the configured router decides. `using` is expected to be a
        # concrete alias or falsy (None) per the caller's contract; a falsy value
        # defers to the router, which is the correct behavior either way.
        manager = CachedValue.objects.using(using) if using else CachedValue.objects

        buffer = []
        counter = 0
        for instance in instances:

            # First item
            if not counter:

                # Determine the indexer
                if indexer is None:
                    try:
                        indexer = get_indexer(instance)
                    except KeyError:
                        break

                # Prefetch any associated custom fields (excluding those with a zero search weight)
                custom_fields = [
                    cf for cf in CustomField.objects.get_for_model(indexer.model)
                    if cf.search_weight > 0
                ]

            # Wipe out any previously cached values for the object
            if remove_existing:
                self.remove(instance, using=using)

            # Generate cache data
            object_type = ObjectType.objects.get_for_model(indexer.model)
            for field in indexer.to_cache(instance, custom_fields=custom_fields):
                buffer.append(
                    CachedValue(
                        object_type=object_type,
                        object_id=instance.pk,
                        field=field.name,
                        type=field.type,
                        weight=field.weight,
                        value=field.value
                    )
                )

            # Check whether the buffer needs to be flushed
            if len(buffer) >= 2000:
                counter += len(manager.bulk_create(buffer))
                buffer = []

        # Final buffer flush
        if buffer:
            counter += len(manager.bulk_create(buffer))

        return counter

    def _remove_by_id(self, object_type_id, object_ids, using=None):
        """
        Delete cached values for the given content type and object IDs using a
        single raw DELETE. Shared by remove() and the deferred search task.
        """
        if not object_ids:
            return None

        qs = CachedValue.objects.filter(object_type_id=object_type_id, object_id__in=object_ids)

        # Call _raw_delete() on the queryset to avoid first loading instances into memory
        return qs._raw_delete(using=using or qs.db)

    def remove(self, instance, using=None):
        # Avoid attempting to query for non-cacheable objects
        try:
            indexer = get_indexer(instance)
        except KeyError:
            return None

        # Use the indexer's (concrete) model to resolve the object type, matching
        # the content type that cache() writes entries under.
        object_type = ObjectType.objects.get_for_model(indexer.model)

        return self._remove_by_id(object_type.pk, [instance.pk], using=using)

    def clear(self, object_types=None):
        qs = CachedValue.objects.all()
        if object_types:
            qs = qs.filter(object_type__in=object_types)

        # Call _raw_delete() on the queryset to avoid first loading instances into memory
        return qs._raw_delete(using=qs.db)

    def count(self, object_types=None):
        qs = CachedValue.objects.all()
        if object_types:
            qs = qs.filter(object_type__in=object_types)
        return qs.count()

    @property
    def size(self):
        return CachedValue.objects.count()


def get_backend():
    """
    Initializes and returns the configured search backend.
    """
    try:
        backend_cls = import_string(settings.SEARCH_BACKEND)
    except AttributeError:
        raise ImproperlyConfigured(f"Failed to import configured SEARCH_BACKEND: {settings.SEARCH_BACKEND}")

    # Initialize and return the backend instance
    return backend_cls()


search_backend = get_backend()

# Connect handlers to the appropriate model signals
post_save.connect(search_backend.caching_handler)
post_delete.connect(search_backend.removal_handler)
