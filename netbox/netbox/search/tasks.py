import logging

from django.db import DatabaseError, transaction

from core.models import ObjectType
from netbox.jobs import JobRunner
from netbox.search.backends import search_backend

# Internal search-indexing machinery; not part of the public/plugin API.

logger = logging.getLogger(__name__)

# Postgres SQLSTATEs indicating the target schema/table no longer exists. This
# happens when a branch is merged or deprovisioned (its schema dropped) between
# the time an update was enqueued and when this job runs. Such errors are
# expected and safe to skip; the index is rebuilt on the next reindex. Any other
# DatabaseError (e.g. a deadlock or lost connection) is transient and must
# propagate so the job fails visibly and can be retried, rather than silently
# dropping index updates.
_MISSING_SCHEMA_SQLSTATES = frozenset((
    '3F000',  # invalid_schema_name
    '42P01',  # undefined_table
))


def _is_missing_schema(exc):
    """
    Return True if the given DatabaseError was caused by the target schema/table
    no longer existing (vs. a transient error that should propagate).
    """
    sqlstate = getattr(getattr(exc, '__cause__', None), 'sqlstate', None)
    return sqlstate in _MISSING_SCHEMA_SQLSTATES


def update_search_cache(using=None, cache_groups=None, remove_groups=None, log=logger):
    """
    Apply a coalesced batch of updates to the global search cache.

    The `using` alias captured when each object was saved/deleted is replayed
    here so that cache entries are written to the originating database/schema
    (e.g. a branch schema under netbox-branching), regardless of any routing
    context that is no longer active by the time this runs.

    Args:
        using: The database alias to read objects from and write cache entries to.
        cache_groups: Mapping of {object_type_id: [pk, ...]} to (re)index.
        remove_groups: Mapping of {object_type_id: [pk, ...]} to remove.
        log: Logger to use (the job logger when run as a background job).
    """
    for object_type_id, pks in (remove_groups or {}).items():
        try:
            search_backend._remove_by_id(object_type_id, pks, using=using)
        except DatabaseError as e:
            if not _is_missing_schema(e):
                raise
            # The target schema no longer exists (e.g. a branch was merged or
            # deprovisioned between enqueue and execution). Skip; the index will
            # be rebuilt on the next reindex.
            log.warning(f"Skipping search cache removal for object type {object_type_id}: {e}")

    for object_type_id, pks in (cache_groups or {}).items():
        try:
            object_type = ObjectType.objects.get(pk=object_type_id)
        except ObjectType.DoesNotExist:
            continue
        model = object_type.model_class()
        if model is None:
            continue

        try:
            # Re-fetch live instances from the originating database. Reading on
            # `using` is required: a branch object's PK may be absent (or refer to
            # a different object) on the default connection.
            queryset = model.objects.using(using).filter(pk__in=pks)

            # Clear any stale entries for these objects, then re-insert. Wrapping
            # both in one transaction avoids leaving an object with no cache rows
            # if execution fails between the delete and the insert.
            with transaction.atomic(using=using):
                search_backend._remove_by_id(object_type_id, pks, using=using)
                search_backend.cache(queryset, remove_existing=False, using=using)
        except DatabaseError as e:
            if not _is_missing_schema(e):
                raise
            log.warning(f"Skipping search cache update for object type {object_type_id}: {e}")


class SearchCacheJob(JobRunner):
    """
    Background job which applies deferred updates to the global search cache.
    """
    class Meta:
        name = 'Search cache update'

    def run(self, using=None, cache_groups=None, remove_groups=None, **kwargs):
        update_search_cache(
            using=using,
            cache_groups=cache_groups,
            remove_groups=remove_groups,
            log=self.logger,
        )
