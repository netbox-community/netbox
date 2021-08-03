from django.contrib.contenttypes.models import ContentType
from graphene_django import DjangoObjectType

from extras.graphql.mixins import CustomFieldsMixin, JournalEntriesMixin, TagsMixin

__all__ = (
    'BaseObjectType',
    'OrganizationalObjectType',
    'PrimaryObjectType',
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


class OrganizationalObjectType(
    CustomFieldsMixin,
    BaseObjectType
):
    """
    Base type for organizational models
    """
    class Meta:
        abstract = True


class PrimaryObjectType(
    CustomFieldsMixin,
    JournalEntriesMixin,
    TagsMixin,
    BaseObjectType
):
    """
    Base type for primary models
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
