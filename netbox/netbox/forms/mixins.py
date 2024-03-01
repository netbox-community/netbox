from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _

from core.models import ObjectType
from extras.choices import *
from extras.models import *
from utilities.forms.fields import DynamicModelMultipleChoiceField

__all__ = (
    'CustomFieldsMixin',
    'SavedFiltersMixin',
    'TagsMixin',
)


class CustomFieldsMixin:
    """
    Extend a Form to include custom field support.

    Attributes:
        model: The model class
    """
    model = None

    def __init__(self, *args, **kwargs):
        self.custom_fields = {}
        self.custom_field_groups = {}

        super().__init__(*args, **kwargs)

        self._append_customfield_fields()

    def _get_content_type(self):
        """
        Return the ObjectType of the form's model.
        """
        if not getattr(self, 'model', None):
            raise NotImplementedError(_("{class_name} must specify a model class.").format(
                class_name=self.__class__.__name__
            ))
        return ObjectType.objects.get_for_model(self.model)

    def _get_custom_fields(self, content_type):
        return CustomField.objects.filter(object_types=content_type).exclude(
            ui_editable=CustomFieldUIEditableChoices.HIDDEN
        )

    def _get_form_field(self, customfield):
        return customfield.to_form_field()

    def _append_customfield_fields(self):
        """
        Append form fields for all CustomFields assigned to this object type.
        """
        for customfield in self._get_custom_fields(self._get_content_type()):
            field_name = f'cf_{customfield.name}'
            self.fields[field_name] = self._get_form_field(customfield)

            # Annotate the field in the list of CustomField form fields
            self.custom_fields[field_name] = customfield
            if customfield.group_name not in self.custom_field_groups:
                self.custom_field_groups[customfield.group_name] = []
            self.custom_field_groups[customfield.group_name].append(field_name)


class SavedFiltersMixin(forms.Form):
    filter_id = DynamicModelMultipleChoiceField(
        queryset=SavedFilter.objects.all(),
        required=False,
        label=_('Saved Filter'),
        query_params={
            'usable': True,
        }
    )


class TagsMixin(forms.Form):
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label=_('Tags'),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit tags to those applicable to the object type
        content_type = ContentType.objects.get_for_model(self._meta.model)
        if content_type and hasattr(self.fields['tags'].widget, 'add_query_param'):
            self.fields['tags'].widget.add_query_param('for_object_type_id', content_type.pk)
