import os
import subprocess
import sys
import time
from unittest import mock

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import DEFAULT_DB_ALIAS, ProgrammingError, connection, transaction
from django.db.models.signals import post_delete, post_save
from django.test import TestCase, TransactionTestCase
from redis.exceptions import ConnectionError as RedisConnectionError

from dcim.models import Manufacturer, Site
from dcim.search import SiteIndex
from extras.models import CachedValue
from netbox.search import deferred
from netbox.search.backends import SearchBackend, search_backend
from netbox.search.jobs import SearchCacheJob
from utilities.testing.mixins import RQQueueTestMixin


def scheduled_search_flushes():
    # The deferred flush callbacks scheduled on the current connection,
    # identified by the alias tag set in netbox.search.deferred. Django stores
    # each registered callback as a (savepoint_ids, func, robust) tuple.
    return [
        entry[1] for entry in connection.run_on_commit
        if hasattr(entry[1], deferred._FLUSH_ALIAS_ATTR)
    ]


class SearchBackendTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create sites with a value for each cacheable field defined on SiteIndex
        sites = (
            Site(
                name='Site 1',
                slug='site-1',
                facility='Alpha',
                description='First test site',
                physical_address='123 Fake St Lincoln NE 68588',
                shipping_address='123 Fake St Lincoln NE 68588',
                comments='Lorem ipsum etcetera'
            ),
            Site(
                name='Site 2',
                slug='site-2',
                facility='Bravo',
                description='Second test site',
                physical_address='725 Cyrus Valleys Suite 761 Douglasfort NE 57761',
                shipping_address='725 Cyrus Valleys Suite 761 Douglasfort NE 57761',
                comments='Lorem ipsum etcetera'
            ),
            Site(
                name='Site 3',
                slug='site-3',
                facility='Charlie',
                description='Third test site',
                physical_address='2321 Dovie Dale East Cristobal AK 71959',
                shipping_address='2321 Dovie Dale East Cristobal AK 71959',
                comments='Lorem ipsum etcetera'
            ),
        )
        Site.objects.bulk_create(sites)

    def test_cache_single_object(self):
        """
        Test that a single object is cached appropriately
        """
        site = Site.objects.first()
        search_backend.cache(site)

        content_type = ContentType.objects.get_for_model(Site)
        self.assertEqual(
            CachedValue.objects.filter(object_type=content_type, object_id=site.pk).count(),
            len(SiteIndex.fields)
        )
        for field_name, weight in SiteIndex.fields:
            self.assertTrue(
                CachedValue.objects.filter(
                    object_type=content_type,
                    object_id=site.pk,
                    field=field_name,
                    value=getattr(site, field_name),
                    weight=weight
                ),
            )

    def test_cache_multiple_objects(self):
        """
        Test that multiples objects are cached appropriately
        """
        sites = Site.objects.all()
        search_backend.cache(sites)

        content_type = ContentType.objects.get_for_model(Site)
        self.assertEqual(
            CachedValue.objects.filter(object_type=content_type).count(),
            len(SiteIndex.fields) * sites.count()
        )
        for site in sites:
            for field_name, weight in SiteIndex.fields:
                self.assertTrue(
                    CachedValue.objects.filter(
                        object_type=content_type,
                        object_id=site.pk,
                        field=field_name,
                        value=getattr(site, field_name),
                        weight=weight
                    ),
                )

    def test_cache_on_save(self):
        """
        Test that an object is automatically cached on calling save().
        """
        site = Site(
            name='Site 4',
            slug='site-4',
            facility='Delta',
            description='Fourth test site',
            physical_address='7915 Lilla Plains West Ladariusport TX 19429',
            shipping_address='7915 Lilla Plains West Ladariusport TX 19429',
            comments='Lorem ipsum etcetera'
        )

        # Caching is deferred to a post-commit task. With no RQ worker running in
        # the test environment it falls back to synchronous indexing; execute the
        # on_commit callback to drive it within the test's transaction.
        with self.captureOnCommitCallbacks(execute=True):
            site.save()

        content_type = ContentType.objects.get_for_model(Site)
        self.assertEqual(
            CachedValue.objects.filter(object_type=content_type, object_id=site.pk).count(),
            len(SiteIndex.fields)
        )

    def test_remove_on_delete(self):
        """
        Test that any cached value for an object are automatically removed on delete().
        """
        content_type = ContentType.objects.get_for_model(Site)

        # Seed an object with cached entries, then delete it. Capture the pk before delete() (which
        # nulls instance.pk in memory) so the post-delete assertion queries the real id rather than
        # object_id=None. The create is wrapped in captureOnCommitCallbacks so the deferred caching
        # actually runs (and writes rows) before we assert it was seeded.
        with self.captureOnCommitCallbacks(execute=True):
            site = Site.objects.create(name='Site Delete', slug='site-delete', facility='Foxtrot')
        site_pk = site.pk
        self.assertTrue(
            CachedValue.objects.filter(object_type=content_type, object_id=site_pk).exists()
        )

        with self.captureOnCommitCallbacks(execute=True):
            site.delete()

        self.assertFalse(
            CachedValue.objects.filter(object_type=content_type, object_id=site_pk).exists()
        )

    def test_clear_all(self):
        """
        Test that calling clear() on the backend removes all cached entries.
        """
        sites = Site.objects.all()
        search_backend.cache(sites)
        self.assertTrue(
            CachedValue.objects.exists()
        )

        search_backend.clear()
        self.assertFalse(
            CachedValue.objects.exists()
        )

    def test_search(self):
        """
        Test various searches.
        """
        sites = Site.objects.all()
        search_backend.cache(sites)

        results = search_backend.search('site')
        self.assertEqual(len(results), 3)
        results = search_backend.search('first')
        self.assertEqual(len(results), 1)
        results = search_backend.search('xxxxx')
        self.assertEqual(len(results), 0)


