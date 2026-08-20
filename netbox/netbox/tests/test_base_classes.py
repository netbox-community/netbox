from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.test import TestCase
from django.utils.module_loading import import_string

from netbox.api.serializers import (
    NestedGroupModelSerializer,
    NetBoxModelSerializer,
    OrganizationalModelSerializer,
    PrimaryModelSerializer,
)
from netbox.filtersets import (
    NestedGroupModelFilterSet,
    NetBoxModelFilterSet,
    OrganizationalModelFilterSet,
    PrimaryModelFilterSet,
)
from netbox.forms.bulk_edit import (
    NestedGroupModelBulkEditForm,
    NetBoxModelBulkEditForm,
    OrganizationalModelBulkEditForm,
    PrimaryModelBulkEditForm,
)
from netbox.forms.bulk_import import (
    NestedGroupModelImportForm,
    NetBoxModelImportForm,
    OrganizationalModelImportForm,
    PrimaryModelImportForm,
)
from netbox.forms.filtersets import (
    NestedGroupModelFilterSetForm,
    NetBoxModelFilterSetForm,
    OrganizationalModelFilterSetForm,
    PrimaryModelFilterSetForm,
)
from netbox.forms.model_forms import (
    NestedGroupModelForm,
    NetBoxModelForm,
    OrganizationalModelForm,
    PrimaryModelForm,
)
from netbox.graphql.types import (
    NestedGroupObjectType,
    NetBoxObjectType,
    OrganizationalObjectType,
    PrimaryObjectType,
)
from netbox.models import NestedGroupModel, NetBoxModel, OrganizationalModel, PrimaryModel
from netbox.registry import registry
from netbox.tables import (
    NestedGroupModelTable,
    NetBoxTable,
    OrganizationalModelTable,
    PrimaryModelTable,
)
from utilities.testing import TableTestCases


