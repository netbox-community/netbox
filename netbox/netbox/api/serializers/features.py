from rest_framework import serializers
from rest_framework.fields import CreateOnlyDefault

from extras.api.customfields import CustomFieldsDataField, CustomFieldDefaultValues
from .nested import NestedTagSerializer

__all__ = (
    'CustomFieldModelSerializer',
    'TaggableModelSerializer',
)


class CustomFieldModelSerializer(serializers.Serializer):
    """
    Introduces support for custom field assignment and representation.
    """
    custom_fields = CustomFieldsDataField(
        source='custom_field_data',
        default=CreateOnlyDefault(CustomFieldDefaultValues())
    )


class TaggableModelSerializer(serializers.Serializer):
    """
    Introduces support for Tag assignment. Adds `tags` serialization, and handles tag assignment
    on create() and update().
    """
    tags = NestedTagSerializer(many=True, required=False)

    def create(self, validated_data):
        tags = validated_data.pop('tags', None)
        instance = super().create(validated_data)

        if tags is not None:
            return self._save_tags(instance, tags)
        return instance

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)

        # Cache tags on instance for change logging
        instance._tags = tags or []

        instance = super().update(instance, validated_data)

        if tags is not None:
            return self._save_tags(instance, tags)
        return instance

    def _save_tags(self, instance, tags):
        if tags:
            instance.tags.set([t.name for t in tags])
        else:
            instance.tags.clear()

        return instance