class DeferredCachingTestCase(RQQueueTestMixin, TestCase):
    """
    Tests for the deferred (post-commit) search caching machinery in
    netbox.search.deferred.

    With no RQ worker registered, deferral falls back to synchronous indexing on
    commit, so these tests assert on real CachedValue state and on the real
    per-transaction buffer (connection.run_on_commit) rather than mocking the
    queue.

    Some tests patch the worker probe True and write to the real tasks Redis
    (DB 0). RQQueueTestMixin flushes that database around each test and
    serializes this class against the other Redis-backed suites, so a parallel
    worker's flush can't wipe the coalescing keys mid-test.
    """

    def _scheduled_flush_aliases(self):
        return [getattr(func, deferred._FLUSH_ALIAS_ATTR) for func in scheduled_search_flushes()]

    def _pending_batch(self):
        for func in scheduled_search_flushes():
            return getattr(func, deferred._FLUSH_BATCH_ATTR)
        return None

    def test_run_on_commit_entry_shape(self):
        """
        deferred._pending_batch() relies on Django storing each on_commit
        callback as a (savepoint_ids, func, robust) tuple in
        connection.run_on_commit. That structure is a Django internal, not a
        documented API. Assert its shape explicitly so a change in a future
        Django release fails here with a clear pointer, rather than surfacing as
        an opaque unpack error inside the deferred-caching machinery.
        """
        with transaction.atomic():
            transaction.on_commit(lambda: None)
            entries = connection.run_on_commit
            self.assertTrue(entries, "expected a registered on_commit callback")
            entry = entries[-1]
            self.assertEqual(
                len(entry), 3,
                "Django's connection.run_on_commit entry is no longer a 3-tuple; "
                "netbox.search.deferred._pending_batch() unpacks (sids, func, robust) "
                "and must be updated to match the new structure."
            )
            sids, func, robust = entry
            self.assertIsInstance(sids, set)
            self.assertTrue(callable(func))
            self.assertIsInstance(robust, bool)

    def test_savepoint_ids_shape(self):
        """
        deferred.mark_for_deferred_indexing() reads connection.savepoint_ids to
        scope each flush callback to its savepoint stack. That is a Django
        internal, not a documented API. Assert it is a list inside a nested
        atomic() so a future change fails here rather than silently re-leaking
        nested-savepoint ops into an outer batch.
        """
        with transaction.atomic():
            with transaction.atomic():
                self.assertIsInstance(
                    connection.savepoint_ids, list,
                    "Django's connection.savepoint_ids is no longer a list; "
                    "netbox.search.deferred.mark_for_deferred_indexing() keys its "
                    "flush callbacks on tuple(savepoint_ids) and must be updated."
                )
                self.assertTrue(
                    connection.savepoint_ids,
                    "expected at least one savepoint id inside a nested atomic()"
                )

    def test_bulk_save_schedules_single_flush(self):
        """
        A batch of saves within one transaction coalesces into a single flush
        carrying every object, rather than one scheduled flush per object.
        """
        site_ct = ContentType.objects.get_for_model(Site)
        with transaction.atomic():
            for i in range(20):
                Site.objects.create(name=f'Site {i}', slug=f'site-{i}')

            # Exactly one flush is scheduled, and its batch holds all 20 objects.
            self.assertEqual(self._scheduled_flush_aliases().count('default'), 1)
            batch = self._pending_batch()
            site_pks = [pk for (ot_id, pk) in batch if ot_id == site_ct.pk]
            self.assertEqual(len(site_pks), 20)

    def test_save_then_delete_in_same_scope_coalesces_to_removal(self):
        """
        A create and delete buffered in the same savepoint scope coalesce to a
        single removal. Model.delete() runs in its own atomic(savepoint=False)
        block, which pushes a scope marker, so to exercise coalescing within one
        scope the operations are buffered directly rather than via a real
        delete().
        """
        site_ct = ContentType.objects.get_for_model(Site)
        with transaction.atomic():
            deferred.mark_for_deferred_indexing(site_ct.pk, 1, deferred.OP_CACHE)
            deferred.mark_for_deferred_indexing(site_ct.pk, 1, deferred.OP_REMOVE)
            batch = self._pending_batch()
            self.assertEqual(batch[(site_ct.pk, 1)], deferred.OP_REMOVE)

    def test_save_then_delete_ends_absent_from_cache(self):
        """
        Creating then deleting an object within one transaction leaves it absent
        from the cache, regardless of how the create and delete ops are scoped.
        """
        site_ct = ContentType.objects.get_for_model(Site)
        with self.captureOnCommitCallbacks(execute=True):
            site = Site.objects.create(name='Ephemeral', slug='ephemeral')
            pk = site.pk
            site.delete()

        self.assertFalse(
            CachedValue.objects.filter(object_type=site_ct, object_id=pk).exists()
        )

    def test_rollback_does_not_leak_buffer(self):
        """
        An object dirtied inside a transaction that rolls back leaves no flush
        scheduled and no stale buffer behind, so it is never indexed.
        """
        content_type = ContentType.objects.get_for_model(Site)

        # A nested atomic block that rolls back: its on_commit callback (and the
        # batch it captured) are discarded by Django, so nothing is scheduled on
        # the surrounding transaction.
        with self.assertRaises(RuntimeError):
            with transaction.atomic():
                rolled_back = Site.objects.create(name='RolledBack', slug='rolled-back')
                rolled_back_pk = rolled_back.pk
                # A flush was scheduled within this savepoint...
                self.assertEqual(self._scheduled_flush_aliases().count('default'), 1)
                raise RuntimeError('abort')

        # ...and is gone once the savepoint rolled back.
        self.assertEqual(self._scheduled_flush_aliases().count('default'), 0)
        self.assertFalse(
            CachedValue.objects.filter(object_type=content_type, object_id=rolled_back_pk).exists()
        )

    def test_commit_after_rollback_still_indexes(self):
        """
        After a rolled-back transaction, a subsequent committed save on the same
        connection still indexes correctly (no sticky buffer state survives the
        rollback to suppress it).
        """
        content_type = ContentType.objects.get_for_model(Site)

        with self.assertRaises(RuntimeError):
            with transaction.atomic():
                Site.objects.create(name='RolledBack2', slug='rolled-back-2')
                raise RuntimeError('abort')

        with self.captureOnCommitCallbacks(execute=True):
            site = Site.objects.create(
                name='Committed',
                slug='committed',
                facility='Echo',
                description='Committed after rollback',
                physical_address='1 Test Way',
                shipping_address='1 Test Way',
                comments='Lorem ipsum',
            )

        # The committed object is indexed (no sticky buffer state from the
        # rolled-back transaction suppressed it).
        self.assertEqual(
            CachedValue.objects.filter(object_type=content_type, object_id=site.pk).count(),
            len(SiteIndex.fields)
        )

    def test_non_searchable_model_schedules_no_flush(self):
        """
        Saving a model without a registered search index schedules no deferred
        flush.
        """
        with transaction.atomic():
            # CachedValue itself has no search indexer.
            CachedValue.objects.create(
                object_type=ContentType.objects.get_for_model(Site),
                object_id=1,
                field='name',
                type='str',
                value='test',
                weight=100,
            )
            self.assertEqual(self._scheduled_flush_aliases(), [])

    def test_flush_enqueues_job_when_worker_available(self):
        """
        When an RQ worker is available, a committed batch is merged into the
        shared Redis buffer and a single drain is scheduled, rather than indexing
        inline. The originating database alias is carried on the scheduled job so
        the deferred write targets the originating schema (e.g. a branch schema
        under netbox-branching).
        """
        site_ct = ContentType.objects.get_for_model(Site)

        # Patching the worker-availability probe is the established pattern for
        # worker-gated behavior (cf. extras/tests/test_views.py, test_api.py).
        with mock.patch('netbox.search.deferred.any_workers_for_queue', return_value=True):
            with mock.patch.object(SearchCacheJob, 'enqueue') as enqueue:
                with self.captureOnCommitCallbacks(execute=True):
                    site = Site.objects.create(name='Enqueued', slug='enqueued')

        enqueue.assert_called_once()
        self.assertEqual(enqueue.call_args.kwargs['using'], DEFAULT_DB_ALIAS)
        # The object was buffered for a later drain rather than enqueued inline.
        buffered = deferred._connection().hgetall(deferred._pending_key(DEFAULT_DB_ALIAS))
        self.assertIn(f'{site_ct.pk}:{site.pk}', {k.decode() for k in buffered})

    def test_flush_falls_back_inline_when_broker_unreachable(self):
        """
        If the broker is unreachable (the worker-availability probe raises a
        RedisError), the flush must not propagate the error; it falls back to
        inline indexing, which is a PostgreSQL write with no Redis dependency.
        """
        content_type = ContentType.objects.get_for_model(Site)

        with mock.patch(
            'netbox.search.deferred.any_workers_for_queue',
            side_effect=RedisConnectionError("broker down"),
        ):
            with self.captureOnCommitCallbacks(execute=True):
                site = Site.objects.create(
                    name='Broker Down',
                    slug='broker-down',
                    facility='Golf',
                    description='Indexed inline despite broker outage',
                    physical_address='3 Test Way',
                    shipping_address='3 Test Way',
                    comments='Lorem ipsum',
                )

        # The object was indexed inline (no exception propagated, rows written).
        self.assertEqual(
            CachedValue.objects.filter(object_type=content_type, object_id=site.pk).count(),
            len(SiteIndex.fields)
        )

    def test_flush_falls_back_inline_when_enqueue_fails(self):
        """
        A worker can die (or the broker can drop) between the availability probe
        and the enqueue. The flush guards the whole dispatch, not just the probe:
        if enqueue raises a RedisError it still falls back to inline indexing.
        """
        content_type = ContentType.objects.get_for_model(Site)

        with mock.patch('netbox.search.deferred.any_workers_for_queue', return_value=True):
            with mock.patch.object(
                SearchCacheJob, 'enqueue', side_effect=RedisConnectionError("broker dropped")
            ):
                with self.captureOnCommitCallbacks(execute=True):
                    site = Site.objects.create(
                        name='Enqueue Failed',
                        slug='enqueue-failed',
                        facility='Hotel',
                        description='Indexed inline after enqueue failure',
                        physical_address='4 Test Way',
                        shipping_address='4 Test Way',
                        comments='Lorem ipsum',
                    )

        self.assertEqual(
            CachedValue.objects.filter(object_type=content_type, object_id=site.pk).count(),
            len(SiteIndex.fields)
        )
        # The scheduling lock is released so recovery can proceed promptly.
        self.assertFalse(
            deferred._connection().exists(deferred._lock_key(DEFAULT_DB_ALIAS))
        )

    def test_cache_update_skips_deleted_object(self):
        """
        _apply_deferred_updates tolerates a pk that no longer exists (object
        deleted between enqueue and execution): it must not error or create cache
        rows.
        """
        site = Site.objects.create(name='Vanished', slug='vanished')
        site_ct = ContentType.objects.get_for_model(Site)
        pk = site.pk
        site.delete()
        CachedValue.objects.filter(object_type=site_ct, object_id=pk).delete()

        # No exception, and no rows resurrected for the missing object.
        search_backend._apply_deferred_updates(using=None, cache_groups={site_ct.pk: [pk]}, remove_groups={})
        self.assertFalse(
            CachedValue.objects.filter(object_type=site_ct, object_id=pk).exists()
        )

    def test_remove_groups_skips_missing_cache_table(self):
        """
        Regression test for the per-iteration transaction.atomic() in the remove_groups loop:
        without a savepoint to roll back to, a tolerated failure on the first group's DELETE
        leaves the connection's transaction aborted, and a second group's DELETE in the same call
        then dies with 25P02 (in_failed_sql_transaction) -- a SQLSTATE in neither tolerated set --
        instead of being tolerated like the first. Two remove_groups entries are required to
        observe this: a single entry never reaches a second DELETE to fail.
        """
        table = CachedValue._meta.db_table
        with connection.cursor() as cursor:
            cursor.execute('SET CONSTRAINTS ALL IMMEDIATE')
            cursor.execute(f'ALTER TABLE {table} RENAME TO {table}_missing')

        # Neither group's object type/pk needs to correspond to a real object: _remove_by_id()
        # only uses them to filter CachedValue, which is what no longer exists here.
        search_backend._apply_deferred_updates(
            using=None, cache_groups={}, remove_groups={1: [1], 2: [2]},
        )

    def test_cache_update_skips_dropped_column(self):
        """
        _apply_deferred_updates tolerates the model being indexed having lost a column the ORM
        still expects (e.g. a plugin's dynamically-generated model whose field was renamed or
        removed within an unmerged branch since the update was enqueued): it must not error, and
        a cache entry already written by an earlier, successful index must survive untouched.
        The read of the model being indexed happens before any write to CachedValue, so a
        tolerated failure there means the removal and re-insert are never even attempted for
        this object -- that ordering, not a rollback, is what leaves the earlier entry
        untouched, and is the property actually worth protecting here, not just "no exception"
        (netboxlabs/netbox-custom-objects#651; netbox-community/netbox#22909).

        Manufacturer (rather than Site, used elsewhere in this file) is used here because it
        carries no denormalization triggers of its own -- but every FK constraint Django creates
        on PostgreSQL is DEFERRABLE INITIALLY DEFERRED by default, so this test's own INSERT
        (via its object_type FK) leaves a pending RI trigger event within the same transaction;
        Postgres refuses to ALTER TABLE until that settles, hence the explicit SET CONSTRAINTS
        below.
        """
        manufacturer = Manufacturer.objects.create(
            name='Column Dropped', slug='column-dropped', description='doomed',
        )
        manufacturer_ct = ContentType.objects.get_for_model(Manufacturer)
        pk = manufacturer.pk

        # Seed a real, successful index entry -- the thing that must survive intact below.
        search_backend.cache(manufacturer)
        cached_before = set(
            CachedValue.objects.filter(object_type=manufacturer_ct, object_id=pk)
            .values_list('field', 'value')
        )
        self.assertTrue(cached_before, 'setup failed to index the object at all')

        column = Manufacturer._meta.get_field('description').column
        with connection.cursor() as cursor:
            cursor.execute('SET CONSTRAINTS ALL IMMEDIATE')
            cursor.execute(f'ALTER TABLE {Manufacturer._meta.db_table} DROP COLUMN {column}')

        # No exception, and the prior index entry is left exactly as it was: a tolerated failure
        # must not wipe out previously-good data.
        search_backend._apply_deferred_updates(
            using=None, cache_groups={manufacturer_ct.pk: [pk]}, remove_groups={},
        )
        cached_after = set(
            CachedValue.objects.filter(object_type=manufacturer_ct, object_id=pk)
            .values_list('field', 'value')
        )
        self.assertEqual(cached_before, cached_after)

    def test_cache_update_propagates_unrelated_database_error(self):
        """
        The tolerance added for a stale target column (test_cache_update_skips_dropped_column) is
        scoped to reading the model being indexed. A DatabaseError raised while writing to this
        backend's own CachedValue table -- e.g. an undefined_column there too, which would
        indicate a genuine defect (such as code deployed against a database that has not yet
        been migrated) rather than a plugin's branch-diverged schema -- must still propagate
        rather than being swallowed by the widened tolerance.
        """
        manufacturer = Manufacturer.objects.create(name='Propagates', slug='propagates')
        manufacturer_ct = ContentType.objects.get_for_model(Manufacturer)

        column = CachedValue._meta.get_field('weight').column
        with connection.cursor() as cursor:
            cursor.execute('SET CONSTRAINTS ALL IMMEDIATE')
            cursor.execute(f'ALTER TABLE {CachedValue._meta.db_table} DROP COLUMN {column}')

        # Pin down that this specifically is the write to CachedValue failing, not some
        # unrelated ProgrammingError -- otherwise a future change that broke the read side
        # instead could still satisfy this assertion.
        with self.assertRaises(ProgrammingError) as ctx:
            search_backend._apply_deferred_updates(
                using=None,
                cache_groups={manufacturer_ct.pk: [manufacturer.pk]},
                remove_groups={},
            )
        self.assertIn(column, str(ctx.exception))


