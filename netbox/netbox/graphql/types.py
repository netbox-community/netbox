import graphene
from graphene.types.generic import GenericScalar
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
    """
    Extends BaseObjectType with support for custom field data.
    """
    # custom_fields = GenericScalar()

    class Meta:
        abstract = True

    # def resolve_custom_fields(self, info):
    #     return self.custom_field_data


class TaggedObjectType(ObjectType):
    """
    Extends ObjectType with support for Tags
    """
    tags = graphene.List(graphene.String)

    class Meta:
        abstract = True

    def resolve_tags(self, info):
        return self.tags.all()
