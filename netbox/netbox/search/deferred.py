import logging
import time
import uuid
from datetime import timedelta

from django.db import DEFAULT_DB_ALIAS, connections, transaction
from django.utils import timezone
from django_pg_utils import advisory_lock
from django_rq.queues import get_connection
from redis.exceptions import RedisError, ResponseError

from netbox.constants import RQ_QUEUE_DEFAULT
from netbox.search.backends import search_backend
from netbox.search.jobs import SearchCacheJob
from utilities.rqworker import any_workers_for_queue

# This module is internal plumbing for the search signal handlers; nothing here
# is part of the public/plugin API, so no symbols are exported via __all__.

logger = logging.getLogger(__name__)

# Operation markers stored in the per-transaction buffer
OP_CACHE = 'cache'
OP_REMOVE = 'remove'

# Cross-transaction coalescing buffer. Committed batches accumulate in a
# per-alias Redis hash on the tasks connection and are drained by a single
# scheduled SearchCacheJob, so N committed transactions produce roughly one job
# instead of N (the regression this replaces).
FLUSH_INTERVAL = 2  # Seconds to coalesce before draining.
LOCK_TTL = 60       # Seconds; scheduling throttle lease (one drain scheduled per alias).
APPLY_LEASE = 60    # Seconds; per-batch processing lease (one applier per batch).

# A persistently failing batch is retried by the safety net until it has failed
# this many times, then dropped with an error-level log; the affected objects
# stay unindexed until re-saved or `manage.py reindex` is run. The cap stops one
# poisoned batch from blocking indexing of unrelated objects forever.
MAX_APPLY_ATTEMPTS = 5

PENDING_PREFIX = 'netbox:search:pending:'
LOCK_PREFIX = 'netbox:search:flush-lock:'
STAGING_PREFIX = 'netbox:search:draining:'
LEASE_PREFIX = 'netbox:search:draining-lease:'
ATTEMPTS_PREFIX = 'netbox:search:apply-attempts:'
# Bounds growth of a batch's failure counter if its staging key disappears
# through another path (e.g. a worker that crashed before writing the counter).
ATTEMPTS_TTL = 3600

# Attributes used to tag a flush callback so we can recognize our own callbacks
# among those registered on a connection and reach the batch they will flush.
_FLUSH_ALIAS_ATTR = '_netbox_search_flush_alias'
_FLUSH_BATCH_ATTR = '_netbox_search_flush_batch'
# The savepoint stack active when a flush callback was registered; see
# _pending_batch() for why buffering is scoped to it.
_FLUSH_SCOPE_ATTR = '_netbox_search_flush_scope'


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
    # Fall back to the default alias when no originating alias was captured. This is correct for the
    # common case (autocommit / non-branch writes route to the default connection), but if a write
    # under a branch schema ever reached here without its alias, the deferred write would silently
    # land in the main schema. Log at debug so that case is observable rather than invisible.
    if not using:
        logger.debug("Search cache: no originating DB alias for object %s/%s; using default", object_type_id, pk)
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

    # Scope buffering to the current savepoint stack, not just the alias (see
    # _pending_batch). May legitimately contain None entries for nested
    # atomic(savepoint=False) blocks; matching is by equality, so that is fine.
    scope = tuple(connection.savepoint_ids)

    batch = _pending_batch(connection, alias, scope)
    if batch is None:
        batch = {}

        def flush(batch=batch, alias=alias):
            _flush(batch, alias)

        setattr(flush, _FLUSH_ALIAS_ATTR, alias)
        setattr(flush, _FLUSH_BATCH_ATTR, batch)
        setattr(flush, _FLUSH_SCOPE_ATTR, scope)
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


def _pending_batch(connection, alias, scope):
    """
    Return the batch dict of a flush callback already scheduled for the given
    alias and savepoint scope on this connection's current transaction, or None
    if there is none.

    This scans `connection.run_on_commit` on each call rather than caching the
    lookup elsewhere. That is intentional: the scan is bounded (run_on_commit
    holds only the transaction's registered commit callbacks, not one per saved
    object), and reading it fresh each time is what keeps the buffer correctly
    scoped to the live transaction. Django clears run_on_commit on both commit
    and rollback, so a rolled-back transaction's batch can never be found here.

    Matching on `scope` (the savepoint stack active when the callback was
    registered) as well as `alias` keeps each savepoint scope on its own
    callback. Django prunes a callback when a savepoint in its registration
    snapshot rolls back, so an op buffered inside a nested savepoint is dropped
    with its callback if that savepoint rolls back -- it can never be found here
    and reused by an outer scope.
    """
    for _sids, func, _robust in connection.run_on_commit:
        if (
            getattr(func, _FLUSH_ALIAS_ATTR, None) == alias
            and getattr(func, _FLUSH_SCOPE_ATTR, None) == scope
        ):
            return getattr(func, _FLUSH_BATCH_ATTR)
    return None


