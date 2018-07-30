from __future__ import unicode_literals

from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from extras.constants import CF_TYPE_BOOLEAN, CF_TYPE_DATE, CF_TYPE_INTEGER, CF_TYPE_SELECT
from extras.models import CustomField, CustomFieldChoice, CustomFieldValue
from utilities.api import ValidatedModelSerializer


#
# Custom fields
#

class CustomFieldsSerializer(serializers.BaseSerializer):

    def to_representation(self, obj):
        return obj

    def to_internal_value(self, data):

        content_type = ContentType.objects.get_for_model(self.parent.Meta.model)
        custom_fields = {field.name: field for field in CustomField.objects.filter(obj_type=content_type)}

        for field_name, value in data.items():

            try:
                cf = custom_fields[field_name]
            except KeyError:
                raise ValidationError(
                    "Invalid custom field for {} objects: {}".format(content_type, field_name)
                )

            # Data validation
            if value not in [None, '']:

                # Validate integer
                if cf.type == CF_TYPE_INTEGER:
                    try:
                        int(value)
                    except ValueError:
                        raise ValidationError(
                            "Invalid value for integer field {}: {}".format(field_name, value)
                        )

                # Validate boolean
                if cf.type == CF_TYPE_BOOLEAN and value not in [True, False, 1, 0]:
                    raise ValidationError(
                        "Invalid value for boolean field {}: {}".format(field_name, value)
                    )

                # Validate date
                if cf.type == CF_TYPE_DATE:
                    try:
                        datetime.strptime(value, '%Y-%m-%d')
                    except ValueError:
                        raise ValidationError(
                            "Invalid date for field {}: {}. (Required format is YYYY-MM-DD.)".format(field_name, value)
                        )

                # Validate selected choice
                if cf.type == CF_TYPE_SELECT:
                    try:
                        value = int(value)
                    except ValueError:
                        raise ValidationError(
                            "{}: Choice selections must be passed as integers.".format(field_name)
                        )
                    valid_choices = [c.pk for c in cf.choices.all()]
                    if value not in valid_choices:
                        raise ValidationError(
                            "Invalid choice for field {}: {}".format(field_name, value)
                        )

            elif cf.required:
                raise ValidationError("Required field {} cannot be empty.".format(field_name))

        # Check for missing required fields
        missing_fields = []
        for field_name, field in custom_fields.items():
            if field.required and field_name not in data:
                missing_fields.append(field_name)
        if missing_fields:
            raise ValidationError("Missing required fields: {}".format(u", ".join(missing_fields)))

        return data


class CustomFieldModelSerializer(ValidatedModelSerializer):
    """
    Extends ModelSerializer to render any CustomFields and their values associated with an object.
    """
    custom_fields = CustomFieldsSerializer(required=False)

    def __init__(self, *args, **kwargs):

        def _populate_custom_fields(instance, fields):
            custom_fields = {f.name: None for f in fields}
            for cfv in instance.custom_field_values.all():
                if cfv.field.type == CF_TYPE_SELECT:
                    custom_fields[cfv.field.name] = CustomFieldChoiceSerializer(cfv.value).data
                else:
                    custom_fields[cfv.field.name] = cfv.value
            instance.custom_fields = custom_fields

        super(CustomFieldModelSerializer, self).__init__(*args, **kwargs)

        if self.instance is not None:

            # Retrieve the set of CustomFields which apply to this type of object
            content_type = ContentType.objects.get_for_model(self.Meta.model)
            fields = CustomField.objects.filter(obj_type=content_type)

            # Populate CustomFieldValues for each instance from database
            try:
                for obj in self.instance:
                    _populate_custom_fields(obj, fields)
            except TypeError:
                _populate_custom_fields(self.instance, fields)

    def _save_custom_fields(self, instance, custom_fields):
        content_type = ContentType.objects.get_for_model(self.Meta.model)
        for field_name, value in custom_fields.items():
            custom_field = CustomField.objects.get(name=field_name)
            CustomFieldValue.objects.update_or_create(
                field=custom_field,
                obj_type=content_type,
                obj_id=instance.pk,
                defaults={'serialized_value': custom_field.serialize_value(value)},
            )

    def create(self, validated_data):

        custom_fields = validated_data.pop('custom_fields', None)

        with transaction.atomic():

            instance = super(CustomFieldModelSerializer, self).create(validated_data)

            # Save custom fields
            if custom_fields is not None:
                self._save_custom_fields(instance, custom_fields)
                instance.custom_fields = custom_fields

        return instance

    def update(self, instance, validated_data):

        custom_fields = validated_data.pop('custom_fields', None)

        with transaction.atomic():

            instance = super(CustomFieldModelSerializer, self).update(instance, validated_data)

            # Save custom fields
            if custom_fields is not None:
                self._save_custom_fields(instance, custom_fields)
                instance.custom_fields = custom_fields

        return instance


class CustomFieldChoiceSerializer(serializers.ModelSerializer):
    """
    Imitate utilities.api.ChoiceFieldSerializer
    """
    value = serializers.IntegerField(source='pk')
    label = serializers.CharField(source='value')

    class Meta:
        model = CustomFieldChoice
        fields = ['value', 'label']
