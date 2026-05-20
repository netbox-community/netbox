import inspect
from importlib import import_module
from importlib.util import find_spec
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.urls import NoReverseMatch

from core.filtersets import ObjectTypeFilterSet
from core.models import ObjectType
from netbox.registry import registry
from utilities.testing import APITestCase, BaseFilterSetTests, ModelViewTestCase
from utilities.views import get_action_url


def intentional(reason):
    return f'Intentional non-standard model coverage: {reason}'


EXEMPTIONS = {
    'api': {
        'core.objectchange': intentional(
            'Read-only audit log; changelog behavior is primarily tested through '
            'parent objects rather than standalone CRUD-style model tests.'
        ),
        'extras.script': intentional(
            'Database-backed script definitions expose bespoke run/admin behavior rather than standard CRUD semantics.'
        ),
    },
    'views': {
        'core.objectchange': intentional(
            'Read-only audit log; changelog behavior is tested through parent object '
            'views rather than a standalone ModelViewTestCase.'
        ),
        'core.configrevision': intentional('Read-only configuration audit/history model, not a standard CRUD viewset.'),
        'extras.script': intentional(
            'Database-backed script definitions use bespoke script admin/run views '
            'rather than the standard CRUD view pattern.'
        ),
    },
    'filtersets': {
        'core.configrevision': intentional(
            'Read-only configuration audit/history model, not standard filterset test coverage.'
        ),
        'extras.script': intentional(
            'Database-backed script definitions use bespoke behavior rather than standard model filtering workflows.'
        ),
    },
}


def model_label(model):
    return f'{model._meta.app_label}.{model._meta.model_name}'


def import_optional(module_name):
    """
    Import an optional submodule if it exists.

    Returns None when the module (or its parent package) cannot be located.
    Import errors raised from inside an existing module are propagated so
    that real bugs do not get silently swallowed.
    """
    try:
        spec = find_spec(module_name)
    except ModuleNotFoundError as err:
        if module_name == err.name or module_name.startswith(f'{err.name}.'):
            return None
        raise

    if spec is None:
        return None

    return import_module(module_name)


def has_tests(cls):
    return any(name.startswith('test_') and callable(getattr(cls, name)) for name in dir(cls))


def get_queryset_model(cls):
    queryset = getattr(cls, 'queryset', None)
    if queryset is not None:
        return queryset.model

    filterset = getattr(cls, 'filterset', None)
    if filterset is not None:
        return filterset._meta.model

    return None


class ModelTestCoverageTestCase(TestCase):
    def get_public_models(self):
        models = []

        for object_type in ObjectType.objects.public().order_by('app_label', 'model'):
            if object_type.is_plugin_model:
                continue

            model = object_type.model_class()
            if model is not None:
                models.append(model)

        return models

    def get_app_labels(self, models):
        return sorted({model._meta.app_label for model in models})

    def collect_covered_models(self, app_labels, module_suffix, base_class, get_model):
        covered = {}

        for app_label in app_labels:
            module = import_optional(f'{app_label}.tests.{module_suffix}')
            if module is None:
                continue

            for _, cls in inspect.getmembers(module, inspect.isclass):
                if cls.__module__ != module.__name__:
                    continue
                if not issubclass(cls, base_class):
                    continue
                if not has_tests(cls):
                    continue

                model = get_model(cls)
                if model is not None:
                    covered.setdefault(model, []).append(f'{cls.__module__}.{cls.__qualname__}')

        return covered

    def has_action_url(self, model, action='list', rest_api=False):
        try:
            get_action_url(model, action=action, rest_api=rest_api)
        except NoReverseMatch:
            return False

        return True

    def format_exemptions(self, category, labels):
        return '\n'.join(f'  - {label}: {EXEMPTIONS[category][label]}' for label in labels)

    def assert_coverage(self, category, expected, covered):
        expected_labels = {model_label(model) for model in expected}
        covered_labels = {model_label(model) for model in covered}
        exempted_labels = set(EXEMPTIONS[category])

        stale_exemptions = sorted(exempted_labels - expected_labels)
        self.assertFalse(
            stale_exemptions,
            f'Remove stale {category} coverage exemptions; these models are '
            f'no longer expected in this category:\n' + self.format_exemptions(category, stale_exemptions),
        )

        covered_exemptions = sorted(exempted_labels & covered_labels)
        self.assertFalse(
            covered_exemptions,
            f'Remove stale {category} coverage exemptions; these models now '
            f'have standard test coverage:\n' + self.format_exemptions(category, covered_exemptions),
        )

        missing = sorted(expected_labels - covered_labels - exempted_labels)
        self.assertFalse(
            missing,
            f'Missing {category} test coverage for:\n' + '\n'.join(f'  - {label}' for label in missing),
        )

    def test_api_test_cases_exist_for_api_models(self):
        models = self.get_public_models()
        app_labels = self.get_app_labels(models)

        expected = {model for model in models if self.has_action_url(model, action='list', rest_api=True)}

        covered = self.collect_covered_models(
            app_labels,
            'test_api',
            APITestCase,
            lambda cls: getattr(cls, 'model', None),
        )

        self.assert_coverage('api', expected, covered)

    def test_view_test_cases_exist_for_ui_models(self):
        models = self.get_public_models()
        app_labels = self.get_app_labels(models)

        expected = {model for model in models if self.has_action_url(model, action='list')}

        covered = self.collect_covered_models(
            app_labels,
            'test_views',
            ModelViewTestCase,
            lambda cls: getattr(cls, 'model', None),
        )

        self.assert_coverage('views', expected, covered)

    def test_filterset_test_cases_exist_for_registered_filtersets(self):
        models = self.get_public_models()
        app_labels = self.get_app_labels(models)

        # Defensive import: app filtersets are normally imported during app/test
        # setup, but loading them here keeps the test self-contained.
        for app_label in app_labels:
            import_optional(f'{app_label}.filtersets')

        expected = {model for model in models if model_label(model) in registry['filtersets']}

        covered = self.collect_covered_models(
            app_labels,
            'test_filtersets',
            BaseFilterSetTests,
            get_queryset_model,
        )

        self.assert_coverage('filtersets', expected, covered)


