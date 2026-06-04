"""Tests for the GraphQL filter test framework in utilities/testing/api.py."""

import sys
import types
from decimal import Decimal
from typing import Annotated

import strawberry
from django.test import TestCase

from netbox.graphql.filter_lookups import FloatLookup
from utilities.testing.api import APIViewTestCases, GraphQLFilterTest


class GraphQLFilterAnnotationMROTestCase(TestCase):
    """Cover MRO override, import error propagation, lazy annotation resolution, and the zero-auto-test gate."""

    def test_subclass_annotation_overrides_base(self):
        """Subclass annotations win over base in `_iter_filter_class_annotations`."""
        class Base:
            __annotations__ = {'shared': int}

        class Sub(Base):
            __annotations__ = {'shared': str}

        # Stand up a throwaway instance just to access the method as bound.
        instance = APIViewTestCases.GraphQLTestCase()
        pairs = dict(instance._iter_filter_class_annotations(Sub))
        self.assertEqual(pairs['shared'], str)

    def test_get_filter_class_propagates_real_import_errors(self):
        """A broken import inside a model's filters module must surface, not silently return None."""
        broken = types.ModuleType('netbox_broken_filter_fixture.graphql.filters')

        def _raise(*args, **kwargs):
            raise ImportError('simulated downstream breakage')

        broken.__getattr__ = _raise
        # sys.modules mutation is safe under --parallel (separate processes), not threads.
        sys.modules['netbox_broken_filter_fixture'] = types.ModuleType('netbox_broken_filter_fixture')
        sys.modules['netbox_broken_filter_fixture.graphql'] = types.ModuleType(
            'netbox_broken_filter_fixture.graphql'
        )
        sys.modules['netbox_broken_filter_fixture.graphql.filters'] = broken

        try:
            class FakeMeta:
                app_label = 'netbox_broken_filter_fixture'

            class FakeModel:
                _meta = FakeMeta()
                __name__ = 'BrokenModel'

            instance = APIViewTestCases.GraphQLTestCase()
            with self.assertRaises(ImportError):
                instance._get_model_graphql_filter_class(FakeModel)
        finally:
            for key in (
                'netbox_broken_filter_fixture',
                'netbox_broken_filter_fixture.graphql',
                'netbox_broken_filter_fixture.graphql.filters',
            ):
                sys.modules.pop(key, None)

    def test_zero_auto_filter_tests_fails_loudly(self):
        """Helper fails when auto mode is required and no tests of any kind exist."""

        class FakeMeta:
            label = 'fake.FakeModel'

        class FakeModel:
            _meta = FakeMeta()

        class Case(APIViewTestCases.GraphQLTestCase):
            model = FakeModel
            graphql_auto_filter_tests = True
            graphql_auto_filter_required = True

        case = Case()
        with self.assertRaisesRegex(AssertionError, r'No GraphQL filter tests.*fake\.FakeModel'):
            case._assert_graphql_filter_tests_exist([], [], [])

    def test_lazy_annotated_lookup_resolves(self):
        """Annotated['FloatLookup', strawberry.lazy(...)] | None resolves to FloatLookup."""
        annotation = Annotated['FloatLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None
        self.assertIs(
            APIViewTestCases.GraphQLTestCase._unwrap_filter_annotation(annotation),
            FloatLookup,
        )

    def test_str_lookup_emits_all_four_variants(self):
        """`_emit_str_lookup_filter_tests` emits exact, i_contains, i_starts_with, i_ends_with."""
        captured_value = 'production'

        class FakeMeta:
            label = 'fake.FakeModel'
            app_label = 'fake'

        class Case(APIViewTestCases.GraphQLTestCase):
            def _get_model_field_for_filter_field(self, field_name):
                class FakeField:
                    name = field_name
                return FakeField()

            def _get_nonempty_field_value(self, field):
                return captured_value

            def _graphql_literal(self, value):
                return f'"{value}"'

        case = Case()
        tests = list(case._emit_str_lookup_filter_tests('name', None))
        self.assertEqual(
            [t.name for t in tests],
            ['name__exact', 'name__i_contains', 'name__i_starts_with', 'name__i_ends_with'],
        )

    def test_explicit_tests_satisfy_auto_required_gate(self):
        """Helper does NOT fail when explicit tests exist, even if auto/legacy are empty."""

        class FakeMeta:
            label = 'fake.FakeModel'

        class FakeModel:
            _meta = FakeMeta()

        class Case(APIViewTestCases.GraphQLTestCase):
            model = FakeModel
            graphql_auto_filter_tests = True
            graphql_auto_filter_required = True

        case = Case()
        # Should not raise.
        case._assert_graphql_filter_tests_exist(
            auto_tests=[],
            legacy_tests=[],
            explicit_tests=[GraphQLFilterTest(name='x', filters='x: 1')],
        )

    def test_graphql_literal_renders_lists(self):
        """List and tuple values render as GraphQL list literals, not quoted strings."""
        literal = APIViewTestCases.GraphQLTestCase._graphql_literal
        self.assertEqual(literal([1, 2, 3]), '[1, 2, 3]')
        self.assertEqual(literal(('a', 'b')), '["a", "b"]')
        self.assertEqual(literal([]), '[]')

    def test_graphql_literal_renders_decimal_as_number(self):
        """Decimal values render as numeric literals, not quoted strings."""
        literal = APIViewTestCases.GraphQLTestCase._graphql_literal
        self.assertEqual(literal(Decimal('1.23')), '1.23')
        self.assertEqual(literal([Decimal('1.5'), Decimal('2.5')]), '[1.5, 2.5]')

    def test_per_kind_cap_counts_successful_emissions(self):
        """Later candidate fields are tried until per-kind successful emissions reach the cap."""

        class FakeMeta:
            label = 'fake.FakeModel'
            app_label = 'fake'

        class FakeModel:
            _meta = FakeMeta()
            __name__ = 'FakeModel'

        emit_calls = []

        class Case(APIViewTestCases.GraphQLTestCase):
            model = FakeModel
            graphql_auto_filter_fields_per_kind = 2

            def _get_model_graphql_filter_class(self, model=None):
                class FilterClass:
                    __annotations__ = {
                        'empty_field_1': str,
                        'empty_field_2': str,
                        'useful_field_1': str,
                        'useful_field_2': str,
                        'useful_field_3': str,
                    }
                return FilterClass

            def _classify_filter_annotation(self, annotation):
                return 'str_lookup', None

            def _emit_str_lookup_filter_tests(self, field_name, _kind_arg):
                emit_calls.append(field_name)
                if field_name.startswith('empty_'):
                    return iter(())
                return iter((GraphQLFilterTest(name=field_name, filters=f'{field_name}: "x"'),))

        case = Case()
        list(case._iter_auto_graphql_filter_tests())

        # The candidate-counting bug stops at 'empty_field_1' and 'empty_field_2' (the slice
        # captures the first 2). After the fix, the emitter is invoked on all 5 candidates
        # in order until 2 SUCCESSFUL fields have emitted.
        self.assertEqual(
            emit_calls,
            ['empty_field_1', 'empty_field_2', 'useful_field_1', 'useful_field_2'],
        )

    def test_get_filter_class_returns_none_when_parent_module_missing(self):
        """When the parent `<app>.graphql` package is absent, return None instead of re-raising."""

        class FakeMeta:
            app_label = 'netbox_missing_graphql_fixture'

        class FakeModel:
            _meta = FakeMeta()
            __name__ = 'BrokenModel'

        instance = APIViewTestCases.GraphQLTestCase()
        # No `netbox_missing_graphql_fixture` package is registered in sys.modules,
        # so import_module raises ModuleNotFoundError with exc.name == 'netbox_missing_graphql_fixture'
        # (the parent), not the full path 'netbox_missing_graphql_fixture.graphql.filters'.
        # The fix accepts both shapes.
        self.assertIsNone(instance._get_model_graphql_filter_class(FakeModel))

    def test_filter_class_assertion_skipped_with_handwritten_tests(self):
        """Hand-written tests exempt a model from the conventional filter class requirement."""

        class FakeMeta:
            label = 'fake.FakeModel'
            app_label = 'fake'

        class FakeModel:
            _meta = FakeMeta()
            __name__ = 'FakeModel'

        class Case(APIViewTestCases.GraphQLTestCase):
            model = FakeModel

            def _get_model_graphql_filter_class(self, model=None):
                return None

        case = Case()
        # Should not raise despite the missing conventional filter class.
        case._assert_graphql_filter_class_present(
            set(), handwritten_tests=[GraphQLFilterTest(name='x', filters='x: 1')]
        )

    def test_filter_class_assertion_fails_without_filter_class(self):
        """Missing conventional filter class raises when no hand-written tests exist."""

        class FakeMeta:
            label = 'fake.FakeModel'
            app_label = 'fake'

        class FakeModel:
            _meta = FakeMeta()
            __name__ = 'FakeModel'

        class Case(APIViewTestCases.GraphQLTestCase):
            model = FakeModel

            def _get_model_graphql_filter_class(self, model=None):
                return None

        case = Case()
        with self.assertRaisesRegex(AssertionError, r'No GraphQL filter class found for fake\.FakeModel'):
            case._assert_graphql_filter_class_present(set())
