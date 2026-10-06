from django.db import DEFAULT_DB_ALIAS, connection, connections
from django.http import QueryDict
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext

from dcim.models import Region, Site
from utilities.data import deepmerge
from utilities.query import dict_to_filter_params, find_nonempty
from utilities.querydict import normalize_querydict


class DictToFilterParamsTestCase(TestCase):
    """
    Validate the operation of dict_to_filter_params().
    """
    def test_dict_to_filter_params(self):

        input = {
            'a': True,
            'foo': {
                'bar': 123,
                'baz': 456,
            },
            'x': {
                'y': {
                    'z': False
                }
            }
        }

        output = {
            'a': True,
            'foo__bar': 123,
            'foo__baz': 456,
            'x__y__z': False,
        }

        self.assertEqual(dict_to_filter_params(input), output)

        input['x']['y']['z'] = True

        self.assertNotEqual(dict_to_filter_params(input), output)


class RegionReplicaRouter:
    """
    Route Region reads to the "replica" database alias.
    """
    def db_for_read(self, model, **hints):
        return 'replica' if model is Region else None


class FindNonEmptyTestCase(TestCase):
    """
    Validate the operation of find_nonempty().
    """
    @classmethod
    def setUpTestData(cls):
        Site.objects.create(name='Site 1', slug='site-1')

    def test_returns_positions_of_matching_querysets(self):
        """Every matching queryset is reported by its own position."""
        querysets = [
            Site.objects.filter(name='Nonexistent'),
            Site.objects.all(),
            Region.objects.filter(name='Nonexistent'),
            Site.objects.filter(name='Site 1'),
        ]

        self.assertEqual(find_nonempty(querysets), {1, 3})

    def test_uses_a_single_query(self):
        """All candidates are probed by one combined query limited to one row per candidate."""
        querysets = [
            Site.objects.filter(name='Nonexistent'),
            Site.objects.all(),
            Region.objects.filter(name='Nonexistent'),
        ]

        with CaptureQueriesContext(connection) as queries:
            find_nonempty(querysets)

        self.assertEqual(len(queries.captured_queries), 1)
        self.assertEqual(queries.captured_queries[0]['sql'].count('LIMIT 1'), len(querysets))

    def test_empty_input_issues_no_query(self):
        """An empty candidate list is resolved without a query."""
        with CaptureQueriesContext(connection) as queries:
            result = find_nonempty([])

        self.assertEqual(result, set())
        self.assertEqual(len(queries.captured_queries), 0)

    def test_none_candidates_issue_no_query(self):
        """Candidates which are all none() are resolved without a query."""
        with CaptureQueriesContext(connection) as queries:
            result = find_nonempty([Site.objects.none(), Region.objects.none()])

        self.assertEqual(result, set())
        self.assertEqual(len(queries.captured_queries), 0)

    def test_none_candidates_do_not_shift_positions(self):
        """A none() candidate is skipped without renumbering the candidates after it."""
        self.assertEqual(find_nonempty([Site.objects.none(), Site.objects.all()]), {1})

    def test_distinct_candidate_is_probed(self):
        """A distinct() candidate joining another table is matched like any other."""
        querysets = [
            Region.objects.filter(name='Nonexistent'),
            Site.objects.filter(asns__isnull=True).distinct(),
        ]

        self.assertEqual(find_nonempty(querysets), {1})

    def test_unsatisfiable_candidate_does_not_hide_matches(self):
        """A candidate whose filter can never match does not hide the matches of the others."""
        querysets = [
            Site.objects.filter(pk__in=[]),
            Site.objects.all(),
            Region.objects.filter(name='Nonexistent'),
        ]

        self.assertEqual(find_nonempty(querysets), {1})

    def test_sliced_and_combined_candidates_keep_their_semantics(self):
        """Sliced and combined candidates are matched by their own slice and set operation."""
        querysets = [
            Site.objects.filter(name='Site 1')[1:],
            Site.objects.filter(name='Nonexistent').union(Site.objects.filter(name='Site 1')),
            Region.objects.filter(name='Nonexistent'),
        ]

        self.assertEqual(find_nonempty(querysets), {1})

    def test_candidates_are_batched_per_database(self):
        """Candidates routed to different databases are never combined into one query."""
        connections['replica'] = connections[DEFAULT_DB_ALIAS]
        self.addCleanup(connections.__delitem__, 'replica')
        querysets = [
            Site.objects.filter(name='Nonexistent'),
            Site.objects.all(),
            Region.objects.filter(name='Nonexistent'),
        ]

        with override_settings(DATABASE_ROUTERS=[RegionReplicaRouter()]):
            with CaptureQueriesContext(connection) as queries:
                result = find_nonempty(querysets)

        self.assertEqual(result, {1})
        self.assertEqual(len(queries.captured_queries), 2)


class NormalizeQueryDictTestCase(TestCase):
    """
    Validate normalize_querydict() utility function.
    """
    def test_normalize_querydict(self):
        self.assertDictEqual(
            normalize_querydict(QueryDict('foo=1&bar=2&bar=3&baz=')),
            {'foo': '1', 'bar': ['2', '3'], 'baz': ''}
        )


class DeepMergeTestCase(TestCase):
    """
    Validate the behavior of the deepmerge() utility.
    """
    def test_deepmerge(self):

        dict1 = {
            'active': True,
            'foo': 123,
            'fruits': {
                'orange': 1,
                'apple': 2,
                'pear': 3,
            },
            'vegetables': None,
            'dairy': {
                'milk': 1,
                'cheese': 2,
            },
            'deepnesting': {
                'foo': {
                    'a': 10,
                    'b': 20,
                    'c': 30,
                },
            },
        }

        dict2 = {
            'active': False,
            'bar': 456,
            'fruits': {
                'banana': 4,
                'grape': 5,
            },
            'vegetables': {
                'celery': 1,
                'carrots': 2,
                'corn': 3,
            },
            'dairy': None,
            'deepnesting': {
                'foo': {
                    'a': 100,
                    'd': 40,
                },
            },
        }

        merged = {
            'active': False,
            'foo': 123,
            'bar': 456,
            'fruits': {
                'orange': 1,
                'apple': 2,
                'pear': 3,
                'banana': 4,
                'grape': 5,
            },
            'vegetables': {
                'celery': 1,
                'carrots': 2,
                'corn': 3,
            },
            'dairy': None,
            'deepnesting': {
                'foo': {
                    'a': 100,
                    'b': 20,
                    'c': 30,
                    'd': 40,
                },
            },
        }

        self.assertEqual(
            deepmerge(dict1, dict2),
            merged
        )
