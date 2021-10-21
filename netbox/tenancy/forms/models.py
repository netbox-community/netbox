from django import forms

from extras.forms import CustomFieldModelForm
from extras.models import Tag
from tenancy.models import *
from utilities.forms import (
    BootstrapMixin, CommentField, DynamicModelChoiceField, DynamicModelMultipleChoiceField, SlugField, SmallTextarea,
    StaticSelect,
)

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

class TenantGroupForm(BootstrapMixin, CustomFieldModelForm):
    parent = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False
    )
    slug = SlugField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = TenantGroup
        fields = [
            'parent', 'name', 'slug', 'description', 'tags',
        ]


class TenantForm(BootstrapMixin, CustomFieldModelForm):
    slug = SlugField()
    group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Tenant
        fields = (
            'name', 'slug', 'group', 'description', 'comments', 'tags',
        )
        fieldsets = (
            ('Tenant', ('name', 'slug', 'group', 'description', 'tags')),
        )


#
# Contacts
#

class ContactGroupForm(BootstrapMixin, CustomFieldModelForm):
    parent = DynamicModelChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False
    )
    slug = SlugField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = ContactGroup
        fields = ('parent', 'name', 'slug', 'description', 'tags')


class ContactRoleForm(BootstrapMixin, CustomFieldModelForm):
    slug = SlugField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = ContactRole
        fields = ('name', 'slug', 'description', 'tags')


class ContactForm(BootstrapMixin, CustomFieldModelForm):
    group = DynamicModelChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Contact
        fields = (
            'group', 'name', 'title', 'phone', 'email', 'address', 'comments', 'tags',
        )
        fieldsets = (
            ('Contact', ('group', 'name', 'title', 'phone', 'email', 'address', 'tags')),
        )
        widgets = {
            'address': SmallTextarea(attrs={'rows': 3}),
        }


class ContactAssignmentForm(BootstrapMixin, forms.ModelForm):
    group = DynamicModelChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        initial_params={
            'contacts': '$contact'
        }
    )
    contact = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        query_params={
            'group_id': '$group'
        }
    )
    role = DynamicModelChoiceField(
        queryset=ContactRole.objects.all()
    )

    class Meta:
        model = ContactAssignment
        fields = (
            'group', 'contact', 'role', 'priority',
        )
        widgets = {
            'priority': StaticSelect(),
        }
