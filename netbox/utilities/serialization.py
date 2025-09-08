import json

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core import serializers

from extras.utils import is_taggable

__all__ = (
    'deserialize_object',
    'serialize_object',
)


def serialize_object(obj, resolve_tags=True, extra=None, exclude=None):
    """
    Return a generic JSON representation of an object using Django's built-in serializer. (This is used for things like
    change logging, not the REST API.) Optionally include a dictionary to supplement the object data. A list of keys
    can be provided to exclude them from the returned dictionary.

    Args:
        obj: The object to serialize
        resolve_tags: If true, any assigned tags will be represented by their names
        extra: Any additional data to include in the serialized output. Keys provided in this mapping will
            override object attributes.
        exclude: An iterable of attributes to exclude from the serialized output
    """
    json_str = serializers.serialize('json', [obj])
    data = json.loads(json_str)[0]['fields']
    exclude = exclude or []

    # Include custom_field_data as "custom_fields"
    if 'custom_field_data' in data:
        data['custom_fields'] = data.pop('custom_field_data')

    # Resolve any assigned tags to their names. Check for tags cached on the instance;
    # fall back to using the manager.
    if resolve_tags and is_taggable(obj):
        tags = getattr(obj, '_tags', None) or obj.tags.all()
        data['tags'] = sorted([tag.name for tag in tags])

    # Skip any excluded attributes
    for key in list(data.keys()):
        if key in exclude:
            data.pop(key)

    # Append any extra data
    if extra is not None:
        data.update(extra)

    return data


def deserialize_object(model, data, pk=None):
    """
    Instantiate an object from the given model and field data. Functions as
    the complement to serialize_object().
    """
    content_type = ContentType.objects.get_for_model(model)
    data = data.copy()
    m2m_data = {}

    # Account for custom field data
    if 'custom_fields' in data:
        data['custom_field_data'] = data.pop('custom_fields')

    # Pop any assigned tags to handle the M2M relationships manually
    if is_taggable(model) and data.get('tags'):
        Tag = apps.get_model('extras', 'Tag')
        m2m_data['tags'] = Tag.objects.filter(name__in=data.pop('tags'))

    # Separate any non-field attributes for assignment after deserialization of the object
    model_fields = [
        field.name for field in model._meta.get_fields()
    ]
    attrs = {
        name: data.pop(name) for name in list(data.keys())
        if name not in model_fields
    }

    # Employ Django's native Python deserializer to produce the instance
    data = {
        'model': '.'.join(content_type.natural_key()),
        'pk': pk,
        'fields': data,
    }
    instance = list(serializers.deserialize('python', [data]))[0]

    # Assign non-field attributes
    for name, value in attrs.items():
        setattr(instance.object, name, value)

    # Apply any additional M2M assignments
    instance.m2m_data.update(**m2m_data)

    return instance
