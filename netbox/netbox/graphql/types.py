import graphene

from django.contrib.contenttypes.models import ContentType
from extras.graphql.mixins import (
    ChangelogMixin,
    CustomFieldsMixin,
    JournalEntriesMixin,
    TagsMixin,
)
from graphene_django import DjangoObjectType

__all__ = (
    'BaseObjectType',
    'ObjectType',
    'OrganizationalObjectType',
    'NetBoxObjectType',
)


#
# Base types
#

class BaseObjectType(DjangoObjectType):
    """
    Base GraphQL object type for all NetBox objects. Restricts the model queryset to enforce object permissions.
    """
    display = graphene.String()
    class_type = graphene.String()

    class Meta:
        abstract = True

    @classmethod
    def get_queryset(cls, queryset, info):
        # Enforce object permissions on the queryset
        return queryset.restrict(info.context.user, 'view')

    def resolve_display(parent, info, **kwargs):
        return str(parent)

    def resolve_class_type(parent, info, **kwargs):
        return parent.__class__.__name__


class ObjectType(
    ChangelogMixin,
    BaseObjectType
):
    """
    Base GraphQL object type for unclassified models which support change logging
    """
    class Meta:
        abstract = True


class OrganizationalObjectType(
    ChangelogMixin,
    CustomFieldsMixin,
    TagsMixin,
    BaseObjectType
):
    """
    Base type for organizational models
    """
    class Meta:
        abstract = True


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
    class Meta:
        abstract = True


#
# Miscellaneous types
#

class ContentTypeType(DjangoObjectType):

    class Meta:
        model = ContentType
        fields = ('id', 'app_label', 'model')
