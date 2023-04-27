from django.db.models import ManyToManyField
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

__all__ = (
    'BaseModelSerializer',
    'ValidatedModelSerializer',
)


class BaseModelSerializer(serializers.ModelSerializer):
    display = serializers.SerializerMethodField(read_only=True)

    @extend_schema_field(OpenApiTypes.STR)
    def get_display(self, obj):
        return str(obj)


class ValidatedModelSerializer(BaseModelSerializer):
    """
    Extends the built-in ModelSerializer to enforce calling full_clean() on a copy of the associated instance during
    validation. (DRF does not do this by default; see https://github.com/encode/django-rest-framework/issues/3144)
    """
    def validate(self, data):

        # Remove custom fields data and tags (if any) prior to model validation
        attrs = data.copy()
        attrs.pop('custom_fields', None)
        attrs.pop('tags', None)

        # Skip ManyToManyFields
        for field in self.Meta.model._meta.get_fields():
            if isinstance(field, ManyToManyField):
                attrs.pop(field.name, None)

        # Run clean() on an instance of the model
        if self.instance is None:
            instance = self.Meta.model(**attrs)
        else:
            instance = self.instance
            for k, v in attrs.items():
                setattr(instance, k, v)
        instance.full_clean()

        return data
