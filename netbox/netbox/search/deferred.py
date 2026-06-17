import logging

from django.db import DEFAULT_DB_ALIAS, connections, transaction

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


def mark_dirty(object_type_id, pk, op, using=None):
    """
    Record a searchable object as dirty for deferred (re)indexing.

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
    if not connection.in_atomic_block:
        _flush({(object_type_id, pk): op}, alias)
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
        transaction.on_commit(flush, using=alias)

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
    Dispatch a coalesced batch of dirty objects for (re)indexing. Enqueues a
    background job when an RQ worker is available, otherwise runs the indexing
    synchronously inline (preserving pre-deferral behavior on installs without a
    running worker).
    """
    if not batch:
        return

    # Group object IDs by content type and operation.
    cache_groups = {}
    remove_groups = {}
    for (object_type_id, pk), op in batch.items():
        groups = remove_groups if op == OP_REMOVE else cache_groups
        groups.setdefault(object_type_id, []).append(pk)

    # Imported here (not at module load) to avoid an import cycle: backends.py
    # connects the search signals at import time, and these pull in netbox.config.
    from netbox.constants import RQ_QUEUE_DEFAULT
    from netbox.search.tasks import SearchCacheJob, update_search_cache
    from utilities.rqworker import any_workers_for_queue

    if any_workers_for_queue(RQ_QUEUE_DEFAULT):
        SearchCacheJob.enqueue(using=using, cache_groups=cache_groups, remove_groups=remove_groups)
    else:
        # No worker available: index synchronously, bypassing the Job framework
        # (a Job record would never be picked up without a worker).
        update_search_cache(using=using, cache_groups=cache_groups, remove_groups=remove_groups)
