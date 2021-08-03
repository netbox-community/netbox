from django.contrib.contenttypes.models import ContentType
from graphene_django import DjangoObjectType

from extras.graphql.mixins import CustomFieldsMixin, TagsMixin

__all__ = (
    'BaseObjectType',
    'ObjectType',
    'TaggedObjectType',
)


#
# Base types
#

class BaseObjectType(DjangoObjectType):
    """
    Base GraphQL object type for all NetBox objects
    """
    class Meta:
        abstract = True

    @classmethod
    def get_queryset(cls, queryset, info):
        # Enforce object permissions on the queryset
        return queryset.restrict(info.context.user, 'view')


class ObjectType(CustomFieldsMixin, BaseObjectType):
    """
    Extends BaseObjectType with support for custom fields.
    """
    class Meta:
        abstract = True


class TaggedObjectType(CustomFieldsMixin, TagsMixin, BaseObjectType):
    """
    Extends BaseObjectType with support for custom fields and tags
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
