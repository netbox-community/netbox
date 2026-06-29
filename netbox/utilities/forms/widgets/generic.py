from django import forms
from django.contrib.contenttypes.models import ContentType

from .apiselect import APISelect
from .select import HTMXSelect

__all__ = (
    'GenericObjectSelect',
)


class GenericObjectSelect(forms.MultiWidget):
    """
    Composite widget pairing a content-type selector with an API-backed object selector. Used by
    GenericObjectChoiceField to represent a generic foreign key as a single form field.

    Because the subwidgets are supplied as a dict, the rendered names are suffixed with the dict keys,
    e.g. a field named "scope" renders inputs named "scope_content_type" and "scope_object_id".
    """
    template_name = 'widgets/generic_object.html'

    def __init__(self, content_type_widget=None, object_widget=None, attrs=None):
        widgets = {
            'content_type': content_type_widget or HTMXSelect(),
            'object_id': object_widget or APISelect(),
        }
        super().__init__(widgets, attrs)

    def decompress(self, value):
        # An object instance: split into (content type pk, object pk)
        if value and hasattr(value, '_meta'):
            return [ContentType.objects.get_for_model(value).pk, value.pk]
        # An already-decomposed [content_type, object_id] pair
        if isinstance(value, (list, tuple)):
            if len(value) == 2:
                return list(value)
            if len(value) == 1:
                return [value[0], None]
        return [None, None]
