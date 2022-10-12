import graphene
from dcim.fields import MACAddressField, WWNField
from django.db import models
from graphene import Dynamic
from graphene_django.converter import convert_django_field, get_django_field_description
from graphene_django.fields import DjangoConnectionField
from ipam.fields import IPAddressField, IPNetworkField
from taggit.managers import TaggableManager

from .fields import ObjectListField


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


@convert_django_field.register(models.ManyToManyField)
@convert_django_field.register(models.ManyToManyRel)
@convert_django_field.register(models.ManyToOneRel)
def convert_field_to_list_or_connection(field, registry=None):
    """
    From graphene_django.converter.py we need to monkey-patch this to return
    our ObjectListField with filtering support instead of DjangoListField
    """
    model = field.related_model

    def dynamic_type():
        _type = registry.get_type_for_model(model)
        if not _type:
            return

        if isinstance(field, models.ManyToManyField):
            description = get_django_field_description(field)
        else:
            description = get_django_field_description(field.field)

        # If there is a connection, we should transform the field
        # into a DjangoConnectionField
        if _type._meta.connection:
            # Use a DjangoFilterConnectionField if there are
            # defined filter_fields or a filterset_class in the
            # DjangoObjectType Meta
            if _type._meta.filter_fields or _type._meta.filterset_class:
                from .filter.fields import DjangoFilterConnectionField

                return DjangoFilterConnectionField(_type, required=True, description=description)

            return DjangoConnectionField(_type, required=True, description=description)

        return ObjectListField(
            _type,
            required=True,  # A Set is always returned, never None.
            description=description,
        )

    return Dynamic(dynamic_type)
