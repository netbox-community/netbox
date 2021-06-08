import graphene
from graphene_django.converter import convert_django_field
from taggit.managers import TaggableManager


@convert_django_field.register(TaggableManager)
def convert_field_to_tags_list(field, registry=None):
    """
    Register conversion handler for django-taggit's TaggableManager
    """
    return graphene.List(graphene.String)
