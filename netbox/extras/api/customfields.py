from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

from extras.models import CustomField, CustomFieldChoice


#
# Custom fields
#

class CustomFieldSerializer(serializers.BaseSerializer):
    """
    Extends ModelSerializer to render any CustomFields and their values associated with an object.
    """

    def to_representation(self, manager):

        # Initialize custom fields dictionary
        data = {f.name: None for f in self.parent._custom_fields}

        # Assign CustomFieldValues from database
        for cfv in manager.all():
            data[cfv.field.name] = cfv.value

        return data


class CustomFieldModelSerializer(serializers.ModelSerializer):
    custom_fields = CustomFieldSerializer(source='custom_field_values')

    def __init__(self, *args, **kwargs):

        super(CustomFieldModelSerializer, self).__init__(*args, **kwargs)

        # Cache the list of custom fields for this model
        content_type = ContentType.objects.get_for_model(self.Meta.model)
        self._custom_fields = CustomField.objects.filter(obj_type=content_type)


class CustomFieldChoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomFieldChoice
        fields = ['id', 'value']