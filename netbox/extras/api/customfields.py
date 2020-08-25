from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CreateOnlyDefault

from extras.choices import *
from extras.models import CustomField
from utilities.api import ValidatedModelSerializer


#
# Custom fields
#

class CustomFieldDefaultValues:
    """
    Return a dictionary of all CustomFields assigned to the parent model and their default values.
    """
    requires_context = True

    def __call__(self, serializer_field):
        self.model = serializer_field.parent.Meta.model

        # Retrieve the CustomFields for the parent model
        content_type = ContentType.objects.get_for_model(self.model)
        fields = CustomField.objects.filter(obj_type=content_type)

        # Populate the default value for each CustomField
        value = {}
        for field in fields:
            if field.default:
                if field.type == CustomFieldTypeChoices.TYPE_INTEGER:
                    field_value = int(field.default)
                elif field.type == CustomFieldTypeChoices.TYPE_BOOLEAN:
                    # TODO: Fix default value assignment for boolean custom fields
                    field_value = False if field.default.lower() == 'false' else bool(field.default)
                else:
                    field_value = field.default
                value[field.name] = field_value
            else:
                value[field.name] = None

        return value


class CustomFieldsSerializer(serializers.BaseSerializer):

    def to_representation(self, obj):
        return obj

    def to_internal_value(self, data):

        content_type = ContentType.objects.get_for_model(self.parent.Meta.model)
        custom_fields = {
            field.name: field for field in CustomField.objects.filter(obj_type=content_type)
        }

        for field_name, value in data.items():

            try:
                cf = custom_fields[field_name]
            except KeyError:
                raise ValidationError(f"Invalid custom field for {content_type} objects: {field_name}")

            # Data validation
            if value not in [None, '']:

                # Validate integer
                if cf.type == CustomFieldTypeChoices.TYPE_INTEGER:
                    try:
                        int(value)
                    except ValueError:
                        raise ValidationError(f"Invalid value for integer field {field_name}: {value}")

                # Validate boolean
                if cf.type == CustomFieldTypeChoices.TYPE_BOOLEAN and value not in [True, False, 1, 0]:
                    raise ValidationError(f"Invalid value for boolean field {field_name}: {value}")

                # Validate date
                if cf.type == CustomFieldTypeChoices.TYPE_DATE:
                    try:
                        datetime.strptime(value, '%Y-%m-%d')
                    except ValueError:
                        raise ValidationError(
                            f"Invalid date for field {field_name}: {value}. (Required format is YYYY-MM-DD.)"
                        )

                # Validate selected choice
                if cf.type == CustomFieldTypeChoices.TYPE_SELECT:
                    if value not in cf.choices:
                        raise ValidationError(f"Invalid choice for field {field_name}: {value}")

            elif cf.required:
                raise ValidationError(f"Required field {field_name} cannot be empty.")

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
    custom_fields = CustomFieldsSerializer(
        source='custom_field_data',
        required=False,
        default=CreateOnlyDefault(CustomFieldDefaultValues())
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance is not None:

            # Retrieve the set of CustomFields which apply to this type of object
            content_type = ContentType.objects.get_for_model(self.Meta.model)
            fields = CustomField.objects.filter(obj_type=content_type)

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
