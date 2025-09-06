from django import forms
from django.utils.translation import gettext_lazy as _

from netbox.forms import NetBoxModelBulkEditForm
from tenancy.choices import ContactPriorityChoices
from tenancy.models import *
from utilities.forms import add_blank_choice
from utilities.forms.fields import CommentField, DynamicModelChoiceField, DynamicModelMultipleChoiceField
from utilities.forms.rendering import FieldSet

__all__ = (
    'ContactAssignmentBulkEditForm',
    'ContactBulkEditForm',
    'ContactGroupBulkEditForm',
    'ContactRoleBulkEditForm',
    'TenantBulkEditForm',
    'TenantGroupBulkEditForm',
)


#
# Tenants
#

class TenantGroupBulkEditForm(NetBoxModelBulkEditForm):
    parent = DynamicModelChoiceField(
        label=_('Parent'),
        queryset=TenantGroup.objects.all(),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = TenantGroup
    nullable_fields = ('parent', 'description', 'comments')


class TenantBulkEditForm(NetBoxModelBulkEditForm):
    group = DynamicModelChoiceField(
        label=_('Group'),
        queryset=TenantGroup.objects.all(),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )

    model = Tenant
    fieldsets = (
        FieldSet('group', 'description'),
    )
    nullable_fields = ('group', 'description')


#
# Contacts
#

class ContactGroupBulkEditForm(NetBoxModelBulkEditForm):
    parent = DynamicModelChoiceField(
        label=_('Parent'),
        queryset=ContactGroup.objects.all(),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = ContactGroup
    fieldsets = (
        FieldSet('parent', 'description'),
    )
    nullable_fields = ('parent', 'description', 'comments')


class ContactRoleBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )

    model = ContactRole
    fieldsets = (
        FieldSet('description'),
    )
    nullable_fields = ('description',)


class ContactBulkEditForm(NetBoxModelBulkEditForm):
    add_groups = DynamicModelMultipleChoiceField(
        label=_('Add groups'),
        queryset=ContactGroup.objects.all(),
        required=False
    )
    remove_groups = DynamicModelMultipleChoiceField(
        label=_('Remove groups'),
        queryset=ContactGroup.objects.all(),
        required=False
    )
    title = forms.CharField(
        label=_('Title'),
        max_length=100,
        required=False
    )
    phone = forms.CharField(
        label=_('Phone'),
        max_length=50,
        required=False
    )
    email = forms.EmailField(
        label=_('Email'),
        required=False
    )
    address = forms.CharField(
        label=_('Address'),
        max_length=200,
        required=False
    )
    link = forms.URLField(
        label=_('Link'),
        assume_scheme='https',
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = Contact
    fieldsets = (
        FieldSet('title', 'phone', 'email', 'address', 'link', 'description'),
        FieldSet('add_groups', 'remove_groups', name=_('Groups')),
    )

    nullable_fields = (
        'add_groups', 'remove_groups', 'title', 'phone', 'email', 'address', 'link', 'description', 'comments'
    )


class ContactAssignmentBulkEditForm(NetBoxModelBulkEditForm):
    contact = DynamicModelChoiceField(
        label=_('Contact'),
        queryset=Contact.objects.all(),
        required=False
    )
    role = DynamicModelChoiceField(
        label=_('Role'),
        queryset=ContactRole.objects.all(),
        required=False
    )
    priority = forms.ChoiceField(
        label=_('Priority'),
        choices=add_blank_choice(ContactPriorityChoices),
        required=False
    )

    model = ContactAssignment
    fieldsets = (
        FieldSet('contact', 'role', 'priority'),
    )
    nullable_fields = ('priority',)
