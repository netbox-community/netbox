from django import forms

from netbox.forms import NetBoxModelBulkEditForm
from tenancy.choices import ContactPriorityChoices
from tenancy.models import *
from utilities.forms import add_blank_choice
from utilities.forms.fields import CommentField, DynamicModelChoiceField

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
        queryset=TenantGroup.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    model = TenantGroup
    nullable_fields = ('parent', 'description')


class TenantBulkEditForm(NetBoxModelBulkEditForm):
    group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False
    )

    model = Tenant
    fieldsets = (
        (None, ('group',)),
    )
    nullable_fields = ('group',)


#
# Contacts
#

class ContactGroupBulkEditForm(NetBoxModelBulkEditForm):
    parent = DynamicModelChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    model = ContactGroup
    fieldsets = (
        (None, ('parent', 'description')),
    )
    nullable_fields = ('parent', 'description')


class ContactRoleBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(
        max_length=200,
        required=False
    )

    model = ContactRole
    fieldsets = (
        (None, ('description',)),
    )
    nullable_fields = ('description',)


class ContactBulkEditForm(NetBoxModelBulkEditForm):
    group = DynamicModelChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False
    )
    title = forms.CharField(
        max_length=100,
        required=False
    )
    phone = forms.CharField(
        max_length=50,
        required=False
    )
    email = forms.EmailField(
        required=False
    )
    address = forms.CharField(
        max_length=200,
        required=False
    )
    link = forms.URLField(
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = Contact
    fieldsets = (
        (None, ('group', 'title', 'phone', 'email', 'address', 'link', 'description')),
    )
    nullable_fields = ('group', 'title', 'phone', 'email', 'address', 'link', 'description', 'comments')


class ContactAssignmentBulkEditForm(NetBoxModelBulkEditForm):
    contact = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        required=False
    )
    role = DynamicModelChoiceField(
        queryset=ContactRole.objects.all(),
        required=False
    )
    priority = forms.ChoiceField(
        choices=add_blank_choice(ContactPriorityChoices),
        required=False
    )

    model = ContactAssignment
    fieldsets = (
        (None, ('contact', 'role', 'priority')),
    )
    nullable_fields = ('priority',)
