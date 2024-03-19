from typing import Annotated, List

import strawberry
from strawberry import auto
import strawberry_django

from core.models import ObjectType as ObjectType_
from django.contrib.contenttypes.models import ContentType
from extras.graphql.mixins import (
    ChangelogMixin,
    CustomFieldsMixin,
    JournalEntriesMixin,
    TagsMixin,
)

__all__ = (
    'BaseObjectType',
    'ObjectType',
    'OrganizationalObjectType',
    'NetBoxObjectType',
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
    def get_queryset(cls, queryset, info, **kwargs):
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


class ObjectType(
    ChangelogMixin,
    BaseObjectType
):
    """
    Base GraphQL object type for unclassified models which support change logging
    """
    pass


class OrganizationalObjectType(
    ChangelogMixin,
    CustomFieldsMixin,
    TagsMixin,
    BaseObjectType
):
    """
    Base type for organizational models
    """
    pass


class NetBoxObjectType(
    ChangelogMixin,
    CustomFieldsMixin,
    JournalEntriesMixin,
    TagsMixin,
    BaseObjectType
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
)
class ContentTypeType:
    pass


@strawberry_django.type(
    ObjectType_,
    fields=['id', 'app_label', 'model'],
)
class ObjectTypeType:
    pass
