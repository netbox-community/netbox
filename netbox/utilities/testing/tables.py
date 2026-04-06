import inspect
from importlib import import_module

from django.test import RequestFactory

from netbox.views import generic

from .base import TestCase

__all__ = (
    "ModelTableTestCase",
    "TableTestCases",
)


class ModelTableTestCase(TestCase):
    """
    Shared helpers for model-backed table ordering smoke tests.

    Concrete subclasses should set `table` and may override `queryset_sources`,
    `queryset_source_view_classes`, or `excluded_orderable_columns` as needed.
    """
    table = None
    excluded_orderable_columns = frozenset({"actions"})

    # Optional explicit override for odd cases
    queryset_sources = None

    # Only these view types are considered sortable queryset sources by default
    queryset_source_view_classes = (generic.ObjectListView,)

    @classmethod
    def validate_table_test_case(cls):
        """
        Assert that the test case is correctly configured with a model-backed table.

        Raises:
            AssertionError: If ``table`` is not set or is not backed by a Django model.
        """
        if cls.table is None:
            raise AssertionError(f"{cls.__name__} must define `table`")
        if getattr(cls.table._meta, "model", None) is None:
            raise AssertionError(f"{cls.__name__}.table must be model-backed")

    def get_request(self):
        """
        Build a minimal ``GET`` request authenticated as the test user.
        """
        request = RequestFactory().get("/")
        request.user = self.user
        return request

    def get_table(self, queryset):
        """
        Instantiate the table class under test with the given *queryset*.
        """
        return self.table(queryset)

    @classmethod
    def is_queryset_source_view(cls, view):
        """
        Return ``True`` if *view* is a list-style view class that declares
        this test case's table and exposes a usable queryset.
        """
        model = cls.table._meta.model
        app_label = model._meta.app_label

        return (
            inspect.isclass(view)
            and view.__module__.startswith(f"{app_label}.views")
            and getattr(view, "table", None) is cls.table
            and getattr(view, "queryset", None) is not None
            and issubclass(view, cls.queryset_source_view_classes)
        )

    @classmethod
    def get_queryset_sources(cls):
        """
        Return iterable of (label, queryset) pairs to test.

        The label is included in the subtest failure output.

        By default, only discover list-style views that declare this table.
        That keeps bulk edit/delete confirmation tables out of the ordering
        smoke test.
        """
        if cls.queryset_sources is not None:
            return tuple(cls.queryset_sources)

        model = cls.table._meta.model
        app_label = model._meta.app_label
        module = import_module(f"{app_label}.views")

        sources = []
        for _, view in inspect.getmembers(module, inspect.isclass):
            if not cls.is_queryset_source_view(view):
                continue

            queryset = view.queryset
            if hasattr(queryset, "all"):
                queryset = queryset.all()

            sources.append((view.__name__, queryset))

        if not sources:
            raise AssertionError(
                f"{cls.__name__} could not find any list-style queryset source for "
                f"{cls.table.__module__}.{cls.table.__name__}; "
                "set `queryset_sources` explicitly if needed."
            )

        return tuple(sources)

    def iter_orderable_columns(self, queryset):
        """
        Yield the names of all orderable columns for *queryset*, excluding
        any listed in ``excluded_orderable_columns``.
        """
        for column in self.get_table(queryset).columns:
            if not column.orderable:
                continue
            if column.name in self.excluded_orderable_columns:
                continue
            yield column.name


class TableTestCases:
    """
    Keep test_* methods nested to avoid unittest auto-discovering the reusable
    base classes directly.
    """

    class StandardTableTestCase(ModelTableTestCase):
        @classmethod
        def setUpClass(cls):
            super().setUpClass()
            cls.validate_table_test_case()

        def test_every_orderable_column_renders(self):
            """
            Verify that each declared ordering can be applied without error.

            This is intentionally a smoke test. It validates ordering against
            the configured queryset sources but does not create model
            instances by default, so it complements rather than replaces
            data-backed rendering tests for tables whose behavior depends on
            populated querysets.
            """
            request = self.get_request()

            for source_name, queryset in self.get_queryset_sources():
                for column_name in self.iter_orderable_columns(queryset):
                    for direction, prefix in (("asc", ""), ("desc", "-")):
                        with self.subTest(source=source_name, column=column_name, direction=direction):
                            table = self.get_table(queryset)
                            table.order_by = f"{prefix}{column_name}"
                            table.as_html(request)
