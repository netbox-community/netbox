from django import forms
from django.utils.translation import gettext_lazy as _

from netbox.forms import NetBoxModelBulkEditForm
from tenancy.choices import ContactPriorityChoices
from tenancy.models import *
from utilities.forms import add_blank_choice
from utilities.forms.fields import CommentField, DynamicModelChoiceField
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

    model = TenantGroup
    nullable_fields = ('parent', 'description')


class TenantBulkEditForm(NetBoxModelBulkEditForm):
    group = DynamicModelChoiceField(
        label=_('Group'),
        queryset=TenantGroup.objects.all(),
        required=False
    )

    model = Tenant
    fieldsets = (
        FieldSet('group'),
    )
    nullable_fields = ('group',)


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
        label=_('Desciption'),
        max_length=200,
        required=False
    )

    model = ContactGroup
    fieldsets = (
        FieldSet('parent', 'description'),
    )
    nullable_fields = ('parent', 'description')


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
    group = DynamicModelChoiceField(
        label=_('Group'),
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
        FieldSet('group', 'title', 'phone', 'email', 'address', 'link', 'description'),
    )
    nullable_fields = ('group', 'title', 'phone', 'email', 'address', 'link', 'description', 'comments')


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
