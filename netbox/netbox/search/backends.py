import logging
from collections import defaultdict

import netaddr
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import DatabaseError, ProgrammingError, transaction
from django.db.models import F, Q, Window, prefetch_related_objects
from django.db.models.fields.related import ForeignKey
from django.db.models.functions import window
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

DEFAULT_LOOKUP_TYPE = LookupTypes.PARTIAL
MAX_RESULTS = 1000

logger = logging.getLogger(__name__)


class SearchBackend:
    """
    Base class for search backends. Subclasses must extend the `cache()`, `remove()`, and `clear()`
    methods below.
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

    # caching_handler() and removal_handler() are the default, synchronous signal receivers; they are
    # connected to post_save/post_delete from netbox.search.signals (wired from CoreConfig.ready()).
    # They are internal plumbing for signal dispatch, not a documented extension point: the public
    # backend contract is cache()/remove()/clear(). A backend that needs to do something other than
    # index inline (e.g. defer the work) overrides these in its subclass; see CachedValueSearchBackend.
    def caching_handler(self, sender, instance, created, **kwargs):
        """
        Receiver for the post_save signal, responsible for caching object creation/changes.
        """
        try:
            self.cache(instance, remove_existing=not created)
        except ProgrammingError as e:
            # The schema may be incomplete during migrations; skip caching.
            logger.warning(f"Skipping search cache update due to schema error: {e}")
            pass

    def removal_handler(self, sender, instance, **kwargs):
        """
        Receiver for the post_delete signal, responsible for caching object deletion.
        """
        self.remove(instance)

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

    # These override the base's synchronous receivers to defer indexing past the response. They are
    # the seam where this backend captures the `using` alias Django passes to post_save/post_delete:
    # the deferred write runs after the transaction commits (and possibly in a worker), by which point
    # the originating routing context is gone, so the alias must be captured here and replayed on the
    # deferred write to keep cache entries in the originating schema (e.g. a branch schema under
    # netbox-branching). Deferral is internal to this backend; the public contract is unchanged.
    #
    # mark_for_deferred_indexing() etc. are imported inside each method rather than at module level:
    # this module's own top would import deferred.py *before* search_backend is defined further down
    # this same file, and deferred.py (plus jobs.py) need that singleton at their own module level.
    # A module-level import here would close that loop into a backends -> deferred -> backends
    # cycle. See #22485.
    def caching_handler(self, sender, instance, created, using=None, **kwargs):
        """
        Receiver for the post_save signal, responsible for caching object creation/changes.
        """
        from .deferred import OP_CACHE, mark_for_deferred_indexing

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
        from .deferred import OP_REMOVE, mark_for_deferred_indexing

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

    # `using` here is a PostgreSQL/schema concern specific to this backend's deferred-write path (it
    # replays the originating alias so branch writes land in the branch schema). It is deliberately
    # NOT on the base cache()/remove() contract: a non-PostgreSQL backend (Redis, Solr, etc.) has no
    # such concept. Do not lift `using` onto the base for symmetry; doing so would leak this backend's
    # storage model into the generic contract.
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

    # Postgres SQLSTATEs indicating this backend's own CachedValue table (or the schema it lives in)
    # no longer exists. This happens when a branch is merged or deprovisioned (its schema, and every
    # table in it including its copy of CachedValue, dropped) between the time an update was enqueued
    # and when it is applied. There is nothing to write to and nothing worth retrying -- a later write
    # for a surviving branch's CachedValue table is unaffected -- so this is expected and safe to
    # skip. Any other DatabaseError (e.g. a deadlock, lost connection, or CachedValue itself being out
    # of sync with a not-yet-migrated deployment) is not expected and must propagate so the work fails
    # visibly, rather than silently dropping index updates. This set applies to every write this
    # backend makes to CachedValue (removals below, and the remove+insert inside the cache loop) --
    # deliberately not to reads of the model being indexed; see _STALE_INDEX_TARGET_SQLSTATES for
    # that.
    _MISSING_CACHE_TABLE_SQLSTATES = frozenset((
        '3F000',  # invalid_schema_name
        '42P01',  # undefined_table
    ))

    # Additionally tolerated when reading the model being (re)indexed -- not when writing to
    # CachedValue (see _MISSING_CACHE_TABLE_SQLSTATES above, which this extends). A plugin whose
    # models are dynamically regenerated per branch (e.g. netbox-custom-objects) resolves
    # ObjectType.model_class() to a branch-unaware class pinned to main; if a branch has renamed or
    # removed a column since an update was enqueued, that stale class's column no longer matches the
    # branch's live table, and reading it raises undefined_column rather than undefined_table.
    # Unlike a dropped schema, this is *not* self-healing on "the next reindex": model_class()
    # resolves the same stale, main-pinned class every time, so the object stays unindexed until the
    # branch is merged or reverted. Scoping this to the read only -- rather than folding it into
    # _MISSING_CACHE_TABLE_SQLSTATES broadly -- keeps a genuine defect in the write path (e.g. code
    # deployed against a database that has not yet been migrated, which would also raise
    # undefined_column) from being silently downgraded to a warning.
    #
    # This covers only the top-level read of the model's own columns, not a related object a search
    # index's to_cache() might lazily traverse into (e.g. a relational field indexed with a positive
    # search_weight): such a traversal issues its own query inside the write step below, which does
    # not tolerate undefined_column. A plugin whose indexed fields never reference another of its own
    # dynamically-regenerated models is unaffected; one that does would need a plugin-side fix (making
    # ObjectType.model_class() branch-aware) rather than a wider exemption here.
    _STALE_INDEX_TARGET_SQLSTATES = _MISSING_CACHE_TABLE_SQLSTATES | frozenset((
        '42703',  # undefined_column
    ))

    def _is_missing_cache_table(self, exc):
        """
        Return True if the given DatabaseError was caused by CachedValue's own schema/table no longer
        existing (vs. a transient error that should propagate). Covers writes to CachedValue; see
        _is_stale_index_target() for the read side of a deferred update.
        """
        sqlstate = getattr(getattr(exc, '__cause__', None), 'sqlstate', None)
        return sqlstate in self._MISSING_CACHE_TABLE_SQLSTATES

    def _is_stale_index_target(self, exc):
        """
        Return True if the given DatabaseError was caused by the model being (re)indexed no longer
        matching what was expected when the update was enqueued -- its schema or table (as for
        _is_missing_cache_table()), or, for a model whose columns can themselves diverge per branch,
        an individual column.
        """
        sqlstate = getattr(getattr(exc, '__cause__', None), 'sqlstate', None)
        return sqlstate in self._STALE_INDEX_TARGET_SQLSTATES

    def _apply_deferred_updates(self, using=None, cache_groups=None, remove_groups=None, log=logger):
        """
        Apply a coalesced batch of updates to the search cache. Private to this backend; called by the
        deferred-flush machinery (netbox.search.deferred) and the background job
        (netbox.search.jobs.SearchCacheJob), not part of the public backend contract.

        The `using` alias captured when each object was saved/deleted is replayed here so entries are
        written to the originating database/schema (e.g. a branch schema under netbox-branching),
        regardless of any routing context that is no longer active by the time this runs.
        """
        for object_type_id, pks in (remove_groups or {}).items():
            # Resolved once and reused for both the atomic() block and the delete below: passing
            # `using` straight through when it's falsy would let transaction.atomic() default to
            # DEFAULT_DB_ALIAS while _remove_by_id() defers to the router (see cache()'s own comment
            # on this) -- the savepoint would then belong to a different connection than the one the
            # DELETE actually runs on, on any deployment where CachedValue is routed elsewhere.
            db = using or CachedValue.objects.db
            try:
                # A tolerated DatabaseError still needs a savepoint to roll back to: without one,
                # Postgres leaves the connection's enclosing transaction aborted (refusing every
                # further statement in it until a rollback) even though the Python exception was
                # caught, breaking every later iteration of this loop -- not just this one.
                with transaction.atomic(using=db):
                    self._remove_by_id(object_type_id, pks, using=db)
            except DatabaseError as e:
                if not self._is_missing_cache_table(e):
                    raise
                log.warning(
                    f"Skipping search cache removal for object type {object_type_id}: "
                    f"CachedValue's own table or schema no longer exists ({e})"
                )

        for object_type_id, pks in (cache_groups or {}).items():
            try:
                object_type = ObjectType.objects.get(pk=object_type_id)
            except ObjectType.DoesNotExist:
                continue
            model = object_type.model_class()
            if model is None:
                continue

            # Resolved once per group, for the same reason as the removal loop above -- and kept
            # separate for the read vs. the write, since a router could place the indexed model and
            # CachedValue on different aliases (in which case no single atomic() spans both anyway;
            # see the outer/inner split below).
            read_db = using or model._default_manager.db
            write_db = using or CachedValue.objects.db

            try:
                # The outer atomic() makes the delete+insert pair below a single write. It does
                # *not* give the read a consistent snapshot with that write -- PostgreSQL's default
                # (and NetBox's) READ COMMITTED isolation takes a fresh snapshot per statement
                # regardless of transaction boundaries, so a concurrent update can still land
                # between the read and the write either way. That race is pre-existing and benign:
                # the concurrent save schedules its own deferred update, so the object is reindexed
                # again regardless of which value this pass happened to write.
                #
                # Nested inside it, the read gets its own savepoint so a tolerated failure there
                # (see _is_stale_index_target(), which tolerates a wider set of SQLSTATES than a
                # write to CachedValue does) rolls back only the read, without ever reaching -- or
                # needing to roll back -- the write.
                with transaction.atomic(using=write_db):
                    try:
                        with transaction.atomic(using=read_db):
                            # Reading on `read_db` is required: a branch object's PK may be absent
                            # (or refer to a different object) on the default connection.
                            instances = list(model.objects.using(read_db).filter(pk__in=pks))
                    except DatabaseError as e:
                        if not self._is_stale_index_target(e):
                            raise
                        log.warning(
                            f"Skipping search cache update for object type {object_type_id}: the "
                            f"indexed model no longer matches its table, e.g. a branch-diverged "
                            f"column ({e})"
                        )
                        continue

                    # Clear any stale entries for these objects, then re-insert. Wrapping both in
                    # one transaction avoids leaving an object with no cache rows if execution fails
                    # between the delete and the insert.
                    self._remove_by_id(object_type_id, pks, using=write_db)
                    self.cache(instances, remove_existing=False, using=write_db)
            except DatabaseError as e:
                if not self._is_missing_cache_table(e):
                    raise
                log.warning(
                    f"Skipping search cache update for object type {object_type_id}: "
                    f"CachedValue's own table or schema no longer exists ({e})"
                )

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
