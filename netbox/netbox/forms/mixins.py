from django import forms
from django.utils.translation import gettext as _

from core.models import ObjectType
from extras.choices import *
from extras.models import *
from users.models import Owner, OwnerGroup
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField

__all__ = (
    'ChangelogMessageMixin',
    'CustomFieldsMixin',
    'OwnerFilterMixin',
    'OwnerMixin',
    'SavedFiltersMixin',
    'TagsMixin',
)


class ChangelogMessageMixin(forms.Form):
    """
    Adds an optional field for recording a message on the resulting changelog record(s).
    """
    changelog_message = forms.CharField(
        required=False,
        max_length=200,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Declare changelog_message a meta field
        if hasattr(self, 'meta_fields'):
            self.meta_fields.append('changelog_message')
        else:
            self.meta_fields = ['changelog_message']


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
        # Return only custom fields that are not hidden from the UI
        return [
            cf for cf in CustomField.objects.get_for_model(content_type.model_class())
            if cf.ui_editable != CustomFieldUIEditableChoices.HIDDEN
        ]

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
    """
    Form mixin for forms that support saved filters.

    Provides a field for selecting a saved filter,
    with options limited to those applicable to the form's model.
    """

    filter_id = DynamicModelMultipleChoiceField(
        queryset=SavedFilter.objects.all(),
        required=False,
        label=_('Saved Filter'),
        query_params={
            'usable': True,
        },
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit saved filters to those applicable to the form's model
        if hasattr(self, 'model'):
            object_type = ObjectType.objects.get_for_model(self.model)
            self.fields['filter_id'].widget.add_query_params({
                'object_type_id': object_type.pk,
            })


class TagsMixin(forms.Form):
    """
    Mixin for forms that support tagging.

    Provides a field for selecting tags,
    with options limited to those applicable to the form's model.
    """

    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label=_('Tags'),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit tags to those applicable to the object type
        object_type = ObjectType.objects.get_for_model(self._meta.model)
        if object_type and hasattr(self.fields['tags'].widget, 'add_query_param'):
            self.fields['tags'].widget.add_query_param('for_object_type_id', object_type.pk)


class OwnerMixin(forms.Form):
    """
    Mixin for forms which adds ownership fields.

    Include this mixin in forms for models which
    support owner and/or owner group assignment.
    """

    owner_group = DynamicModelChoiceField(
        label=_('Owner group'),
        queryset=OwnerGroup.objects.all(),
        required=False,
        null_option='None',
        initial_params={'members': '$owner'},
    )
    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        query_params={'group_id': '$owner_group'},
        label=_('Owner'),
    )


class OwnerFilterMixin(forms.Form):
    """
    Mixin for filterset forms which adds owner and owner group filtering.

    Include this mixin in filterset forms for models
    which support owner and/or owner group assignment.
    """

    owner_group_id = DynamicModelMultipleChoiceField(
        queryset=OwnerGroup.objects.all(),
        required=False,
        null_option='None',
        label=_('Owner Group'),
    )
    owner_id = DynamicModelMultipleChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'group_id': '$owner_group_id'
        },
        label=_('Owner'),
    )
