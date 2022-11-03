from django.utils.translation import gettext as _
from netbox.forms import NetBoxModelCSVForm
from tenancy.models import *
from utilities.forms import CSVModelChoiceField, SlugField

__all__ = (
    'ContactCSVForm',
    'ContactGroupCSVForm',
    'ContactRoleCSVForm',
    'TenantCSVForm',
    'TenantGroupCSVForm',
)


#
# Tenants
#

class TenantGroupCSVForm(NetBoxModelCSVForm):
    parent = CSVModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Parent group')
    )
    slug = SlugField()

    class Meta:
        model = TenantGroup
        fields = ('name', 'slug', 'parent', 'description', 'tags')


class TenantCSVForm(NetBoxModelCSVForm):
    slug = SlugField()
    group = CSVModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned group')
    )

    class Meta:
        model = Tenant
        fields = ('name', 'slug', 'group', 'description', 'comments', 'tags')


#
# Contacts
#

class ContactGroupCSVForm(NetBoxModelCSVForm):
    parent = CSVModelChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Parent group')
    )
    slug = SlugField()

    class Meta:
        model = ContactGroup
        fields = ('name', 'slug', 'parent', 'description', 'tags')


class ContactRoleCSVForm(NetBoxModelCSVForm):
    slug = SlugField()

    class Meta:
        model = ContactRole
        fields = ('name', 'slug', 'description')


class ContactCSVForm(NetBoxModelCSVForm):
    group = CSVModelChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned group')
    )

    class Meta:
        model = Contact
        fields = ('name', 'title', 'phone', 'email', 'address', 'link', 'group', 'description', 'comments', 'tags')
