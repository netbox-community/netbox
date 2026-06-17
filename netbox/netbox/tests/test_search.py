from unittest import mock

from django.contrib.contenttypes.models import ContentType
from django.db import connection, transaction
from django.test import TestCase, TransactionTestCase

from dcim.models import Site
from dcim.search import SiteIndex
from extras.models import CachedValue
from netbox.search import deferred
from netbox.search.backends import search_backend


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

    @staticmethod
    def _scheduled_flushes():
        # Django stores each registered callback as a (savepoint_ids, func, robust)
        # tuple in connection.run_on_commit; return the search flush callbacks.
        return [
            entry[1] for entry in connection.run_on_commit
            if hasattr(entry[1], deferred._FLUSH_ALIAS_ATTR)
        ]

    def _scheduled_flush_aliases(self):
        return [getattr(func, deferred._FLUSH_ALIAS_ATTR) for func in self._scheduled_flushes()]

    def _pending_batch(self):
        for func in self._scheduled_flushes():
            return getattr(func, deferred._FLUSH_BATCH_ATTR)
        return None

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

    def test_save_then_delete_coalesces_to_removal(self):
        """
        Creating then deleting an object within one transaction coalesces to a
        single removal; the object ends up absent from the cache.
        """
        site_ct = ContentType.objects.get_for_model(Site)
        with self.captureOnCommitCallbacks(execute=True):
            site = Site.objects.create(name='Ephemeral', slug='ephemeral')
            pk = site.pk
            site.delete()
            # The coalesced op for this object is a removal, not a cache.
            batch = self._pending_batch()
            self.assertEqual(batch[(site_ct.pk, pk)], deferred.OP_REMOVE)

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
        from django.db import DEFAULT_DB_ALIAS

        from netbox.search.tasks import SearchCacheJob

        site_ct = ContentType.objects.get_for_model(Site)

        # Patching the worker-availability probe is the established pattern for
        # worker-gated behavior (cf. extras/tests/test_views.py, test_api.py).
        with mock.patch('utilities.rqworker.any_workers_for_queue', return_value=True):
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

    def test_cache_update_skips_deleted_object(self):
        """
        update_search_cache tolerates a pk that no longer exists (object deleted
        between enqueue and execution): it must not error or create cache rows.
        """
        from netbox.search.tasks import update_search_cache

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
    autocommit (connection.in_atomic_block is False), exercising mark_dirty's
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