class FormClassesTestCase(TestCase):

    @staticmethod
    def get_form_for_model(model, prefix=''):
        """
        Import and return the form class for a given model.
        """
        app_label = model._meta.app_label
        model_name = model.__name__
        return import_string(f'{app_label}.forms.{model_name}{prefix}Form')

    @staticmethod
    def get_model_form_base_class(model):
        """
        Return the base form class for creating/editing the given model.
        """
        if model._meta.app_label == 'dummy_plugin':
            return None
        if issubclass(model, PrimaryModel):
            return PrimaryModelForm
        if issubclass(model, OrganizationalModel):
            return OrganizationalModelForm
        if issubclass(model, NestedGroupModel):
            return NestedGroupModelForm
        if issubclass(model, NetBoxModel):
            return NetBoxModelForm
        return None

    @staticmethod
    def get_bulk_edit_form_base_class(model):
        """
        Return the base form class for bulk editing the given model.
        """
        if model._meta.app_label == 'dummy_plugin':
            return None
        if issubclass(model, PrimaryModel):
            return PrimaryModelBulkEditForm
        if issubclass(model, OrganizationalModel):
            return OrganizationalModelBulkEditForm
        if issubclass(model, NestedGroupModel):
            return NestedGroupModelBulkEditForm
        if issubclass(model, NetBoxModel):
            return NetBoxModelBulkEditForm
        return None

    @staticmethod
    def get_import_form_base_class(model):
        """
        Return the base form class for importing the given model.
        """
        if model._meta.app_label == 'dummy_plugin':
            return None
        if issubclass(model, PrimaryModel):
            return PrimaryModelImportForm
        if issubclass(model, OrganizationalModel):
            return OrganizationalModelImportForm
        if issubclass(model, NestedGroupModel):
            return NestedGroupModelImportForm
        if issubclass(model, NetBoxModel):
            return NetBoxModelImportForm
        return None

    @staticmethod
    def get_filterset_form_base_class(model):
        """
        Return the base form class for the given model's FilterSet.
        """
        if model._meta.app_label == 'dummy_plugin':
            return None
        if issubclass(model, PrimaryModel):
            return PrimaryModelFilterSetForm
        if issubclass(model, OrganizationalModel):
            return OrganizationalModelFilterSetForm
        if issubclass(model, NestedGroupModel):
            return NestedGroupModelFilterSetForm
        if issubclass(model, NetBoxModel):
            return NetBoxModelFilterSetForm
        return None

    @classmethod
    def get_bulk_edit_form_for_model(cls, model):
        """
        Return the bulk edit form class for a given model, or None if it has none.
        """
        try:
            return cls.get_form_for_model(model, prefix='BulkEdit')
        except ImportError:
            return None

    def test_model_form_base_classes(self):
        """
        Check that each model form inherits from the appropriate base class.
        """
        for model in apps.get_models():
            if base_class := self.get_model_form_base_class(model):
                form_class = self.get_form_for_model(model)
                self.assertTrue(issubclass(form_class, base_class), f"{form_class} does not inherit from {base_class}")

    def test_bulk_edit_form_base_classes(self):
        """
        Check that each bulk edit form inherits from the appropriate base class.
        """
        for model in apps.get_models():
            if base_class := self.get_bulk_edit_form_base_class(model):
                form_class = self.get_form_for_model(model, prefix='BulkEdit')
                self.assertTrue(issubclass(form_class, base_class), f"{form_class} does not inherit from {base_class}")

    def test_bulk_edit_nullable_fields(self):
        """
        Check that every name in a bulk edit form's nullable_fields is a field on the form, and that no
        name is listed twice. A name with no matching field is inert: neither the rendered form nor the
        update handler acts on it.
        """
        for model in apps.get_models():
            if (form_class := self.get_bulk_edit_form_for_model(model)) is None:
                continue
            # Read the class attribute, which excludes the fields added per instance at runtime
            declared = tuple(form_class.nullable_fields)
            for name in declared:
                self.assertIn(
                    name,
                    form_class.base_fields,
                    f"{form_class.__name__}.nullable_fields lists '{name}', which is not a field on the form",
                )
                # The update handler reads model_field.null when nullifying, so a form-only field crashes
                try:
                    model._meta.get_field(name)
                except FieldDoesNotExist:
                    self.fail(
                        f"{form_class.__name__}.nullable_fields lists '{name}', "
                        f"which is not a field on {model.__name__}"
                    )
            duplicates = sorted({name for name in declared if declared.count(name) > 1})
            self.assertEqual(
                duplicates,
                [],
                f"{form_class.__name__}.nullable_fields lists duplicate entries: {duplicates}",
            )

    def test_bulk_edit_hardcoded_nullable_fields(self):
        """
        Check that forms which declare fieldsets mark their owner and comments fields as nullable. The
        bulk edit template renders a Set Null control for both outside the declared fieldsets, so a form
        which omits them offers a control that does nothing.
        """
        for model in apps.get_models():
            if (form_class := self.get_bulk_edit_form_for_model(model)) is None:
                continue
            if not getattr(form_class, 'fieldsets', None):
                continue
            # Instantiate so that fields added per instance by _extend_nullable_fields() are included
            form = form_class({'pk': []}, initial={})
            declared_in_fieldsets = {
                item for fieldset in form_class.fieldsets for item in fieldset.items
            }
            for name in ('owner', 'comments'):
                if name not in form.fields:
                    continue
                self.assertIn(
                    name,
                    form.nullable_fields,
                    f"{form_class.__name__} renders a Set Null control for '{name}' without marking it nullable",
                )
                self.assertNotIn(
                    name,
                    declared_in_fieldsets,
                    f"{form_class.__name__} lists '{name}' in a fieldset, which renders the field twice",
                )

    def test_import_form_base_classes(self):
        """
        Check that each bulk import form inherits from the appropriate base class.
        """
        for model in apps.get_models():
            if base_class := self.get_import_form_base_class(model):
                form_class = self.get_form_for_model(model, prefix='Import')
                self.assertTrue(issubclass(form_class, base_class), f"{form_class} does not inherit from {base_class}")

    def test_filterset_form_base_classes(self):
        """
        Check that each filterset form inherits from the appropriate base class.
        """
        for model in apps.get_models():
            if base_class := self.get_filterset_form_base_class(model):
                form_class = self.get_form_for_model(model, prefix='Filter')
                self.assertTrue(issubclass(form_class, base_class), f"{form_class} does not inherit from {base_class}")


class FilterSetClassesTestCase(TestCase):

    @staticmethod
    def get_filterset_for_model(model):
        """
        Return the filterset class for a given model from the application registry.
        """
        label = f'{model._meta.app_label}.{model._meta.model_name}'
        return registry['filtersets'].get(label)

    @staticmethod
    def get_model_filterset_base_class(model):
        """
        Return the base FilterSet class for the given model.
        """
        if model._meta.app_label == 'dummy_plugin':
            return None
        if issubclass(model, PrimaryModel):
            return PrimaryModelFilterSet
        if issubclass(model, OrganizationalModel):
            return OrganizationalModelFilterSet
        if issubclass(model, NestedGroupModel):
            return NestedGroupModelFilterSet
        if issubclass(model, NetBoxModel):
            return NetBoxModelFilterSet
        return None

    def test_model_filterset_base_classes(self):
        """
        Check that each FilterSet inherits from the appropriate base class.
        """
        for model in apps.get_models():
            if base_class := self.get_model_filterset_base_class(model):
                filterset = self.get_filterset_for_model(model)
                self.assertIsNotNone(filterset, f"No registered filterset found for model {model}")
                self.assertTrue(
                    issubclass(filterset, base_class),
                    f"{filterset} does not inherit from {base_class}",
                )


