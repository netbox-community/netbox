import strawberry
import strawberry_django
from django.contrib.contenttypes.models import ContentType
from django.db.models import ExpressionWrapper, F, Func, IntegerField, Value
from strawberry.types import Info

from core.graphql.mixins import ChangelogMixin
from core.models import ObjectType as ObjectType_
from extras.graphql.mixins import CustomFieldsMixin, JournalEntriesMixin, TagsMixin
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
)


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
    annotated onto the queryset. We read the annotation rather than the `path`
    column directly: `path` is excluded from the schema, so accessing it through
    the resolver source would re-enter field resolution and recurse.
    """
    @strawberry_django.field(annotate={
        'ltree_level': ExpressionWrapper(
            Func(F('path'), function='nlevel', output_field=IntegerField()) - Value(1),
            output_field=IntegerField(),
        )
    })
    def level(self) -> int:
        return self.ltree_level


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

@strawberry_django.type(
    ContentType,
    fields=['id', 'app_label', 'model'],
    pagination=True
)
class ContentTypeType:
    pass


@strawberry_django.type(
    ObjectType_,
    fields=['id', 'app_label', 'model'],
    pagination=True
)
class ObjectTypeType:
    pass
