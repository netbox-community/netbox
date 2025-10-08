from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from netbox.forms import NetBoxModelImportForm
from tenancy.models import *
from utilities.forms.fields import CSVContentTypeField, CSVModelChoiceField, CSVModelMultipleChoiceField, SlugField

__all__ = (
    'ContactAssignmentImportForm',
    'ContactImportForm',
    'ContactGroupImportForm',
    'ContactRoleImportForm',
    'TenantImportForm',
    'TenantGroupImportForm',
)


#
# Tenants
#

class TenantGroupImportForm(NetBoxModelImportForm):
    parent = CSVModelChoiceField(
        label=_('Parent'),
        queryset=TenantGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Parent group'),
    )
    slug = SlugField()

    class Meta:
        model = TenantGroup
        fields = ('name', 'slug', 'parent', 'description', 'tags', 'comments')


class TenantImportForm(NetBoxModelImportForm):
    slug = SlugField()
    group = CSVModelChoiceField(
        label=_('Group'),
        queryset=TenantGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned group'),
    )

    class Meta:
        model = Tenant
        fields = ('name', 'slug', 'group', 'description', 'comments', 'tags')


#
# Contacts
#

class ContactGroupImportForm(NetBoxModelImportForm):
    parent = CSVModelChoiceField(
        label=_('Parent'),
        queryset=ContactGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Parent group'),
    )
    slug = SlugField()

    class Meta:
        model = ContactGroup
        fields = ('name', 'slug', 'parent', 'description', 'tags', 'comments')


class ContactRoleImportForm(NetBoxModelImportForm):
    slug = SlugField()

    class Meta:
        model = ContactRole
        fields = ('name', 'slug', 'description')


class ContactImportForm(NetBoxModelImportForm):
    groups = CSVModelMultipleChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Group names separated by commas, encased with double quotes (e.g. "Group 1,Group 2")'),
    )
    link = forms.URLField(
        label=_('Link'),
        assume_scheme='https',
        required=False,
    )

    class Meta:
        model = Contact
        fields = ('name', 'title', 'phone', 'email', 'address', 'link', 'groups', 'description', 'comments', 'tags')


class ContactAssignmentImportForm(NetBoxModelImportForm):
    object_type = CSVContentTypeField(
        queryset=ContentType.objects.all(),
        help_text=_("One or more assigned object types")
    )
    contact = CSVModelChoiceField(
        queryset=Contact.objects.all(),
        to_field_name='name',
        help_text=_('Assigned contact')
    )
    role = CSVModelChoiceField(
        queryset=ContactRole.objects.all(),
        to_field_name='name',
        help_text=_('Assigned role')
    )

    class Meta:
        model = ContactAssignment
        fields = ('object_type', 'object_id', 'contact', 'priority', 'role')
