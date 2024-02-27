from rest_framework import serializers
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
        super().__init__(*args, **kwargs)

        self.nested = nested

        if nested and not fields:
            fields = getattr(self.Meta, 'brief_fields', None)

        # If specific fields have been requested, omit the others
        if fields:
            for field in list(self.fields.keys()):
                if field not in fields:
                    self.fields.pop(field)

    def to_internal_value(self, data):

        # If initialized as a nested serializer, we should expect to receive the attrs or PK
        # identifying a related object.
        if self.nested:
            queryset = self.Meta.model.objects.all()
            return get_related_object_by_attrs(queryset, data)

        return super().to_internal_value(data)

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
        m2m_values = {}
        for field in self.Meta.model._meta.local_many_to_many:
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
