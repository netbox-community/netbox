from django import forms
from django.utils.translation import gettext_lazy as _

from core.models import ObjectType
from extras.choices import *
from extras.models import Tag
from netbox.models.features import ContactsMixin
from tenancy.choices import ContactPriorityChoices
from tenancy.models import Contact, ContactRole
from utilities.forms import BulkEditForm, add_blank_choice
from utilities.forms.fields import CommentField, DynamicModelChoiceField, DynamicModelMultipleChoiceField

from .mixins import ChangelogMessageMixin, CustomFieldsMixin, OwnerMixin

__all__ = (
    'NestedGroupModelBulkEditForm',
    'NetBoxModelBulkEditForm',
    'OrganizationalModelBulkEditForm',
    'PrimaryModelBulkEditForm',
)


class NetBoxModelBulkEditForm(ChangelogMessageMixin, CustomFieldsMixin, BulkEditForm):
    """
    Base form for modifying multiple NetBox objects (of the same type) in bulk via the UI. Adds support for custom
    fields, adding/removing tags, and adding/removing contact assignments (for models which support contacts).

    Attributes:
        fieldsets: An iterable of two-tuples which define a heading and field set to display per section of
            the rendered form (optional). If not defined, the all fields will be rendered as a single section.
    """
    fieldsets = None

    pk = forms.ModelMultipleChoiceField(
        queryset=None,  # Set from self.model on init
        widget=forms.MultipleHiddenInput
    )
    add_tags = DynamicModelMultipleChoiceField(
        label=_('Add tags'),
        queryset=Tag.objects.all(),
        required=False
    )
    remove_tags = DynamicModelMultipleChoiceField(
        label=_('Remove tags'),
        queryset=Tag.objects.all(),
        required=False
    )
    add_contacts = DynamicModelMultipleChoiceField(
        label=_('Add contacts'),
        queryset=Contact.objects.all(),
        required=False
    )
    contact_role = DynamicModelChoiceField(
        label=_('Role'),
        queryset=ContactRole.objects.all(),
        required=False,
        help_text=_('Role to assign to added contacts')
    )
    contact_priority = forms.ChoiceField(
        label=_('Priority'),
        choices=add_blank_choice(ContactPriorityChoices),
        required=False,
        help_text=_('Priority to assign to added contacts')
    )
    remove_contacts = DynamicModelMultipleChoiceField(
        label=_('Remove contacts'),
        queryset=Contact.objects.all(),
        required=False,
        help_text=_('Removes all assignments of these contacts, regardless of role')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['pk'].queryset = self.model.objects.all()

        # Restrict tag fields by model
        object_type = ObjectType.objects.get_for_model(self.model)
        self.fields['add_tags'].widget.add_query_param('for_object_type_id', object_type.pk)
        self.fields['remove_tags'].widget.add_query_param('for_object_type_id', object_type.pk)

        # Contact fields apply only to models which support contact assignment
        if not issubclass(self.model, ContactsMixin):
            for name in ('add_contacts', 'contact_role', 'contact_priority', 'remove_contacts'):
                del self.fields[name]

        self._extend_nullable_fields()

    def clean(self):
        super().clean()

        if self.cleaned_data.get('add_contacts') and not self.cleaned_data.get('contact_role'):
            raise forms.ValidationError({
                'contact_role': _('A role must be specified when adding contacts.')
            })

        return self.cleaned_data

    def _get_form_field(self, customfield):
        return customfield.to_form_field(set_initial=False, enforce_required=False)

    def _extend_nullable_fields(self):
        # The bulk edit template always renders a Set Null control for these
        nullable_common_fields = [
            name for name in ('owner', 'comments')
            if name in self.fields and name not in self.nullable_fields
        ]
        nullable_custom_fields = [
            name for name, customfield in self.custom_fields.items()
            if (not customfield.required and customfield.ui_editable == CustomFieldUIEditableChoices.YES)
        ]
        self.nullable_fields = (
            *self.nullable_fields,
            *nullable_common_fields,
            *nullable_custom_fields,
        )


class PrimaryModelBulkEditForm(OwnerMixin, NetBoxModelBulkEditForm):
    """
    Bulk edit form for models which inherit from PrimaryModel.
    """
    description = forms.CharField(
        label=_('Description'),
        max_length=100,
        required=False
    )
    comments = CommentField()


class OrganizationalModelBulkEditForm(OwnerMixin, NetBoxModelBulkEditForm):
    """
    Bulk edit form for models which inherit from OrganizationalModel.
    """
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()


class NestedGroupModelBulkEditForm(OwnerMixin, NetBoxModelBulkEditForm):
    """
    Bulk edit form for models which inherit from NestedGroupModel.
    """
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()
