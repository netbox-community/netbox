from rest_framework import serializers
from rest_framework.fields import CreateOnlyDefault

from extras.api.customfields import CustomFieldsDataField, CustomFieldDefaultValues
from .nested import NestedTagSerializer

__all__ = (
    'ChangeLogMessageSerializer',
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


class ChangeLogMessageSerializer(serializers.Serializer):
    changelog_message = serializers.CharField(
        write_only=True,
        required=False,
    )

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)

        # Workaround to bypass requirement to include changelog_message in Meta.fields on every serializer
        if type(data) is dict and 'changelog_message' in data:
            ret['changelog_message'] = data['changelog_message']

        return ret

    def save(self, **kwargs):
        if self.instance is not None:
            self.instance._changelog_message = self.validated_data.get('changelog_message')
        return super().save(**kwargs)
