from django import forms

from netbox.forms import NetBoxModelBulkEditForm
from tenancy.models import *
from utilities.forms import DynamicModelChoiceField

__all__ = (
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
    pk = forms.ModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    parent = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    nullable_fields = ('parent', 'description')


class TenantBulkEditForm(NetBoxModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False
    )

    nullable_fields = ('group',)


#
# Contacts
#

class ContactGroupBulkEditForm(NetBoxModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ContactGroup.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    parent = DynamicModelChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    nullable_fields = ('parent', 'description')


class ContactRoleBulkEditForm(NetBoxModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ContactRole.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    nullable_fields = ('description',)


class ContactBulkEditForm(NetBoxModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Contact.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
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

    nullable_fields = ('group', 'title', 'phone', 'email', 'address', 'comments')
