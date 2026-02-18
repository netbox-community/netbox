from django.apps import apps
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
from netbox.tables import (
    NestedGroupModelTable,
    NetBoxTable,
    OrganizationalModelTable,
    PrimaryModelTable,
)


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
        Import and return the filterset class for a given model.
        """
        app_label = model._meta.app_label
        model_name = model.__name__
        return import_string(f'{app_label}.filtersets.{model_name}FilterSet')

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