class TableClassesTestCase(TestCase):

    @staticmethod
    def get_table_for_model(model):
        """
        Import and return the table class for a given model.
        """
        app_label = model._meta.app_label
        model_name = model.__name__
        return import_string(f'{app_label}.tables.{model_name}Table')

    @staticmethod
    def get_table_test_for_model(model):
        """
        Import and return the table test class for a given model.
        """
        app_label = model._meta.app_label
        model_name = model.__name__
        return import_string(f'{app_label}.tests.test_tables.{model_name}TableTestCase')

    @staticmethod
    def get_model_table_base_class(model):
        """
        Return the base table class for the given model.
        """
        if model._meta.app_label == 'dummy_plugin':
            return None
        if issubclass(model, PrimaryModel):
            return PrimaryModelTable
        if issubclass(model, OrganizationalModel):
            return OrganizationalModelTable
        if issubclass(model, NestedGroupModel):
            return NestedGroupModelTable
        if issubclass(model, NetBoxModel):
            return NetBoxTable
        return None

    def test_model_table_base_classes(self):
        """
        Check that each table inherits from the appropriate base class.
        """
        for model in apps.get_models():
            if base_class := self.get_model_table_base_class(model):
                table = self.get_table_for_model(model)
                self.assertTrue(
                    issubclass(table, base_class),
                    f"{table} does not inherit from {base_class}",
                )
                self.assertTrue(
                    issubclass(table.Meta, base_class.Meta),
                    f"{table}.Meta does not inherit from {base_class}.Meta",
                )

    def test_model_table_test_classes(self):
        """
        Check that each model-backed table has a standard table test case.
        """
        for model in apps.get_models():
            if self.get_model_table_base_class(model) is None:
                continue

            with self.subTest(model=model.__name__):
                app_label = model._meta.app_label
                model_name = model.__name__
                try:
                    table = self.get_table_for_model(model)
                except ImportError:
                    self.fail(
                        f"No table class found for {model_name} "
                        f"(expected {app_label}.tables.{model_name}Table)"
                    )
                try:
                    table_test = self.get_table_test_for_model(model)
                except ImportError:
                    self.fail(
                        f"No table test case found for {model_name} "
                        f"(expected {app_label}.tests.test_tables.{model_name}TableTestCase)"
                    )

                self.assertTrue(
                    issubclass(table_test, TableTestCases.StandardTableTestCase),
                    f"{table_test} does not inherit from {TableTestCases.StandardTableTestCase}",
                )
                self.assertIs(
                    table_test.table,
                    table,
                    f"{table_test}.table is not set to {table}",
                )


class SerializerClassesTestCase(TestCase):

    @staticmethod
    def get_serializer_for_model(model):
        """
        Import and return the REST API serializer class for a given model.
        """
        app_label = model._meta.app_label
        model_name = model.__name__
        return import_string(f'{app_label}.api.serializers.{model_name}Serializer')

    @staticmethod
    def get_model_serializer_base_class(model):
        """
        Return the base serializer class for the given model.
        """
        if model._meta.app_label == 'dummy_plugin':
            return None
        if issubclass(model, PrimaryModel):
            return PrimaryModelSerializer
        if issubclass(model, OrganizationalModel):
            return OrganizationalModelSerializer
        if issubclass(model, NestedGroupModel):
            return NestedGroupModelSerializer
        if issubclass(model, NetBoxModel):
            return NetBoxModelSerializer
        return None

    def test_model_serializer_base_classes(self):
        """
        Check that each model serializer inherits from the appropriate base class.
        """
        for model in apps.get_models():
            if base_class := self.get_model_serializer_base_class(model):
                serializer = self.get_serializer_for_model(model)
                self.assertTrue(
                    issubclass(serializer, base_class),
                    f"{serializer} does not inherit from {base_class}",
                )


class GraphQLTypeClassesTestCase(TestCase):

    @staticmethod
    def get_type_for_model(model):
        """
        Import and return the GraphQL type for a given model.
        """
        app_label = model._meta.app_label
        model_name = model.__name__
        return import_string(f'{app_label}.graphql.types.{model_name}Type')

    @staticmethod
    def get_model_type_base_class(model):
        """
        Return the base GraphQL type for the given model.
        """
        if model._meta.app_label == 'dummy_plugin':
            return None
        if issubclass(model, PrimaryModel):
            return PrimaryObjectType
        if issubclass(model, OrganizationalModel):
            return OrganizationalObjectType
        if issubclass(model, NestedGroupModel):
            return NestedGroupObjectType
        if issubclass(model, NetBoxModel):
            return NetBoxObjectType
        return None

    def test_model_type_base_classes(self):
        """
        Check that each GraphQL type inherits from the appropriate base class.
        """
        for model in apps.get_models():
            if base_class := self.get_model_type_base_class(model):
                graphql_type = self.get_type_for_model(model)
                self.assertTrue(
                    issubclass(graphql_type, base_class),
                    f"{graphql_type} does not inherit from {base_class}",
                )
