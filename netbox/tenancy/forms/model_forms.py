from django import forms
from django.utils.translation import gettext_lazy as _

from netbox.forms import NetBoxModelForm
from tenancy.models import *
from utilities.forms.fields import CommentField, DynamicModelChoiceField, SlugField
from utilities.forms.rendering import FieldSet, ObjectAttribute

__all__ = (
    'ContactAssignmentForm',
    'ContactForm',
    'ContactGroupForm',
    'ContactRoleForm',
    'TenantForm',
    'TenantGroupForm',
)


#
# Tenants
#

class TenantGroupForm(NetBoxModelForm):
    parent = DynamicModelChoiceField(
        label=_('Parent'),
        queryset=TenantGroup.objects.all(),
        required=False
    )
    slug = SlugField()

    fieldsets = (
        FieldSet('parent', 'name', 'slug', 'description', 'tags', name=_('Tenant Group')),
    )

    class Meta:
        model = TenantGroup
        fields = [
            'parent', 'name', 'slug', 'description', 'tags',
        ]


class TenantForm(NetBoxModelForm):
    slug = SlugField()
    group = DynamicModelChoiceField(
        label=_('Group'),
        queryset=TenantGroup.objects.all(),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        FieldSet('name', 'slug', 'group', 'description', 'tags', name=_('Tenant')),
    )

    class Meta:
        model = Tenant
        fields = (
            'name', 'slug', 'group', 'description', 'comments', 'tags',
        )


#
# Contacts
#

class ContactGroupForm(NetBoxModelForm):
    parent = DynamicModelChoiceField(
        label=_('Parent'),
        queryset=ContactGroup.objects.all(),
        required=False
    )
    slug = SlugField()

    fieldsets = (
        FieldSet('parent', 'name', 'slug', 'description', 'tags', name=_('Contact Group')),
    )

    class Meta:
        model = ContactGroup
        fields = ('parent', 'name', 'slug', 'description', 'tags')


class ContactRoleForm(NetBoxModelForm):
    slug = SlugField()

    fieldsets = (
        FieldSet('name', 'slug', 'description', 'tags', name=_('Contact Role')),
    )

    class Meta:
        model = ContactRole
        fields = ('name', 'slug', 'description', 'tags')


class ContactForm(NetBoxModelForm):
    group = DynamicModelChoiceField(
        label=_('Group'),
        queryset=ContactGroup.objects.all(),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        FieldSet(
            'group', 'name', 'title', 'phone', 'email', 'address', 'link', 'description', 'tags',
            name=_('Contact')
        ),
    )

    class Meta:
        model = Contact
        fields = (
            'group', 'name', 'title', 'phone', 'email', 'address', 'link', 'description', 'comments', 'tags',
        )
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class ContactAssignmentForm(NetBoxModelForm):
    group = DynamicModelChoiceField(
        label=_('Group'),
        queryset=ContactGroup.objects.all(),
        required=False,
        initial_params={
            'contacts': '$contact'
        }
    )
    contact = DynamicModelChoiceField(
        label=_('Contact'),
        queryset=Contact.objects.all(),
        query_params={
            'group_id': '$group'
        }
    )
    role = DynamicModelChoiceField(
        label=_('Role'),
        queryset=ContactRole.objects.all()
    )

    fieldsets = (
        FieldSet(ObjectAttribute('object'), 'group', 'contact', 'role', 'priority', 'tags'),
    )

    class Meta:
        model = ContactAssignment
        fields = (
            'object_type', 'object_id', 'group', 'contact', 'role', 'priority', 'tags'
        )
        widgets = {
            'object_type': forms.HiddenInput(),
            'object_id': forms.HiddenInput(),
        }
