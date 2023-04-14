import functools

from django.core.exceptions import FieldDoesNotExist
from django.db.models import ForeignKey
from django.db.models.constants import LOOKUP_SEP
from django.db.models.fields.reverse_related import ManyToOneRel
from graphene import InputObjectType
from graphene.types.generic import GenericScalar
from graphene.types.resolver import default_resolver
from graphene_django import DjangoObjectType
from graphql import GraphQLResolveInfo, GraphQLSchema
from graphql.execution.execute import get_field_def
from graphql.language.ast import FragmentSpreadNode, InlineFragmentNode, VariableNode
from graphql.pyutils import Path
from graphql.type.definition import GraphQLInterfaceType, GraphQLUnionType

__all__ = (
    'gql_query_optimizer',
)


def gql_query_optimizer(queryset, info, **options):
    return QueryOptimizer(info).optimize(queryset)


class QueryOptimizer(object):
    def __init__(self, info, **options):
        self.root_info = info

    def optimize(self, queryset):
        info = self.root_info
        field_def = get_field_def(info.schema, info.parent_type, info.field_nodes[0])

        field_names = self._optimize_gql_selections(
            self._get_type(field_def),
            info.field_nodes[0],
        )

        qs = queryset.prefetch_related(*field_names)
        return qs

    def _get_type(self, field_def):
        a_type = field_def.type
        while hasattr(a_type, "of_type"):
            a_type = a_type.of_type
        return a_type

    def _get_graphql_schema(self, schema):
        if isinstance(schema, GraphQLSchema):
            return schema
        else:
            return schema.graphql_schema

    def _get_possible_types(self, graphql_type):
        if isinstance(graphql_type, (GraphQLInterfaceType, GraphQLUnionType)):
            graphql_schema = self._get_graphql_schema(self.root_info.schema)
            return graphql_schema.get_possible_types(graphql_type)
        else:
            return (graphql_type,)

    def _get_base_model(self, graphql_types):
        models = tuple(t.graphene_type._meta.model for t in graphql_types)
        for model in models:
            if all(issubclass(m, model) for m in models):
                return model
        return None

    def handle_inline_fragment(self, selection, schema, possible_types, field_names):
        fragment_type_name = selection.type_condition.name.value
        graphql_schema = self._get_graphql_schema(schema)
        fragment_type = graphql_schema.get_type(fragment_type_name)
        fragment_possible_types = self._get_possible_types(fragment_type)
        for fragment_possible_type in fragment_possible_types:
            fragment_model = fragment_possible_type.graphene_type._meta.model
            parent_model = self._get_base_model(possible_types)
            if not parent_model:
                continue
            path_from_parent = fragment_model._meta.get_path_from_parent(parent_model)
            select_related_name = LOOKUP_SEP.join(p.join_field.name for p in path_from_parent)
            if not select_related_name:
                continue
            sub_field_names = self._optimize_gql_selections(
                fragment_possible_type,
                selection,
            )
            field_names.append(select_related_name)
        return

    def handle_fragment_spread(self, field_names, name, field_type):
        fragment = self.root_info.fragments[name]
        sub_field_names = self._optimize_gql_selections(
            field_type,
            fragment,
        )

    def _optimize_gql_selections(self, field_type, field_ast):
        field_names = []
        selection_set = field_ast.selection_set
        if not selection_set:
            return field_names
        optimized_fields_by_model = {}
        schema = self.root_info.schema
        graphql_schema = self._get_graphql_schema(schema)
        graphql_type = graphql_schema.get_type(field_type.name)

        possible_types = self._get_possible_types(graphql_type)
        for selection in selection_set.selections:
            if isinstance(selection, InlineFragmentNode):
                self.handle_inline_fragment(selection, schema, possible_types, field_names)
            else:
                name = selection.name.value
                if isinstance(selection, FragmentSpreadNode):
                    self.handle_fragment_spread(field_names, name, field_type)
                else:
                    for possible_type in possible_types:
                        selection_field_def = possible_type.fields.get(name)
                        if not selection_field_def:
                            continue

                        graphene_type = possible_type.graphene_type
                        model = getattr(graphene_type._meta, "model", None)
                        if model and name not in optimized_fields_by_model:
                            field_model = optimized_fields_by_model[name] = model
                            if field_model == model:
                                self._optimize_field(
                                    field_names,
                                    model,
                                    selection,
                                    selection_field_def,
                                    possible_type,
                                )
        return field_names

    def _get_field_info(self, field_names, model, selection, field_def):
        name = None
        model_field = None
        name = self._get_name_from_resolver(field_def.resolve)
        if not name and callable(field_def.resolve) and not isinstance(field_def.resolve, functools.partial):
            name = selection.name.value
        if name:
            model_field = self._get_model_field_from_name(model, name)

        return (name, model_field)

    def _optimize_field(self, field_names, model, selection, field_def, parent_type):
        name, model_field = self._get_field_info(field_names, model, selection, field_def)
        if model_field:
            self._optimize_field_by_name(field_names, model, selection, field_def, name, model_field)

        return

    def _optimize_field_by_name(self, field_names, model, selection, field_def, name, model_field):
        if model_field.many_to_one or model_field.one_to_one:
            sub_field_names = self._optimize_gql_selections(
                self._get_type(field_def),
                selection,
            )
            if name not in field_names:
                field_names.append(name)

            for field in sub_field_names:
                prefetch_key = f"{name}__{field}"
                if prefetch_key not in field_names:
                    field_names.append(prefetch_key)

        if model_field.one_to_many or model_field.many_to_many:
            sub_field_names = self._optimize_gql_selections(
                self._get_type(field_def),
                selection,
            )

            if isinstance(model_field, ManyToOneRel):
                sub_field_names.append(model_field.field.name)

            field_names.append(name)
            for field in sub_field_names:
                prefetch_key = f"{name}__{field}"
                if prefetch_key not in field_names:
                    field_names.append(prefetch_key)

        return

    def _get_optimization_hints(self, resolver):
        return getattr(resolver, "optimization_hints", None)

    def _get_value(self, info, value):
        if isinstance(value, VariableNode):
            var_name = value.name.value
            value = info.variable_values.get(var_name)
            return value
        elif isinstance(value, InputObjectType):
            return value.__dict__
        else:
            return GenericScalar.parse_literal(value)

    def _get_name_from_resolver(self, resolver):
        optimization_hints = self._get_optimization_hints(resolver)
        if optimization_hints:
            name_fn = optimization_hints.model_field
            if name_fn:
                return name_fn()
        if self._is_resolver_for_id_field(resolver):
            return "id"
        elif isinstance(resolver, functools.partial):
            resolver_fn = resolver
            if resolver_fn.func != default_resolver:
                # Some resolvers have the partial function as the second
                # argument.
                for arg in resolver_fn.args:
                    if isinstance(arg, (str, functools.partial)):
                        break
                else:
                    # No suitable instances found, default to first arg
                    arg = resolver_fn.args[0]
                resolver_fn = arg
            if isinstance(resolver_fn, functools.partial) and resolver_fn.func == default_resolver:
                return resolver_fn.args[0]
            if self._is_resolver_for_id_field(resolver_fn):
                return "id"
            return resolver_fn

    def _is_resolver_for_id_field(self, resolver):
        resolve_id = DjangoObjectType.resolve_id
        return resolver == resolve_id

    def _get_model_field_from_name(self, model, name):
        try:
            return model._meta.get_field(name)
        except FieldDoesNotExist:
            descriptor = model.__dict__.get(name)
            if not descriptor:
                return None
            return getattr(descriptor, "rel", None) or getattr(descriptor, "related", None)  # Django < 1.9

    def _is_foreign_key_id(self, model_field, name):
        return isinstance(model_field, ForeignKey) and model_field.name != name and model_field.get_attname() == name

    def _create_resolve_info(self, field_name, field_asts, return_type, parent_type):
        return GraphQLResolveInfo(
            field_name,
            field_asts,
            return_type,
            parent_type,
            Path(None, 0, None),
            schema=self.root_info.schema,
            fragments=self.root_info.fragments,
            root_value=self.root_info.root_value,
            operation=self.root_info.operation,
            variable_values=self.root_info.variable_values,
            context=self.root_info.context,
            is_awaitable=self.root_info.is_awaitable,
        )
