import logging

from django.db import DEFAULT_DB_ALIAS

from netbox.jobs import JobRunner, system_job
from netbox.search.backends import search_backend

# Internal search-indexing machinery; not part of the public/plugin API.

logger = logging.getLogger(__name__)


class SearchCacheJob(JobRunner):
    """
    Background job which applies deferred updates to the global search cache.
    """
    class Meta:
        name = 'Search cache update'

    def run(self, using=None, cache_groups=None, remove_groups=None, **kwargs):
        using = using or DEFAULT_DB_ALIAS

        # Back-compat: a job enqueued by a pre-coalescing version carried the
        # dirty objects directly. Apply them as-is so in-flight legacy jobs keep
        # working across a rolling upgrade. Serialize with a concurrent new-style
        # drain via the same advisory lock so the two can't apply the same object
        # concurrently (which would duplicate CachedValue rows). wait=True: a
        # legacy job carries its own one-shot batch and cannot be retried, so it
        # must not skip.
        if cache_groups or remove_groups:
            from django_pg_utils import advisory_lock

            from netbox.search.deferred import _apply_lock_key
            with advisory_lock(_apply_lock_key(using), wait=True, using=using):
                search_backend._apply_deferred_updates(
                    using=using,
                    cache_groups=cache_groups,
                    remove_groups=remove_groups,
                    log=self.logger,
                )
            return

        # Imported here to avoid a module-level circular import: deferred.py
        # imports this module for SearchCacheJob.
        from netbox.search import deferred
        deferred.drain_and_apply(using, self.logger)


@system_job(interval=5)
class SearchCacheSafetyNetJob(JobRunner):
    """
    Periodic sweep that recovers deferred search-cache batches which were never
    applied (e.g. the worker meant to drain them died, or application failed
    part-way through). Retained staging data is retried; the batch is deleted
    only once it has been applied successfully.
    """
    class Meta:
        name = 'Search cache flush safety net'

    def run(self, *args, **kwargs):
        from netbox.search import deferred
        deferred.drain_stranded(self.logger)
