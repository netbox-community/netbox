from rest_framework import serializers
from rest_framework.fields import CreateOnlyDefault

from extras.api.customfields import CustomFieldDefaultValues, CustomFieldListSerializer, CustomFieldsDataField

from .base import ValidatedModelSerializer
from .nested import NestedTagSerializer

__all__ = (
    'ChangeLogMessageSerializer',
    'CustomFieldModelSerializer',
    'NetBoxModelSerializer',
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

    @classmethod
    def many_init(cls, *args, **kwargs):
        """
        We can't call super().many_init() and change the outcome because by the time it returns,
        the plain ListSerializer is already instantiated.
        Because every NetBox serializer defines its own Meta which doesn't inherit from a parent Meta,
        this would silently not apply to any real serializer.
        Thats why this method replicates many_init from parent and changed the default value for list_serializer_class.
        """
        list_kwargs = {}
        for key in serializers.LIST_SERIALIZER_KWARGS_REMOVE:
            value = kwargs.pop(key, None)
            if value is not None:
                list_kwargs[key] = value
        list_kwargs['child'] = cls(*args, **kwargs)
        list_kwargs.update({
            key: value for key, value in kwargs.items()
            if key in serializers.LIST_SERIALIZER_KWARGS
        })
        meta = getattr(cls, 'Meta', None)
        list_serializer_class = getattr(meta, 'list_serializer_class', CustomFieldListSerializer)
        return list_serializer_class(*args, **list_kwargs)


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
            # Cache tags on instance so serialize_object() can reuse them without a DB query
            instance._tags = tags
            instance.tags.set([t.name for t in tags])
        else:
            instance._tags = []
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


class NetBoxModelSerializer(
    ChangeLogMessageSerializer,
    TaggableModelSerializer,
    CustomFieldModelSerializer,
    ValidatedModelSerializer
):
    """
    Adds support for custom fields and tags.
    """
    pass
