from extras.forms import CustomFieldModelForm
from extras.models import Tag
from tenancy.models import *
from utilities.forms import (
    BootstrapMixin, CommentField, DynamicModelChoiceField, DynamicModelMultipleChoiceField, SlugField, SmallTextarea,
)

__all__ = (
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

    class Meta:
        model = TenantGroup
        fields = [
            'parent', 'name', 'slug', 'description',
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

    class Meta:
        model = ContactGroup
        fields = ['parent', 'name', 'slug', 'description']


class ContactRoleForm(BootstrapMixin, CustomFieldModelForm):
    slug = SlugField()

    class Meta:
        model = ContactRole
        fields = ['name', 'slug', 'description']


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
