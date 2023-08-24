import strawberry
from strawberry import auto

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

class BaseObjectType:
    """
    Base GraphQL object type for all NetBox objects. Restricts the model queryset to enforce object permissions.
    """
    display: auto
    class_type: auto

    @classmethod
    def get_queryset(cls, queryset, info):
        # Enforce object permissions on the queryset
        return queryset.restrict(info.context.request.user, 'view')

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

class ContentTypeType:

    class Meta:
        model = ContentType
        fields = ('id', 'app_label', 'model')
