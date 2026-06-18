import logging

from django.db import DEFAULT_DB_ALIAS, connections, transaction
from redis.exceptions import RedisError

from netbox.constants import RQ_QUEUE_DEFAULT
from utilities.rqworker import any_workers_for_queue

# This module is internal plumbing for the search signal handlers; nothing here
# is part of the public/plugin API, so no symbols are exported via __all__.

logger = logging.getLogger(__name__)

# Operation markers stored in the per-transaction buffer
OP_CACHE = 'cache'
OP_REMOVE = 'remove'

# Attributes used to tag a flush callback so we can recognize our own callbacks
# among those registered on a connection and reach the batch they will flush.
_FLUSH_ALIAS_ATTR = '_netbox_search_flush_alias'
_FLUSH_BATCH_ATTR = '_netbox_search_flush_batch'


def mark_for_deferred_indexing(object_type_id, pk, op, using=None):
    """
    Schedule a searchable object for deferred (re)indexing.

    The work is coalesced per database connection and per transaction: repeated
    operations on the same object collapse to a single entry (a deletion always
    wins over a create/update), and a single flush is scheduled to run after the
    transaction commits. When no transaction is open (autocommit), the indexing
    runs synchronously.

    Args:
        object_type_id: PK of the object's ObjectType/ContentType.
        pk: PK of the object.
        op: OP_CACHE or OP_REMOVE.
        using: The database alias the originating write used. Replayed verbatim
            on the deferred write so the cache entries land in the same schema
            (e.g. a branch schema under netbox-branching), regardless of any
            routing context that may be unset by the time the flush runs.
    """
    alias = using or DEFAULT_DB_ALIAS
    connection = connections[alias]

    # No transaction in progress: index synchronously. Deferring would have
    # nothing to defer past, and transaction.on_commit() in autocommit mode runs
    # its callback immediately at registration (before we could populate the
    # batch), so handle this case explicitly.
    #
    # On the transactional path below, transaction.on_commit(..., robust=True)
    # ensures a flush failure can never propagate to the (already-committed)
    # caller. The autocommit path has no such backstop, so guard it here: a
    # broad catch is deliberate, because the originating write has committed and
    # a search cache update must never turn a successful save into an error. The
    # error is logged so a genuine indexing defect is still visible.
    if not connection.in_atomic_block:
        try:
            _flush({(object_type_id, pk): op}, alias)
        except Exception:
            logger.exception("Search cache: error while indexing inline")
        return

    # Find the batch for a flush already scheduled for this alias in the current
    # transaction. Django clears a connection's run_on_commit list on both commit
    # and rollback, so any callback we find there belongs to the current
    # (uncommitted) transaction -- no stale state can survive a rollback.
    batch = _pending_batch(connection, alias)
    if batch is None:
        batch = {}

        def flush(batch=batch, alias=alias):
            _flush(batch, alias)

        setattr(flush, _FLUSH_ALIAS_ATTR, alias)
        setattr(flush, _FLUSH_BATCH_ATTR, batch)
        # robust=True is required, not just belt-and-suspenders: Django runs
        # on_commit callbacks synchronously as the atomic block exits (after the
        # COMMIT), so an exception escaping the callback would propagate out of
        # the view's transaction and become a 500 on an already-committed write.
        # _flush handles the recoverable Redis fault itself; robust=True is the
        # only thing that keeps any *other* failure here (logged by Django at
        # ERROR) from surfacing as that post-commit 500.
        transaction.on_commit(flush, using=alias, robust=True)

    # Coalesce: a deletion supersedes any pending create/update for the object.
    key = (object_type_id, pk)
    if op == OP_REMOVE or batch.get(key) != OP_REMOVE:
        batch[key] = op


def _pending_batch(connection, alias):
    """
    Return the batch dict of a flush callback already scheduled for the given
    alias on this connection's current transaction, or None if there is none.

    This scans `connection.run_on_commit` on each call rather than caching the
    lookup elsewhere. That is intentional: the scan is bounded (run_on_commit
    holds only the transaction's registered commit callbacks, not one per saved
    object), and reading it fresh each time is what keeps the buffer correctly
    scoped to the live transaction. Django clears run_on_commit on both commit
    and rollback, so a rolled-back transaction's batch can never be found here.
    """
    for _sids, func, _robust in connection.run_on_commit:
        if getattr(func, _FLUSH_ALIAS_ATTR, None) == alias:
            return getattr(func, _FLUSH_BATCH_ATTR)
    return None


def _flush(batch, using):
    """
    Dispatch a coalesced batch of dirty objects for (re)indexing.

    `_flush` is the single guarded entry point for deferred indexing, reached
    either directly (autocommit) or from a transaction.on_commit callback. By the
    time it runs the originating write has already committed, so it must never
    propagate an error back to the caller and turn a successful save into a 500.

    The inline fallback is safe even during a broker outage: the search index
    lives in PostgreSQL (the extras_cachedvalue table), so a Redis outage only
    prevents backgrounding, not indexing itself.

    If the broker fails mid-enqueue (after the probe succeeds), Job.enqueue() has
    already saved a Job row before the Redis dispatch raised, so the fallback can
    leave behind a PENDING Job that no worker will run. The index is still
    correct (written inline); the stranded row is cosmetic and ages out via the
    housekeeping job.
    """
    if not batch:
        return

    cache_groups = {}
    remove_groups = {}
    for (object_type_id, pk), op in batch.items():
        groups = remove_groups if op == OP_REMOVE else cache_groups
        groups.setdefault(object_type_id, []).append(pk)

    # Imported here, not at module load, to avoid an import cycle: backends.py
    # imports this module at module level (for the signal handlers), and
    # netbox.search.tasks imports search_backend from backends.py, which is
    # defined at the bottom of that module. A proper fix is tracked in #22485.
    from netbox.search.tasks import SearchCacheJob, update_search_cache

    try:
        # Both the worker-availability check and the job enqueue talk to Redis,
        # and a worker can die between the two. Treat any Redis failure across the
        # whole dispatch as "no worker available" and fall back to inline
        # indexing (a PostgreSQL write that does not depend on Redis).
        if any_workers_for_queue(RQ_QUEUE_DEFAULT):
            SearchCacheJob.enqueue(using=using, cache_groups=cache_groups, remove_groups=remove_groups)
            return
    except RedisError:
        logger.warning("Search cache: broker unavailable; indexing inline", exc_info=True)

    update_search_cache(using=using, cache_groups=cache_groups, remove_groups=remove_groups)
