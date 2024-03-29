from functools import cached_property

from rest_framework import serializers
from rest_framework.utils.serializer_helpers import BindingDict
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from utilities.api import get_related_object_by_attrs

__all__ = (
    'BaseModelSerializer',
    'ValidatedModelSerializer',
)


class BaseModelSerializer(serializers.ModelSerializer):
    display = serializers.SerializerMethodField(read_only=True)

    def __init__(self, *args, nested=False, fields=None, **kwargs):
        """
        Extends the base __init__() method to support dynamic fields.

        :param nested: Set to True if this serializer is being employed within a parent serializer
        :param fields: An iterable of fields to include when rendering the serialized object, If nested is
            True but no fields are specified, Meta.brief_fields will be used.
        """
        self.nested = nested
        self._requested_fields = fields

        # Disable validators for nested objects (which already exist)
        if self.nested:
            self.validators = []

        # If this serializer is nested but no fields have been specified,
        # default to using Meta.brief_fields (if set)
        if self.nested and not fields:
            self._requested_fields = getattr(self.Meta, 'brief_fields', None)

        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):

        # If initialized as a nested serializer, we should expect to receive the attrs or PK
        # identifying a related object.
        if self.nested:
            queryset = self.Meta.model.objects.all()
            return get_related_object_by_attrs(queryset, data)

        return super().to_internal_value(data)

    @cached_property
    def fields(self):
        """
        Override the fields property to check for requested fields. If defined,
        return only the applicable fields.
        """
        if not self._requested_fields:
            return super().fields

        fields = BindingDict(self)
        for key, value in self.get_fields().items():
            if key in self._requested_fields:
                fields[key] = value
        return fields

    @extend_schema_field(OpenApiTypes.STR)
    def get_display(self, obj):
        return str(obj)


class ValidatedModelSerializer(BaseModelSerializer):
    """
    Extends the built-in ModelSerializer to enforce calling full_clean() on a copy of the associated instance during
    validation. (DRF does not do this by default; see https://github.com/encode/django-rest-framework/issues/3144)
    """
    def validate(self, data):

        # Skip validation if we're being used to represent a nested object
        if self.nested:
            return data

        attrs = data.copy()

        # Remove custom field data (if any) prior to model validation
        attrs.pop('custom_fields', None)

        # Skip ManyToManyFields
        opts = self.Meta.model._meta
        m2m_values = {}
        for field in [*opts.local_many_to_many, *opts.related_objects]:
            if field.name in attrs:
                m2m_values[field.name] = attrs.pop(field.name)

        # Run clean() on an instance of the model
        if self.instance is None:
            instance = self.Meta.model(**attrs)
        else:
            instance = self.instance
            for k, v in attrs.items():
                setattr(instance, k, v)
        instance._m2m_values = m2m_values
        instance.full_clean()

        return data