def _flush(batch, using):
    """
    Dispatch a coalesced batch of dirty objects for (re)indexing.

    `_flush` is the single guarded entry point for deferred indexing, reached
    either directly (autocommit) or from a transaction.on_commit callback. By the
    time it runs the originating write has already committed, so it must never
    propagate an error back to the caller and turn a successful save into a 500.

    When a worker is available the batch is merged into the shared Redis buffer
    and a single drain is scheduled (see _buffer_and_schedule); committed batches
    from many transactions thus coalesce into far fewer jobs than the
    one-job-per-transaction it replaces. Otherwise it falls back to inline
    indexing, a PostgreSQL write with no Redis dependency.

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

    try:
        has_worker = any_workers_for_queue(RQ_QUEUE_DEFAULT)
    except RedisError:
        has_worker = False

    if has_worker:
        try:
            _buffer_and_schedule(batch, using)
            return
        except RedisError:
            # A worker can die (or the broker can drop) between the availability
            # probe and the buffer write. Fall back to inline indexing. Any
            # pending entry already written is deliberately left in place: it is
            # a recoverable duplicate, and re-applying it is safe because
            # _apply_deferred_updates is idempotent. Deleting it here could
            # discard a concurrent writer's update, which is worse.
            logger.warning("Search cache: broker unavailable; indexing inline", exc_info=True)

    search_backend._apply_deferred_updates(using=using, cache_groups=cache_groups, remove_groups=remove_groups)


def _buffer_and_schedule(batch, using):
    """
    Merge a committed batch into the shared pending hash and ensure exactly one
    drain is scheduled for the alias.
    """
    conn = _connection()
    conn.hset(
        _pending_key(using),
        mapping={_field(object_type_id, pk): op for (object_type_id, pk), op in batch.items()},
    )
    # Only the flush that wins the throttle lock schedules a drain; the rest just
    # merge into the buffer. HSET overwrites a field, so a later op for the same
    # object wins -- the correct cross-batch semantics (a later save supersedes
    # an earlier delete).
    if conn.set(_lock_key(using), '1', nx=True, ex=LOCK_TTL):
        try:
            _schedule(using)
        except Exception:
            # Nothing will run the scheduled drain; release the lock so the
            # safety net (or the next flush) can pick the buffer up promptly.
            conn.delete(_lock_key(using))
            raise


def _schedule(using):
    SearchCacheJob.enqueue(
        using=using,
        schedule_at=timezone.now() + timedelta(seconds=FLUSH_INTERVAL),
    )


def drain_and_apply(using, log=None):
    """
    Claim and apply the pending batch for a single database alias.

    Called by SearchCacheJob after its scheduled delay. The pending hash is moved
    atomically to a durable staging key (see _claim) and applied there, so a
    crash before the work completes leaves the batch recoverable.
    """
    staging = _claim(using)
    if staging is not None:
        _apply_staging(using, staging, log or logger)


def _claim(using):
    """
    Atomically take ownership of the pending hash for an alias.

    RENAME is the claim: exactly one drainer can win it. The resulting staging
    key is immutable (producers only ever write to the pending key), so no update
    buffered while the batch is applied can be lost or overwritten.

    Returns the staging key, or None if there was nothing pending.
    """
    conn = _connection()
    staging = f'{STAGING_PREFIX}{using}:{int(time.time())}:{uuid.uuid4().hex}'
    try:
        conn.rename(_pending_key(using), staging)
    except ResponseError:
        return None
    # Release the throttle once the batch is claimed, so updates arriving during
    # the (potentially slow) apply can schedule a fresh drain rather than being
    # stranded until the safety net runs.
    conn.delete(_lock_key(using))
    return staging


def _apply_staging(using, staging, log):
    """
    Apply a claimed staging batch, deleting it only once application succeeds.

    The per-batch Redis lease is only a cheap pre-filter: it is bounded by
    APPLY_LEASE while the applier can run for up to the job timeout, so the lease
    alone cannot guarantee exclusive execution (the safety net can take a fresh
    lease and start applying the same batch while the original is still running).
    Actual exclusion is provided by a PostgreSQL session-level advisory lock held
    for the whole apply-and-cleanup lifecycle. `_apply_deferred_updates` is
    idempotent, so any retry after the lock is released converges.

    The lease is never deleted by its owner (it only expires), so a slow or
    crashed drainer can never delete a lease a successor has taken over.
    """
    conn = _connection()
    batch_id = staging.rsplit(':', 1)[1]

    if not conn.set(_lease_key(batch_id), '1', nx=True, ex=APPLY_LEASE):
        # Another drainer holds the lease; let it finish.
        return

    data = conn.hgetall(staging)
    if not data:
        conn.delete(staging)
        return

    _warn_if_stale(staging, log)

    cache_groups = {}
    remove_groups = {}
    for raw_field, raw_op in data.items():
        field = raw_field.decode() if isinstance(raw_field, bytes) else raw_field
        op = raw_op.decode() if isinstance(raw_op, bytes) else raw_op
        object_type_id, pk = field.split(':', 1)
        groups = remove_groups if op == OP_REMOVE else cache_groups
        groups.setdefault(int(object_type_id), []).append(int(pk))

    # The advisory lock must span the apply *and* the staging deletion below,
    # otherwise a second applier could acquire it after the apply but before the
    # delete and apply the same batch again, leaving duplicate rows.
    db = using or DEFAULT_DB_ALIAS
    with advisory_lock(_apply_lock_key(db), wait=False, using=db) as acquired:
        if not acquired:
            # Another applier holds the advisory lock: its Redis lease may have
            # expired while it is still running. Do not apply concurrently (that
            # would duplicate rows). It deletes staging on success; if it is
            # killed, PostgreSQL releases the lock when its session ends and the
            # safety net retries the retained batch. Contention is not an apply
            # failure, so it is not counted against MAX_APPLY_ATTEMPTS.
            return

        try:
            search_backend._apply_deferred_updates(
                using=using,
                cache_groups=cache_groups,
                remove_groups=remove_groups,
                log=log,
            )
        except Exception:
            if _record_apply_failure(conn, batch_id) >= MAX_APPLY_ATTEMPTS:
                # Retrying a persistently failing batch forever would block
                # indexing of unrelated objects and grow staging without bound.
                # Drop it with an error-level log; the batch's objects stay
                # unindexed until re-saved or `manage.py reindex` is run.
                log.error(
                    f"Search cache: dropping deferred batch {staging} after "
                    f"{MAX_APPLY_ATTEMPTS} failed apply attempts; run `manage.py reindex` "
                    f"to rebuild the search index",
                    exc_info=True,
                )
                conn.delete(staging)
                conn.delete(_attempts_key(batch_id))
                return
            raise

        # Retained until this returns without raising: a crash or database error
        # leaves the staging key for the safety net to retry.
        conn.delete(staging)
        conn.delete(_attempts_key(batch_id))

    # Updates that arrived while this batch was being applied land in a fresh
    # pending hash; schedule one more drain if none is already scheduled.
    if conn.exists(_pending_key(using)) and conn.set(_lock_key(using), '1', nx=True, ex=LOCK_TTL):
        _schedule(using)


def drain_stranded(log=None):
    """
    Recover deferred work that no drain is scheduled to apply.

    Scans for abandoned staging batches (a worker crashed or failed mid-apply)
    and for pending hashes with no throttle lock (the drain meant to apply them
    never ran). A no-op when there is nothing to recover, so the safety-net job
    stays cheap.
    """
    log = log or logger
    conn = _connection()

    # Collect first, then apply: claiming a pending hash (RENAME) creates a new
    # staging key, which must not be re-scanned as a stranded batch this pass.
    targets = []
    for raw_key in conn.scan_iter(match=f'{STAGING_PREFIX}*'):
        staging = raw_key.decode() if isinstance(raw_key, bytes) else raw_key
        targets.append((_alias_from_staging(staging), staging))

    for raw_key in conn.scan_iter(match=f'{PENDING_PREFIX}*'):
        pending = raw_key.decode() if isinstance(raw_key, bytes) else raw_key
        using = pending[len(PENDING_PREFIX):]
        if conn.exists(_lock_key(using)):
            # A drain is already scheduled for this alias; leave it alone.
            continue
        staging = _claim(using)
        if staging is not None:
            targets.append((using, staging))

    # Isolate failures: one batch that cannot be applied must not prevent the
    # rest from being recovered. A failed batch is left staged for the next pass
    # (its lease expires).
    for using, staging in targets:
        try:
            _apply_staging(using, staging, log)
        except Exception:
            log.warning(f"Search cache: failed to apply deferred batch {staging}", exc_info=True)


def _record_apply_failure(conn, batch_id):
    """
    Increment and return the failed-apply count for a staging batch, refreshing
    its TTL so the counter cannot outlive the batch indefinitely.
    """
    key = _attempts_key(batch_id)
    attempts = conn.incr(key)
    conn.expire(key, ATTEMPTS_TTL)
    return attempts


def _apply_lock_key(db):
    # A single advisory lock key per database/alias, shared by every background
    # applier (the staged drain and the legacy SearchCacheJob path).
    return f'netbox.search.apply:{db}'


def _warn_if_stale(staging, log):
    """
    Log when a batch has been waiting far longer than a normal apply should take
    (e.g. a database outage), so persistent staging growth is observable.
    """
    try:
        claimed_at = int(staging.rsplit(':', 2)[1])
    except (IndexError, ValueError):
        return
    age = int(time.time() - claimed_at)
    if age > APPLY_LEASE:
        log.warning(f"Search cache: applying a deferred batch claimed {age}s ago ({staging})")


def _connection():
    return get_connection(RQ_QUEUE_DEFAULT)


def _field(object_type_id, pk):
    return f'{object_type_id}:{pk}'


def _pending_key(using):
    return f'{PENDING_PREFIX}{using}'


def _lock_key(using):
    return f'{LOCK_PREFIX}{using}'


def _lease_key(batch_id):
    return f'{LEASE_PREFIX}{batch_id}'


def _attempts_key(batch_id):
    return f'{ATTEMPTS_PREFIX}{batch_id}'


def _alias_from_staging(staging):
    # 'netbox:search:draining:<using>:<epoch>:<batch_id>' -> '<using>'
    return staging[len(STAGING_PREFIX):].rsplit(':', 2)[0]
