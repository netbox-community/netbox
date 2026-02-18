import strawberry
import strawberry_django
from django.contrib.contenttypes.models import ContentType
from strawberry.types import Info

from core.graphql.mixins import ChangelogMixin
from core.models import ObjectType as ObjectType_
from extras.graphql.mixins import CustomFieldsMixin, JournalEntriesMixin, TagsMixin
from users.graphql.mixins import OwnerMixin

__all__ = (
    'BaseObjectType',
    'ContentTypeType',
    'NestedGroupObjectType',
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


class NestedGroupObjectType(
    ChangelogMixin,
    CustomFieldsMixin,
    JournalEntriesMixin,
    TagsMixin,
    OwnerMixin,
    BaseObjectType
):
    """
    Base GraphQL type for models which inherit from NestedGroupModel.
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
