from django.db import connection
from django.db.models import Count, F, IntegerField, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext

from extras.models import Tag
from utilities.querysets import chunked_update


class ChunkedUpdateTestCase(TestCase):
    """
    Tests for the chunked_update() helper, which performs a bulk UPDATE optionally split into
    batches bounded by the BULK_UPDATE_CHUNK_SIZE configuration parameter.
    """
    @classmethod
    def setUpTestData(cls):
        Tag.objects.bulk_create([
            Tag(name=f'Tag {i}', slug=f'tag-{i}', weight=i)
            for i in range(1, 6)  # Five tags, weights 1..5
        ])

    @staticmethod
    def _count_updates(queries):
        return len([q for q in queries if q['sql'].strip().upper().startswith('UPDATE')])

    @override_settings(BULK_UPDATE_CHUNK_SIZE=None)
    def test_update_without_chunk_size(self):
        """
        With BULK_UPDATE_CHUNK_SIZE set to None, a single unbounded UPDATE is issued.
        """
        with CaptureQueriesContext(connection) as queries:
            count = chunked_update(Tag.objects.all(), weight=100)

        self.assertEqual(count, 5)
        self.assertEqual(self._count_updates(queries.captured_queries), 1)
        self.assertEqual(Tag.objects.filter(weight=100).count(), 5)

    @override_settings(BULK_UPDATE_CHUNK_SIZE=2)
    def test_update_with_chunk_size(self):
        """
        With BULK_UPDATE_CHUNK_SIZE set, the update is split into batches; every row is updated
        exactly once and the total count is returned.
        """
        with CaptureQueriesContext(connection) as queries:
            count = chunked_update(Tag.objects.all(), weight=100)

        self.assertEqual(count, 5)
        # Five rows in batches of two → three UPDATE statements
        self.assertEqual(self._count_updates(queries.captured_queries), 3)
        self.assertEqual(Tag.objects.filter(weight=100).count(), 5)

    def test_explicit_chunk_size_argument(self):
        """
        An explicit chunk_size argument takes precedence over the configuration parameter.
        """
        with CaptureQueriesContext(connection) as queries:
            count = chunked_update(Tag.objects.all(), chunk_size=2, weight=100)

        self.assertEqual(count, 5)
        self.assertEqual(self._count_updates(queries.captured_queries), 3)
        self.assertEqual(Tag.objects.filter(weight=100).count(), 5)

    @override_settings(BULK_UPDATE_CHUNK_SIZE=2)
    def test_f_expression_applied_once_per_row(self):
        """
        An F() expression referencing the row's own column is applied exactly once per row, even
        when the update is chunked (chunks are disjoint by primary key).
        """
        original = {tag.pk: tag.weight for tag in Tag.objects.all()}

        count = chunked_update(Tag.objects.all(), weight=F('weight') + 1)

        self.assertEqual(count, 5)
        for tag in Tag.objects.all():
            self.assertEqual(tag.weight, original[tag.pk] + 1)

    @override_settings(BULK_UPDATE_CHUNK_SIZE=2)
    def test_correlated_subquery(self):
        """
        A correlated subquery (OuterRef) resolves against each chunk's queryset, mirroring the
        counter-rebuild pattern in utilities.counters.update_counts().
        """
        # Set each tag's weight to the number of tags sharing its slug (always 1), proving the
        # OuterRef binds correctly per-row across chunks.
        subquery = Subquery(
            Tag.objects.filter(slug=OuterRef('slug')).values('slug')
            .annotate(c=Count('pk')).values('c'),
            output_field=IntegerField()
        )
        count = chunked_update(Tag.objects.all(), chunk_size=2, weight=Coalesce(subquery, 0))

        self.assertEqual(count, 5)
        self.assertEqual(Tag.objects.filter(weight=1).count(), 5)

    @override_settings(BULK_UPDATE_CHUNK_SIZE=2)
    def test_filtered_queryset(self):
        """
        Only rows matching the queryset's filter are updated when chunking.
        """
        target_pks = list(Tag.objects.filter(weight__lte=3).values_list('pk', flat=True))

        count = chunked_update(Tag.objects.filter(weight__lte=3), weight=0)

        self.assertEqual(count, len(target_pks))
        self.assertEqual(Tag.objects.filter(weight=0).count(), len(target_pks))
        # Rows outside the filter are untouched (weights 4 and 5 remain)
        self.assertEqual(Tag.objects.filter(weight__gt=3).count(), 2)

    @override_settings(BULK_UPDATE_CHUNK_SIZE=2)
    def test_empty_queryset(self):
        """
        Updating an empty queryset is a no-op that returns zero.
        """
        count = chunked_update(Tag.objects.filter(name='nonexistent'), weight=0)
        self.assertEqual(count, 0)
