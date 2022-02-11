import graphene
from graphene_django.converter import convert_django_field
from taggit.managers import TaggableManager

from dcim.fields import MACAddressField, WWNField
from ipam.fields import IPAddressField, IPNetworkField


@convert_django_field.register(TaggableManager)
def convert_field_to_tags_list(field, registry=None):
    """
    Register conversion handler for django-taggit's TaggableManager
    """
    return graphene.List(graphene.String)


@convert_django_field.register(IPAddressField)
@convert_django_field.register(IPNetworkField)
@convert_django_field.register(MACAddressField)
@convert_django_field.register(WWNField)
def convert_field_to_string(field, registry=None):
    # TODO: Update to use get_django_field_description under django_graphene v3.0
    return graphene.String(description=field.help_text, required=not field.null)
