from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from extras.models import CF_TYPE_SELECT, CustomField, CustomFieldChoice, CustomFieldValue


#
# Custom fields
#

class CustomFieldsSerializer(serializers.BaseSerializer):

    def to_representation(self, obj):
        return obj

    def to_internal_value(self, data):

        parent_content_type = ContentType.objects.get_for_model(self.parent.Meta.model)

        for custom_field, value in data.items():

            # Validate custom field name
            try:
                cf = CustomField.objects.get(name=custom_field)
            except CustomField.DoesNotExist:
                raise ValidationError(u"Unknown custom field: {}".format(custom_field))

            # Validate custom field content type
            if parent_content_type not in cf.obj_type.all():
                raise ValidationError(u"Invalid custom field for {} objects".format(parent_content_type))

            # Validate selected choice
            if cf.type == CF_TYPE_SELECT:
                valid_choices = [c.pk for c in cf.choices.all()]
                if value not in valid_choices:
                    raise ValidationError(u"Invalid choice ({}) for field {}".format(value, custom_field))

        return data


class CustomFieldModelSerializer(serializers.ModelSerializer):
    """
    Extends ModelSerializer to render any CustomFields and their values associated with an object.
    """
    custom_fields = CustomFieldsSerializer()

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
                defaults={'serialized_value': value},
            )

    def create(self, validated_data):

        custom_fields = validated_data.pop('custom_fields')

        with transaction.atomic():

            instance = super(CustomFieldModelSerializer, self).create(validated_data)

            # Save custom fields
            self._save_custom_fields(instance, custom_fields)
            instance.custom_fields = custom_fields

        return instance

    def update(self, instance, validated_data):

        custom_fields = validated_data.pop('custom_fields')

        with transaction.atomic():

            instance = super(CustomFieldModelSerializer, self).update(instance, validated_data)

            # Save custom fields
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