class SearchCacheCoalescingTestCase(RQQueueTestMixin, TestCase):
    """
    Tests for the cross-transaction coalescing buffer in netbox.search.deferred.

    These use the real tasks Redis connection (DB 0), so the RENAME/lock/lease
    primitives are exercised for real rather than mocked. RQQueueTestMixin
    flushes that database around each test and serializes this class against the
    other Redis-backed suites; otherwise a parallel worker's flush would wipe the
    coalescing keys mid-test.
    """

    @staticmethod
    def _create_site(slug='coalesce'):
        # Create the object, then discard any inline-indexed rows so tests start
        # from a known-empty cache for it. Populate every indexed field so the
        # expected CachedValue count is len(SiteIndex.fields).
        site = Site.objects.create(
            name=slug, slug=slug, facility='Alpha', description='desc',
            physical_address='1 Test Way', shipping_address='1 Test Way',
            comments='Lorem ipsum',
        )
        ct = ContentType.objects.get_for_model(Site)
        CachedValue.objects.filter(object_type=ct, object_id=site.pk).delete()
        return ct, site.pk

    def _buffer(self, batch):
        with mock.patch('netbox.search.deferred.any_workers_for_queue', return_value=True):
            with mock.patch.object(SearchCacheJob, 'enqueue'):
                deferred._flush(batch, DEFAULT_DB_ALIAS)

    def test_many_committed_transactions_coalesce_into_one_job(self):
        """
        Regression guard for #23259: many separate committed transactions must
        coalesce into a single scheduled job, not one job per transaction.
        """
        ct, pk = self._create_site()

        with mock.patch('netbox.search.deferred.any_workers_for_queue', return_value=True):
            with mock.patch.object(SearchCacheJob, 'enqueue') as enqueue:
                for i in range(25):
                    deferred._flush({(ct.pk, pk + i): deferred.OP_CACHE}, DEFAULT_DB_ALIAS)

        enqueue.assert_called_once()
        buffered = deferred._connection().hgetall(deferred._pending_key(DEFAULT_DB_ALIAS))
        self.assertEqual(len(buffered), 25)

    def test_later_op_wins_in_buffer(self):
        ct, pk = self._create_site()
        self._buffer({(ct.pk, pk): deferred.OP_CACHE})
        self._buffer({(ct.pk, pk): deferred.OP_REMOVE})
        buffered = deferred._connection().hgetall(deferred._pending_key(DEFAULT_DB_ALIAS))
        self.assertEqual(buffered[f'{ct.pk}:{pk}'.encode()], b'remove')

    def test_drain_applies_and_clears_buffer(self):
        ct, pk = self._create_site()
        self._buffer({(ct.pk, pk): deferred.OP_CACHE})
        deferred.drain_and_apply(DEFAULT_DB_ALIAS)
        self.assertEqual(
            CachedValue.objects.filter(object_type=ct, object_id=pk).count(),
            len(SiteIndex.fields),
        )
        conn = deferred._connection()
        self.assertFalse(conn.exists(deferred._pending_key(DEFAULT_DB_ALIAS)))
        self.assertEqual(list(conn.scan_iter(match=f'{deferred.STAGING_PREFIX}*')), [])

    def test_drain_removes_and_clears(self):
        ct, pk = self._create_site()
        search_backend.cache(Site.objects.get(pk=pk))
        self.assertTrue(CachedValue.objects.filter(object_type=ct, object_id=pk).exists())
        self._buffer({(ct.pk, pk): deferred.OP_REMOVE})
        deferred.drain_and_apply(DEFAULT_DB_ALIAS)
        self.assertFalse(CachedValue.objects.filter(object_type=ct, object_id=pk).exists())

    def test_second_claim_returns_none(self):
        ct, pk = self._create_site()
        conn = deferred._connection()
        conn.hset(deferred._pending_key(DEFAULT_DB_ALIAS), mapping={f'{ct.pk}:{pk}': 'cache'})
        self.assertIsNotNone(deferred._claim(DEFAULT_DB_ALIAS))
        self.assertIsNone(deferred._claim(DEFAULT_DB_ALIAS))

    def test_update_arriving_during_drain_is_rescheduled(self):
        ct, pk = self._create_site()
        conn = deferred._connection()
        conn.hset(deferred._pending_key(DEFAULT_DB_ALIAS), mapping={f'{ct.pk}:{pk}': 'cache'})

        def apply_and_arrive(*args, **kwargs):
            # Simulate a commit landing while the claimed batch is being applied.
            conn.hset(deferred._pending_key(DEFAULT_DB_ALIAS), mapping={f'{ct.pk}:{pk}': 'remove'})

        with mock.patch.object(search_backend, '_apply_deferred_updates', side_effect=apply_and_arrive):
            with mock.patch.object(SearchCacheJob, 'enqueue') as enqueue:
                deferred.drain_and_apply(DEFAULT_DB_ALIAS)

        enqueue.assert_called_once()
        self.assertTrue(conn.exists(deferred._pending_key(DEFAULT_DB_ALIAS)))

    def test_stranded_staging_is_recovered(self):
        ct, pk = self._create_site()
        conn = deferred._connection()
        staging = f'{deferred.STAGING_PREFIX}{DEFAULT_DB_ALIAS}:{int(time.time())}:deadbeef'
        conn.hset(staging, mapping={f'{ct.pk}:{pk}': 'cache'})

        deferred.drain_stranded()

        self.assertEqual(
            CachedValue.objects.filter(object_type=ct, object_id=pk).count(),
            len(SiteIndex.fields),
        )
        self.assertFalse(conn.exists(staging))

    def test_failed_apply_retains_staging_and_retry_converges(self):
        ct, pk = self._create_site()
        conn = deferred._connection()
        staging = f'{deferred.STAGING_PREFIX}{DEFAULT_DB_ALIAS}:{int(time.time())}:cafe'
        conn.hset(staging, mapping={f'{ct.pk}:{pk}': 'cache'})

        with mock.patch.object(
            search_backend, '_apply_deferred_updates', side_effect=ProgrammingError('boom')
        ):
            deferred.drain_stranded()

        # The only copy is retained on failure, never discarded.
        self.assertTrue(conn.exists(staging))

        # Simulate lease expiry, then retry for real: the retry converges.
        for raw_key in conn.scan_iter(match=f'{deferred.LEASE_PREFIX}*'):
            conn.delete(raw_key)
        deferred.drain_stranded()

        self.assertEqual(
            CachedValue.objects.filter(object_type=ct, object_id=pk).count(),
            len(SiteIndex.fields),
        )
        self.assertFalse(conn.exists(staging))

    def test_advisory_lock_contention_skips_apply(self):
        """
        If another applier holds the advisory lock (its Redis lease may have
        expired while it is still running), a second applier must not apply the
        same batch concurrently -- that is the #23259 duplicate-row path.
        """
        ct, pk = self._create_site()
        conn = deferred._connection()
        staging = f'{deferred.STAGING_PREFIX}{DEFAULT_DB_ALIAS}:{int(time.time())}:1ease'
        conn.hset(staging, mapping={f'{ct.pk}:{pk}': 'cache'})
        batch_id = staging.rsplit(':', 1)[1]

        with mock.patch('netbox.search.deferred.advisory_lock') as advisory:
            advisory.return_value.__enter__.return_value = False
            with mock.patch.object(search_backend, '_apply_deferred_updates') as apply:
                deferred._apply_staging(DEFAULT_DB_ALIAS, staging, deferred.logger)
                apply.assert_not_called()

        # The batch is retained for the current lock holder (or the safety net),
        # and contention is not counted as an apply failure.
        self.assertTrue(conn.exists(staging))
        self.assertFalse(conn.exists(deferred._attempts_key(batch_id)))

    def test_repeated_apply_failure_is_capped_and_batch_dropped(self):
        """
        A batch that keeps failing is retained below the cap, then dropped at the
        cap with an error-level log instead of blocking indexing of unrelated
        objects forever.
        """
        ct, pk = self._create_site()
        conn = deferred._connection()
        staging = f'{deferred.STAGING_PREFIX}{DEFAULT_DB_ALIAS}:{int(time.time())}:cafe2'
        conn.hset(staging, mapping={f'{ct.pk}:{pk}': 'cache'})
        batch_id = staging.rsplit(':', 1)[1]

        with mock.patch.object(
            search_backend, '_apply_deferred_updates', side_effect=ProgrammingError('boom')
        ):
            with self.assertLogs('netbox.search.deferred', level='ERROR') as logs:
                for _ in range(deferred.MAX_APPLY_ATTEMPTS - 1):
                    # Simulate the lease expiring between safety-net passes.
                    conn.delete(deferred._lease_key(batch_id))
                    with self.assertRaises(ProgrammingError):
                        deferred._apply_staging(DEFAULT_DB_ALIAS, staging, deferred.logger)
                    self.assertTrue(conn.exists(staging))

                conn.delete(deferred._lease_key(batch_id))
                deferred._apply_staging(DEFAULT_DB_ALIAS, staging, deferred.logger)

        self.assertFalse(conn.exists(staging))
        self.assertFalse(conn.exists(deferred._attempts_key(batch_id)))
        self.assertTrue(any('dropping deferred batch' in m for m in logs.output))

    def test_successful_apply_clears_failure_counter(self):
        ct, pk = self._create_site()
        conn = deferred._connection()
        staging = f'{deferred.STAGING_PREFIX}{DEFAULT_DB_ALIAS}:{int(time.time())}:f00d'
        conn.hset(staging, mapping={f'{ct.pk}:{pk}': 'cache'})
        batch_id = staging.rsplit(':', 1)[1]
        conn.set(deferred._attempts_key(batch_id), 3)

        deferred._apply_staging(DEFAULT_DB_ALIAS, staging, deferred.logger)

        self.assertFalse(conn.exists(staging))
        self.assertFalse(conn.exists(deferred._attempts_key(batch_id)))

    def test_lease_prevents_concurrent_apply(self):
        ct, pk = self._create_site()
        conn = deferred._connection()
        staging = f'{deferred.STAGING_PREFIX}{DEFAULT_DB_ALIAS}:{int(time.time())}:feed'
        conn.hset(staging, mapping={f'{ct.pk}:{pk}': 'cache'})
        conn.set(deferred._lease_key('feed'), '1', nx=True, ex=60)

        with mock.patch.object(search_backend, '_apply_deferred_updates') as apply:
            deferred._apply_staging(DEFAULT_DB_ALIAS, staging, deferred.logger)
            apply.assert_not_called()

        self.assertTrue(conn.exists(staging))

    def test_expired_lease_allows_takeover(self):
        ct, pk = self._create_site()
        conn = deferred._connection()
        staging = f'{deferred.STAGING_PREFIX}{DEFAULT_DB_ALIAS}:{int(time.time())}:beef'
        conn.hset(staging, mapping={f'{ct.pk}:{pk}': 'cache'})
        # A lease is set then expires before the batch is applied.
        conn.set(deferred._lease_key('beef'), '1', nx=True, ex=60)
        conn.delete(deferred._lease_key('beef'))

        deferred._apply_staging(DEFAULT_DB_ALIAS, staging, deferred.logger)

        self.assertEqual(
            CachedValue.objects.filter(object_type=ct, object_id=pk).count(),
            len(SiteIndex.fields),
        )
        self.assertFalse(conn.exists(staging))

    def test_draining_one_batch_does_not_delete_newer_pending(self):
        ct, pk = self._create_site()
        conn = deferred._connection()
        staging = f'{deferred.STAGING_PREFIX}{DEFAULT_DB_ALIAS}:{int(time.time())}:abcd'
        conn.hset(staging, mapping={f'{ct.pk}:{pk}': 'cache'})
        # A newer commit arrives after the batch was claimed.
        conn.hset(deferred._pending_key(DEFAULT_DB_ALIAS), mapping={f'{ct.pk}:{pk + 1}': 'remove'})

        with mock.patch.object(SearchCacheJob, 'enqueue'):
            deferred._apply_staging(DEFAULT_DB_ALIAS, staging, deferred.logger)

        buffered = conn.hgetall(deferred._pending_key(DEFAULT_DB_ALIAS))
        self.assertIn(f'{ct.pk}:{pk + 1}'.encode(), buffered)
        self.assertFalse(conn.exists(staging))

    def test_safety_net_skips_alias_with_scheduled_drain(self):
        ct, pk = self._create_site()
        conn = deferred._connection()
        conn.hset(deferred._pending_key(DEFAULT_DB_ALIAS), mapping={f'{ct.pk}:{pk}': 'cache'})
        conn.set(deferred._lock_key(DEFAULT_DB_ALIAS), '1', nx=True, ex=60)

        with mock.patch.object(search_backend, '_apply_deferred_updates') as apply:
            deferred.drain_stranded()
            apply.assert_not_called()

        self.assertTrue(conn.exists(deferred._pending_key(DEFAULT_DB_ALIAS)))

    def test_safety_net_noop_when_empty(self):
        with mock.patch.object(search_backend, '_apply_deferred_updates') as apply:
            deferred.drain_stranded()
            apply.assert_not_called()

    def test_legacy_job_arguments_still_apply(self):
        """
        A SearchCacheJob enqueued by a pre-coalescing version carries cache_groups
        / remove_groups directly; it must still be applied (rolling upgrade).
        """
        ct, pk = self._create_site()
        SearchCacheJob.run(
            mock.Mock(),
            using=DEFAULT_DB_ALIAS,
            cache_groups={ct.pk: [pk]},
            remove_groups={},
        )
        self.assertEqual(
            CachedValue.objects.filter(object_type=ct, object_id=pk).count(),
            len(SiteIndex.fields),
        )

    def test_safety_net_job_registered_by_app_ready(self):
        """
        The safety-net job must be registered by CoreConfig.ready() importing
        netbox.search.jobs -- not merely by this test module's own import of that
        module, which would make an in-process assertion vacuous. Boot Django in
        a clean interpreter that never imports netbox.search.jobs explicitly and
        inspect the registry there.
        """
        script = (
            "import django; django.setup();"
            "from netbox.registry import registry;"
            "jobs = [c for c in registry['system_jobs']"
            " if getattr(c, 'name', None) == 'Search cache flush safety net'];"
            "assert len(jobs) == 1, jobs;"
            "assert registry['system_jobs'][jobs[0]]['interval'] == 5, jobs;"
            "print('REGISTERED')"
        )
        env = os.environ.copy()
        env.setdefault('DJANGO_SETTINGS_MODULE', 'netbox.settings')
        env.setdefault('NETBOX_CONFIGURATION', 'netbox.configuration_testing')
        result = subprocess.run(
            [sys.executable, '-c', script],
            cwd=str(settings.BASE_DIR),
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('REGISTERED', result.stdout)


class AutocommitCachingTestCase(TransactionTestCase):
    """
    Tests for the synchronous (autocommit) indexing path. Uses TransactionTestCase
    rather than TestCase so that a save outside an explicit transaction runs in
    autocommit (connection.in_atomic_block is False), exercising mark_for_deferred_indexing's
    inline-indexing branch rather than the deferred on_commit path.
    """

    def test_autocommit_save_indexes_synchronously(self):
        # Saved outside any atomic() block: indexing happens inline, immediately,
        # with no background worker and no on_commit deferral.
        site = Site.objects.create(
            name='Autocommit Site',
            slug='autocommit-site',
            facility='Foxtrot',
            description='Indexed synchronously',
            physical_address='2 Test Way',
            shipping_address='2 Test Way',
            comments='Lorem ipsum',
        )

        content_type = ContentType.objects.get_for_model(Site)
        self.assertEqual(
            CachedValue.objects.filter(object_type=content_type, object_id=site.pk).count(),
            len(SiteIndex.fields)
        )

    def test_autocommit_delete_removes_synchronously(self):
        site = Site.objects.create(name='Autocommit Del', slug='autocommit-del')
        content_type = ContentType.objects.get_for_model(Site)
        # Capture the pk before delete() nulls instance.pk in memory.
        site_pk = site.pk
        self.assertTrue(
            CachedValue.objects.filter(object_type=content_type, object_id=site_pk).exists()
        )

        site.delete()
        self.assertFalse(
            CachedValue.objects.filter(object_type=content_type, object_id=site_pk).exists()
        )

    def test_inner_savepoint_rollback_does_not_leak_into_outer_batch(self):
        """
        Regression test for the nested-atomic leak: an operation performed inside
        an inner atomic() block (savepoint) that rolls back must not affect the
        search cache when the outer transaction commits.

        TransactionTestCase is required so the outer atomic() is a real
        transaction whose on_commit callbacks actually fire on commit (under
        TestCase the test body is already inside a transaction, so nothing
        commits and the leak is invisible).
        """
        content_type = ContentType.objects.get_for_model(Site)

        # Object that exists before the transaction and stays cached: the inner
        # savepoint will (transiently) delete it, then roll back. Capture the pk
        # up front; Model.delete() nulls instance.pk in memory.
        survivor = Site.objects.create(name='Survivor', slug='survivor')
        survivor_pk = survivor.pk
        self.assertTrue(
            CachedValue.objects.filter(object_type=content_type, object_id=survivor_pk).exists()
        )

        with transaction.atomic():
            # Outer write schedules a search-cache flush for this connection.
            outer = self._create_indexed_site('Outer', 'outer')

            # Inner savepoint deletes the survivor, then rolls back. At the DB
            # level the survivor still exists after the rollback.
            try:
                with transaction.atomic():
                    survivor.delete()
                    self.assertFalse(Site.objects.filter(pk=survivor_pk).exists())
                    raise RuntimeError('abort inner savepoint')
            except RuntimeError:
                pass

            # The savepoint rolled back, so the survivor row is still present.
            self.assertTrue(Site.objects.filter(pk=survivor_pk).exists())

        # After the outer transaction commits, the deferred flush runs. The
        # rolled-back inner delete must NOT have removed the survivor from the
        # cache, and the committed outer object must be indexed.
        self.assertTrue(
            CachedValue.objects.filter(object_type=content_type, object_id=survivor_pk).exists(),
            "rolled-back inner-savepoint delete leaked into the outer flush and "
            "removed the survivor from the search cache",
        )
        self.assertEqual(
            CachedValue.objects.filter(object_type=content_type, object_id=outer.pk).count(),
            len(SiteIndex.fields),
        )

    @staticmethod
    def _create_indexed_site(name, slug):
        # SiteIndex.to_cache() emits a row only for non-empty fields, so populate
        # every indexed field to get exactly len(SiteIndex.fields) cache rows.
        return Site.objects.create(
            name=name,
            slug=slug,
            facility='Facility',
            description=f'{name} description',
            physical_address='1 Test Way',
            shipping_address='1 Test Way',
            comments='Lorem ipsum',
        )

    def test_committed_savepoint_indexes_in_its_own_scope(self):
        """
        A nested atomic() that commits is scoped to its own flush callback (one
        per savepoint scope), and both the outer and the inner-committed object
        are indexed. The two-callback count locks in the per-scope behavior so a
        future change that re-merges scopes cannot silently reintroduce the
        nested-rollback leak.
        """
        content_type = ContentType.objects.get_for_model(Site)

        with transaction.atomic():
            outer = self._create_indexed_site('OuterC', 'outer-c')

            with transaction.atomic():
                inner = self._create_indexed_site('InnerC', 'inner-c')

            # Two distinct savepoint scopes dirtied objects, so two flush
            # callbacks are scheduled (one per scope), not one coalesced batch.
            self.assertEqual(len(scheduled_search_flushes()), 2)

        # Both objects are indexed after the outer transaction commits.
        self.assertEqual(
            CachedValue.objects.filter(object_type=content_type, object_id=outer.pk).count(),
            len(SiteIndex.fields),
        )
        self.assertEqual(
            CachedValue.objects.filter(object_type=content_type, object_id=inner.pk).count(),
            len(SiteIndex.fields),
        )

    def test_cross_scope_save_then_delete_nets_to_removed(self):
        """
        Save an object at the transaction top level, then delete it inside a
        committed nested savepoint. The two ops land in separate scopes (no
        cross-scope coalescing), so two flush callbacks run in registration
        (FIFO) order: the cache pass then the removal pass. The re-fetch at flush
        time is the source of truth, so the end state is correctly "removed".
        """
        content_type = ContentType.objects.get_for_model(Site)

        with transaction.atomic():
            site = Site.objects.create(name='CrossScope', slug='cross-scope')
            site_pk = site.pk

            with transaction.atomic():
                site.delete()

        self.assertFalse(
            CachedValue.objects.filter(object_type=content_type, object_id=site_pk).exists(),
            "object deleted in a committed nested savepoint should not remain cached",
        )
        self.assertFalse(Site.objects.filter(pk=site_pk).exists())

    def test_sibling_savepoints_do_not_cross_contaminate(self):
        """
        Two sequential nested savepoints under one outer transaction: the first
        rolls back, the second commits, each dirtying a different object. Only
        the committed sibling's object is indexed; the rolled-back sibling's op
        is discarded with its own callback.
        """
        content_type = ContentType.objects.get_for_model(Site)

        with transaction.atomic():
            try:
                with transaction.atomic():
                    rolled = Site.objects.create(name='SiblingRollback', slug='sibling-rb')
                    rolled_pk = rolled.pk
                    raise RuntimeError('abort first sibling')
            except RuntimeError:
                pass

            with transaction.atomic():
                committed = self._create_indexed_site('SiblingCommit', 'sibling-commit')

        self.assertFalse(
            CachedValue.objects.filter(object_type=content_type, object_id=rolled_pk).exists(),
            "rolled-back sibling savepoint's object should not be indexed",
        )
        self.assertEqual(
            CachedValue.objects.filter(object_type=content_type, object_id=committed.pk).count(),
            len(SiteIndex.fields),
        )

    def test_deep_nesting_middle_rollback(self):
        """
        Three savepoint levels, each dirtying a distinct object; the middle level
        rolls back. The top object and the deepest object nested under the middle
        are both discarded along with the middle savepoint (its rollback prunes
        every callback whose registration snapshot contains the middle sid), so
        only the top-level object survives to be indexed.
        """
        content_type = ContentType.objects.get_for_model(Site)

        with transaction.atomic():
            top = self._create_indexed_site('DeepTop', 'deep-top')

            try:
                with transaction.atomic():  # middle savepoint
                    middle = Site.objects.create(name='DeepMiddle', slug='deep-middle')
                    middle_pk = middle.pk

                    with transaction.atomic():  # deepest savepoint
                        deepest = Site.objects.create(name='DeepDeepest', slug='deep-deepest')
                        deepest_pk = deepest.pk

                    raise RuntimeError('abort middle')
            except RuntimeError:
                pass

        # Only the top-level object survived; the middle savepoint's rollback
        # discarded both the middle and the deepest object's flush callbacks.
        self.assertEqual(
            CachedValue.objects.filter(object_type=content_type, object_id=top.pk).count(),
            len(SiteIndex.fields),
        )
        self.assertFalse(
            CachedValue.objects.filter(object_type=content_type, object_id=middle_pk).exists()
        )
        self.assertFalse(
            CachedValue.objects.filter(object_type=content_type, object_id=deepest_pk).exists()
        )


class _MinimalSearchBackend(SearchBackend):
    """
    A backend implementing only the documented contract (search/cache/remove/clear), with no
    knowledge of deferral. Records cache()/remove() calls in memory so a test can assert it indexed
    synchronously. Used to prove a custom SEARCH_BACKEND keeps working after this change.
    """

    def __init__(self):
        self.cached = []
        self.removed = []

    def search(self, value, user=None, object_types=None, lookup=None):
        return []

    def cache(self, instances, indexer=None, remove_existing=True):
        if not hasattr(instances, '__iter__'):
            instances = [instances]
        self.cached.extend(instances)

    def remove(self, instance):
        self.removed.append(instance)

    def clear(self, object_types=None):
        self.cached.clear()
        self.removed.clear()


class CustomBackendContractTestCase(TransactionTestCase):
    """
    Proves the deferred-indexing work did not change the public SearchBackend contract: a custom
    backend implementing only search/cache/remove/clear still indexes synchronously through the base
    signal handlers, and never schedules deferred (on_commit) work. Deferral is private to
    CachedValueSearchBackend; it must not leak onto a backend that didn't opt into it.
    """

    def test_custom_backend_indexes_synchronously(self):
        backend = _MinimalSearchBackend()

        # Connect the custom backend's (inherited, synchronous) handlers, exactly as
        # netbox.search.signals connects the configured backend from CoreConfig.ready(). Same
        # call site, no type-check.
        post_save.connect(backend.caching_handler, sender=Site)
        post_delete.connect(backend.removal_handler, sender=Site)
        self.addCleanup(post_save.disconnect, backend.caching_handler, sender=Site)
        self.addCleanup(post_delete.disconnect, backend.removal_handler, sender=Site)

        # A backend implementing only the documented contract indexes through the base handlers
        # inline (the handler calls self.cache()/self.remove() synchronously). It is never routed
        # into the deferral machinery, which is private to CachedValueSearchBackend.
        site = Site.objects.create(name='Custom Backend', slug='custom-backend')
        self.assertIn(site, backend.cached)

        site.delete()
        self.assertEqual(len(backend.removed), 1)

    def test_default_backend_defers_via_same_call_path(self):
        # The default backend (CachedValueSearchBackend) IS connected via netbox.search.signals, and
        # reaches the SAME caching_handler call path -- but its override defers instead of indexing
        # inline. This contrasts with the custom backend above: identical dispatch, polymorphic
        # behavior.
        with transaction.atomic():
            Site.objects.create(name='Default Defers', slug='default-defers')
            scheduled = scheduled_search_flushes()
            self.assertEqual(len(scheduled), 1)
