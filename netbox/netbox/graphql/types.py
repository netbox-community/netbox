import graphene
from graphene_django import DjangoObjectType

__all__ = (
    'BaseObjectType',
    'ObjectType',
    'TaggedObjectType',
)


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


class ObjectType(BaseObjectType):
    # TODO: Custom fields support

    class Meta:
        abstract = True


class TaggedObjectType(ObjectType):
    """
    Extends ObjectType with support for Tags
    """
    tags = graphene.List(graphene.String)

    class Meta:
        abstract = True

    def resolve_tags(self, info):
        return self.tags.all()