class HelperFunctionTestCase(TestCase):
    """
    Exercise the helper functions directly so their defensive branches are
    covered even when the main meta-test doesn't trigger them organically.
    """

    def test_import_optional_returns_module_when_present(self):
        module = import_optional('netbox.tests.test_model_test_coverage')
        self.assertIsNotNone(module)
        self.assertEqual(module.__name__, 'netbox.tests.test_model_test_coverage')

    def test_import_optional_returns_none_for_missing_submodule(self):
        # Parent package exists, leaf does not -> find_spec returns None.
        self.assertIsNone(import_optional('netbox.tests.does_not_exist'))

    def test_import_optional_returns_none_for_missing_parent(self):
        # Parent package itself does not exist -> ModuleNotFoundError swallowed.
        self.assertIsNone(import_optional('nonexistent_pkg.tests.test_api'))

    def test_import_optional_propagates_unrelated_find_spec_error(self):
        # find_spec raising ModuleNotFoundError for a different module than the
        # one requested means a parent package itself failed to import; that
        # error must propagate so real bugs aren't silently swallowed.
        with patch(
            'netbox.tests.test_model_test_coverage.find_spec',
            side_effect=ModuleNotFoundError(
                "No module named 'unrelated_dependency'",
                name='unrelated_dependency',
            ),
        ):
            with self.assertRaises(ModuleNotFoundError):
                import_optional('netbox.tests.test_model_test_coverage')

    def test_import_optional_propagates_import_module_errors(self):
        # If find_spec succeeds but import_module raises (e.g. the module
        # exists on disk but a dependency inside it fails to import), the
        # error must propagate rather than being treated as "module missing."
        with (
            patch(
                'netbox.tests.test_model_test_coverage.find_spec',
                return_value=MagicMock(),
            ),
            patch(
                'netbox.tests.test_model_test_coverage.import_module',
                side_effect=ModuleNotFoundError(
                    "No module named 'unrelated_dependency'",
                    name='unrelated_dependency',
                ),
            ),
        ):
            with self.assertRaises(ModuleNotFoundError):
                import_optional('netbox.tests.test_model_test_coverage')

    def test_has_tests_detects_test_methods(self):
        class WithTest:
            def test_thing(self):
                pass

        class WithoutTest:
            def helper(self):
                pass

        self.assertTrue(has_tests(WithTest))
        self.assertFalse(has_tests(WithoutTest))

    def test_get_queryset_model_prefers_queryset(self):
        class Sample:
            queryset = ObjectType.objects.all()

        self.assertEqual(get_queryset_model(Sample), ObjectType)

    def test_get_queryset_model_falls_back_to_filterset(self):
        class Sample:
            filterset = ObjectTypeFilterSet

        self.assertEqual(get_queryset_model(Sample), ObjectType)

    def test_get_queryset_model_returns_none_when_unset(self):
        class Sample:
            pass

        self.assertIsNone(get_queryset_model(Sample))
