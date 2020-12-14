from django.utils.encoding import force_str
from rest_framework.metadata import SimpleMetadata

from netbox.api import ContentTypeField


class ContentTypeMetadata(SimpleMetadata):

    def get_field_info(self, field):
        field_info = super().get_field_info(field)
        if hasattr(field, 'queryset') and not field_info.get('read_only') and isinstance(field, ContentTypeField):
            field_info['choices'] = [
                {
                    'value': choice_value,
                    'display_name': force_str(choice_name, strings_only=True)
                }
                for choice_value, choice_name in field.choices.items()
            ]
            field_info['choices'].sort(key=lambda item: item['display_name'])
        return field_info
