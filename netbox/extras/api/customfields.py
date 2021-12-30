from django.contrib.contenttypes.models import ContentType
from rest_framework.fields import Field

from extras.choices import CustomFieldTypeChoices
from extras.models import CustomField


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
        fields = CustomField.objects.filter(content_types=content_type)

        # Populate the default value for each CustomField
        value = {}
        for field in fields:
            if field.default is not None:
                value[field.name] = field.default
            else:
                value[field.name] = None

        return value


class CustomFieldsDataField(Field):

    def _get_custom_fields(self):
        """
        Cache CustomFields assigned to this model to avoid redundant database queries
        """
        if not hasattr(self, '_custom_fields'):
            content_type = ContentType.objects.get_for_model(self.parent.Meta.model)
            self._custom_fields = CustomField.objects.filter(content_types=content_type)
        return self._custom_fields

    def to_representation(self, obj):
        # TODO: Fix circular import
        from utilities.api import get_serializer_for_model
        data = {}
        for cf in self._get_custom_fields():
            value = cf.deserialize(obj.get(cf.name))
            if value is not None and cf.type == CustomFieldTypeChoices.TYPE_OBJECT:
                serializer = get_serializer_for_model(cf.object_type.model_class(), prefix='Nested')
                value = serializer(value, context=self.parent.context).data
            data[cf.name] = value

        return data

    def to_internal_value(self, data):
        # If updating an existing instance, start with existing custom_field_data
        if self.parent.instance:
            data = {**self.parent.instance.custom_field_data, **data}

        return data
