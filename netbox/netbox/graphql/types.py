import strawberry
import strawberry_django
from django.contrib.contenttypes.models import ContentType
from django.db.models import ExpressionWrapper, F, Func, IntegerField, Value
from strawberry.types import Info

from core.graphql.mixins import ChangelogMixin
from core.models import ObjectType as ObjectType_
from extras.graphql.mixins import CustomFieldsMixin, JournalEntriesMixin, TagsMixin
from netbox.graphql.utils import register_model_graphql_type
from users.graphql.mixins import OwnerMixin

__all__ = (
    'BaseObjectType',
    'ContentTypeType',
    'LtreeNodeMixin',
    'NestedGroupObjectType',
    'NestedLtreeGroupObjectType',
    'NetBoxObjectType',
    'ObjectType',
    'OrganizationalObjectType',
    'PrimaryObjectType',
    'register_type',
)


def register_type(model, **kwargs):
    """
    Drop-in replacement for `strawberry_django.type()` for model-bound NetBox GraphQL output types. Before delegating
    to `strawberry_django.type()`, any plugin-registered output-type mixins for the given model are spliced into the
    decorated class's bases. With no extensions registered this is an exact pass-through, leaving schema output
    unchanged. See `register_model_graphql_type` for the registry-timing contract.
    """
    return register_model_graphql_type(model, strawberry_django.type, 'graphql_type_extensions', **kwargs)


#
# Base types
#

@strawberry.type
class BaseObjectType:
    """
    Base GraphQL object type for all NetBox objects. Restricts the model queryset to enforce object permissions.
    """

    @classmethod
    def get_queryset(cls, queryset, info: Info, **kwargs):
        # Enforce object permissions on the queryset
        if hasattr(queryset, 'restrict'):
            return queryset.restrict(info.context.request.user, 'view')
        return queryset

    @strawberry_django.field
    def display(self) -> str:
        return str(self)

    @strawberry_django.field
    def class_type(self) -> str:
        return self.__class__.__name__


class ObjectType(
    ChangelogMixin,
    BaseObjectType
):
    """
    Base GraphQL object type for unclassified models which support change logging
    """
    pass


class PrimaryObjectType(
    ChangelogMixin,
    CustomFieldsMixin,
    JournalEntriesMixin,
    TagsMixin,
    OwnerMixin,
    BaseObjectType
):
    """
    Base GraphQL type for models which inherit from PrimaryModel.
    """
    pass


class OrganizationalObjectType(
    ChangelogMixin,
    CustomFieldsMixin,
    JournalEntriesMixin,
    TagsMixin,
    OwnerMixin,
    BaseObjectType
):
    """
    Base GraphQL type for models which inherit from OrganizationalModel.
    """
    pass


@strawberry.type
class LtreeNodeMixin:
    """
    Exposes the ltree-backed tree depth as a `level` field, preserving the `level`
    field MPTT-based types previously surfaced automatically as a real column.

    The depth is computed in the database as `nlevel(path) - 1` (root = 0) and
    annotated onto the queryset. We prefer the annotation over the `path` column,
    which is excluded from the schema. When a resolution path does not apply the
    annotation (e.g. a nested relation), `ltree_level` is absent; fall back to the
    loaded `path` string (the same depth the LtreeModel.level property computes)
    so the field never raises AttributeError.
    """
    @strawberry_django.field(annotate={
        'ltree_level': ExpressionWrapper(
            Func(F('path'), function='nlevel', output_field=IntegerField()) - Value(1),
            output_field=IntegerField(),
        )
    })
    def level(self) -> int:
        ltree_level = getattr(self, 'ltree_level', None)
        if ltree_level is not None:
            return ltree_level
        path = getattr(self, 'path', '') or ''
        return str(path).count('.')


class NestedGroupObjectType(
    ChangelogMixin,
    CustomFieldsMixin,
    JournalEntriesMixin,
    TagsMixin,
    OwnerMixin,
    BaseObjectType
):
    """
    Base GraphQL type for the deprecated MPTT-backed NestedGroupModel, kept for
    plugin compatibility. MPTT exposes `level` as a real column, so no annotation
    mixin is needed. New code should use NestedLtreeGroupObjectType.
    """
    pass


class NestedLtreeGroupObjectType(
    LtreeNodeMixin,
    ChangelogMixin,
    CustomFieldsMixin,
    JournalEntriesMixin,
    TagsMixin,
    OwnerMixin,
    BaseObjectType
):
    """
    Base GraphQL type for models which inherit from NestedLtreeGroupModel.
    Adds a `level` field annotated via `nlevel(path)`.
    """
    pass


class NetBoxObjectType(
    ChangelogMixin,
    CustomFieldsMixin,
    JournalEntriesMixin,
    TagsMixin,
    BaseObjectType
):
    pass


#
# Miscellaneous types
#

@register_type(
    ContentType,
    fields=['id', 'app_label', 'model'],
    pagination=True
)
class ContentTypeType:
    pass


@register_type(
    ObjectType_,
    fields=['id', 'app_label', 'model'],
    pagination=True
)
class ObjectTypeType:
    pass
