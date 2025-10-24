import strawberry
import strawberry_django
from strawberry.types import Info
from django.contrib.contenttypes.models import ContentType

from core.graphql.mixins import ChangelogMixin
from core.models import ObjectType as ObjectType_
from extras.graphql.mixins import CustomFieldsMixin, JournalEntriesMixin, TagsMixin

__all__ = (
    'BaseObjectTypeV1',
    'ContentTypeTypeV1',
    'ObjectTypeV1',
    'OrganizationalObjectTypeV1',
    'NetBoxObjectTypeV1',
)


#
# Base types
#

@strawberry.type
class BaseObjectTypeV1:
    """
    Base GraphQL object type for all NetBox objects. Restricts the model queryset to enforce object permissions.
    """

    @classmethod
    def get_queryset(cls, queryset, info: Info, **kwargs):
        # Enforce object permissions on the queryset
        if hasattr(queryset, 'restrict'):
            return queryset.restrict(info.context.request.user, 'view')
        else:
            return queryset

    @strawberry_django.field
    def display(self) -> str:
        return str(self)

    @strawberry_django.field
    def class_type(self) -> str:
        return self.__class__.__name__


class ObjectTypeV1(
    ChangelogMixin,
    BaseObjectTypeV1
):
    """
    Base GraphQL object type for unclassified models which support change logging
    """
    pass


class OrganizationalObjectTypeV1(
    ChangelogMixin,
    CustomFieldsMixin,
    TagsMixin,
    BaseObjectTypeV1
):
    """
    Base type for organizational models
    """
    pass


class NetBoxObjectTypeV1(
    ChangelogMixin,
    CustomFieldsMixin,
    JournalEntriesMixin,
    TagsMixin,
    BaseObjectTypeV1
):
    """
    GraphQL type for most NetBox models. Includes support for custom fields, change logging, journaling, and tags.
    """
    pass


#
# Miscellaneous types
#

@strawberry_django.type(
    ContentType,
    fields=['id', 'app_label', 'model'],
    pagination=True
)
class ContentTypeTypeV1:
    pass


@strawberry_django.type(
    ObjectType_,
    fields=['id', 'app_label', 'model'],
    pagination=True
)
class ObjectTypeTypeV1:
    pass
