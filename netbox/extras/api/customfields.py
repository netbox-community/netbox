from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

from extras.models import CF_TYPE_SELECT, CustomField, CustomFieldChoice, CustomFieldValue


#
# Custom fields
#

class CustomFieldsSerializer(serializers.BaseSerializer):

    def to_representation(self, obj):
        return obj


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

        # Retrieve the set of CustomFields which apply to this type of object
        content_type = ContentType.objects.get_for_model(self.Meta.model)
        fields = CustomField.objects.filter(obj_type=content_type)

        # Populate CustomFieldValues for each instance from database
        try:
            for obj in self.instance:
                _populate_custom_fields(obj, fields)
        except TypeError:
            _populate_custom_fields(self.instance, fields)


class CustomFieldChoiceSerializer(serializers.ModelSerializer):
    """
    Imitate utilities.api.ChoiceFieldSerializer
    """
    value = serializers.IntegerField(source='pk')
    label = serializers.CharField(source='value')

    class Meta:
        model = CustomFieldChoice
        fields = ['value', 'label']
