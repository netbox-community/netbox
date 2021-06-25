import graphene
from graphene_django.converter import convert_django_field

from ipam.fields import IPAddressField, IPNetworkField


@convert_django_field.register(IPAddressField)
@convert_django_field.register(IPNetworkField)
def convert_field_to_string(field, registry=None):
    # TODO: Update to use get_django_field_description under django_graphene v3.0
    return graphene.String(description=field.help_text, required=not field.null)
