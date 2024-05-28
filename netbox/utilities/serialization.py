import json

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
    if hasattr(obj, 'custom_field_data'):
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


def deserialize_object(model, fields, pk=None):
    """
    Instantiate an object from the given model and field data. Functions as
    the complement to serialize_object().
    """
    content_type = ContentType.objects.get_for_model(model)
    if 'custom_fields' in fields:
        fields['custom_field_data'] = fields.pop('custom_fields')
    data = {
        'model': '.'.join(content_type.natural_key()),
        'pk': pk,
        'fields': fields,
    }
    instance = list(serializers.deserialize('python', [data]))[0]

    return instance
