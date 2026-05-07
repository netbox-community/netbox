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
    add_tags = NestedTagSerializer(many=True, required=False, write_only=True)
    remove_tags = NestedTagSerializer(many=True, required=False, write_only=True)

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)

        # Workaround to bypass requirement to include add_tags/remove_tags in Meta.fields on every serializer
        if type(data) is dict:
            tag_serializer = NestedTagSerializer(many=True)
            for field_name in ('add_tags', 'remove_tags'):
                if field_name in data:
                    ret[field_name] = tag_serializer.to_internal_value(data[field_name])

        return ret

    def validate(self, data):
        # Skip validation for nested serializer representations (e.g. when used as a related field)
        if type(data) is not dict:
            return super().validate(data)

        if data.get('tags') and (data.get('add_tags') or data.get('remove_tags')):
            raise serializers.ValidationError({
                'tags': 'Cannot specify "tags" together with "add_tags" or "remove_tags".'
            })

        if self.instance is None and data.get('remove_tags'):
            raise serializers.ValidationError({
                'remove_tags': 'Cannot use "remove_tags" when creating a new object.'
            })

        if data.get('add_tags') and data.get('remove_tags'):
            add_pks = {t.pk for t in data['add_tags']}
            remove_pks = {t.pk for t in data['remove_tags']}
            overlap = [t for t in data['add_tags'] if t.pk in (add_pks & remove_pks)]
            if overlap:
                raise serializers.ValidationError({
                    'remove_tags':
                        f'Tags may not be present in both "add_tags" and "remove_tags": '
                        f'{", ".join(t.name for t in overlap)}'
                })

        # Pop add_tags/remove_tags before calling super() to prevent them from being passed
        # to the model constructor during ValidatedModelSerializer validation
        add_tags = data.pop('add_tags', None)
        remove_tags = data.pop('remove_tags', None)

        data = super().validate(data)

        # Restore for use in create()/update()
        if add_tags is not None:
            data['add_tags'] = add_tags
        if remove_tags is not None:
            data['remove_tags'] = remove_tags

        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags', None)
        add_tags = validated_data.pop('add_tags', None)
        validated_data.pop('remove_tags', None)
        instance = super().create(validated_data)

        if tags is not None:
            return self._save_tags(instance, tags)
        if add_tags is not None:
            instance.tags.add(*[t.name for t in add_tags])
        return instance

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        add_tags = validated_data.pop('add_tags', None)
        remove_tags = validated_data.pop('remove_tags', None)

        # Cache tags on instance for change logging
        instance._tags = tags or []

        instance = super().update(instance, validated_data)

        if tags is not None:
            return self._save_tags(instance, tags)
        if add_tags is not None:
            instance.tags.add(*[t.name for t in add_tags])
        if remove_tags is not None:
            instance.tags.remove(*[t.name for t in remove_tags])
        if add_tags is not None or remove_tags is not None:
            instance._tags = instance.tags.all()

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
