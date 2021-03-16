from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError, MultipleObjectsReturned, ObjectDoesNotExist
from django.db.models import ManyToManyField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CreateOnlyDefault

from extras.api.customfields import CustomFieldsDataField, CustomFieldDefaultValues
from extras.models import CustomField, Tag
from utilities.utils import dict_to_filter_params


class ValidatedModelSerializer(serializers.ModelSerializer):
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


class CustomFieldModelSerializer(ValidatedModelSerializer):
    """
    Extends ModelSerializer to render any CustomFields and their values associated with an object.
    """
    custom_fields = CustomFieldsDataField(
        source='custom_field_data',
        default=CreateOnlyDefault(CustomFieldDefaultValues())
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance is not None:

            # Retrieve the set of CustomFields which apply to this type of object
            content_type = ContentType.objects.get_for_model(self.Meta.model)
            fields = CustomField.objects.filter(content_types=content_type)

            # Populate CustomFieldValues for each instance from database
            if type(self.instance) in (list, tuple):
                for obj in self.instance:
                    self._populate_custom_fields(obj, fields)
            else:
                self._populate_custom_fields(self.instance, fields)

    def _populate_custom_fields(self, instance, custom_fields):
        instance.custom_fields = {}
        for field in custom_fields:
            instance.custom_fields[field.name] = instance.cf.get(field.name)


#
# Nested serializers
#

class WritableNestedSerializer(serializers.ModelSerializer):
    """
    Returns a nested representation of an object on read, but accepts only a primary key on write.
    """
    def to_internal_value(self, data):

        if data is None:
            return None

        # Dictionary of related object attributes
        if isinstance(data, dict):
            params = dict_to_filter_params(data)
            queryset = self.Meta.model.objects
            try:
                return queryset.get(**params)
            except ObjectDoesNotExist:
                raise ValidationError(
                    "Related object not found using the provided attributes: {}".format(params)
                )
            except MultipleObjectsReturned:
                raise ValidationError(
                    "Multiple objects match the provided attributes: {}".format(params)
                )
            except FieldError as e:
                raise ValidationError(e)

        # Integer PK of related object
        if isinstance(data, int):
            pk = data
        else:
            try:
                # PK might have been mistakenly passed as a string
                pk = int(data)
            except (TypeError, ValueError):
                raise ValidationError(
                    "Related objects must be referenced by numeric ID or by dictionary of attributes. Received an "
                    "unrecognized value: {}".format(data)
                )

        # Look up object by PK
        queryset = self.Meta.model.objects
        try:
            return queryset.get(pk=int(data))
        except ObjectDoesNotExist:
            raise ValidationError(
                "Related object not found using the provided numeric ID: {}".format(pk)
            )


#
# Nested tags serialization
#

# Declared here for use by PrimaryModelSerializer, but should be imported from extras.api.nested_serializers
class NestedTagSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:tag-detail')

    class Meta:
        model = Tag
        fields = ['id', 'url', 'name', 'slug', 'color']


#
# Base model serializers
#

class OrganizationalModelSerializer(CustomFieldModelSerializer):
    """
    Adds support for custom fields.
    """
    pass


class PrimaryModelSerializer(CustomFieldModelSerializer):
    """
    Adds support for custom fields and tags.
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
            instance.tags.set(*[t.name for t in tags])
        else:
            instance.tags.clear()

        return instance


class NestedGroupModelSerializer(CustomFieldModelSerializer):
    """
    Extends OrganizationalModelSerializer to include MPTT support.
    """
    _depth = serializers.IntegerField(source='level', read_only=True)


class BulkOperationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
