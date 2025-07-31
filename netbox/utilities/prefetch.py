from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import ManyToManyField
from django.db.models.fields.related import ForeignObjectRel
from taggit.managers import TaggableManager

__all__ = (
    'get_prefetchable_fields',
)


def get_prefetchable_fields(model):
    """
    Return a list containing the names of all fields on the given model which support prefetching.
    """
    field_names = []

    for field in model._meta.get_fields():
        # Forward relations (e.g. ManyToManyFields)
        if isinstance(field, ManyToManyField):
            field_names.append(field.name)

        # Reverse relations (e.g. reverse ForeignKeys, reverse M2M)
        elif isinstance(field, ForeignObjectRel):
            field_names.append(field.get_accessor_name())

        # Generic relations
        elif isinstance(field, GenericRelation):
            field_names.append(field.name)

        # Tags
        elif isinstance(field, TaggableManager):
            field_names.append(field.name)

    return field_names
