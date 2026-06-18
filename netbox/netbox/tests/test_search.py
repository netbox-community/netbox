from unittest import mock

from django.contrib.contenttypes.models import ContentType
from django.db import DEFAULT_DB_ALIAS, connection, transaction
from django.test import TestCase, TransactionTestCase
from redis.exceptions import ConnectionError as RedisConnectionError

from dcim.models import Site
from dcim.search import SiteIndex
from extras.models import CachedValue
from netbox.search import deferred
from netbox.search.backends import search_backend
from netbox.search.tasks import SearchCacheJob, update_search_cache


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
        site = Site.objects.first()

        with self.captureOnCommitCallbacks(execute=True):
            site.delete()

        content_type = ContentType.objects.get_for_model(Site)
        self.assertFalse(
            CachedValue.objects.filter(object_type=content_type, object_id=site.pk).exists()
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


class DeferredCachingTestCase(TestCase):
    """
    Tests for the deferred (post-commit) search caching machinery in
    netbox.search.deferred.

    With no RQ worker registered, deferral falls back to synchronous indexing on
    commit, so these tests assert on real CachedValue state and on the real
    per-transaction buffer (connection.run_on_commit) rather than mocking the
    queue.
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
        When an RQ worker is available, the flush enqueues a SearchCacheJob
        carrying the dirty objects (and the originating database alias) rather
        than indexing inline.
        """
        site_ct = ContentType.objects.get_for_model(Site)

        # Patching the worker-availability probe is the established pattern for
        # worker-gated behavior (cf. extras/tests/test_views.py, test_api.py).
        with mock.patch('netbox.search.deferred.any_workers_for_queue', return_value=True):
            with mock.patch.object(SearchCacheJob, 'enqueue') as enqueue:
                with self.captureOnCommitCallbacks(execute=True):
                    site = Site.objects.create(name='Enqueued', slug='enqueued')

        enqueue.assert_called_once()
        kwargs = enqueue.call_args.kwargs
        self.assertEqual(kwargs['cache_groups'], {site_ct.pk: [site.pk]})
        self.assertEqual(kwargs['remove_groups'], {})
        # The database alias captured from the post_save signal is forwarded to
        # the job verbatim. This is what lets a deferred write target the
        # originating schema (e.g. a branch schema under netbox-branching) even
        # though the worker has no active routing context; cross-schema routing
        # itself is covered by the netbox-branching test suite.
        self.assertEqual(kwargs['using'], DEFAULT_DB_ALIAS)

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

    def test_cache_update_skips_deleted_object(self):
        """
        update_search_cache tolerates a pk that no longer exists (object deleted
        between enqueue and execution): it must not error or create cache rows.
        """
        site = Site.objects.create(name='Vanished', slug='vanished')
        site_ct = ContentType.objects.get_for_model(Site)
        pk = site.pk
        site.delete()
        CachedValue.objects.filter(object_type=site_ct, object_id=pk).delete()

        # No exception, and no rows resurrected for the missing object.
        update_search_cache(using=None, cache_groups={site_ct.pk: [pk]}, remove_groups={})
        self.assertFalse(
            CachedValue.objects.filter(object_type=site_ct, object_id=pk).exists()
        )


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
        self.assertTrue(
            CachedValue.objects.filter(object_type=content_type, object_id=site.pk).exists()
        )

        site.delete()
        self.assertFalse(
            CachedValue.objects.filter(object_type=content_type, object_id=site.pk).exists()
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
