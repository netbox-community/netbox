from django import forms
from django.utils.translation import gettext_lazy as _

from core.models import ObjectType
from netbox.forms import NetBoxModelFilterSetForm
from tenancy.choices import *
from tenancy.models import *
from tenancy.forms import ContactModelFilterForm
from utilities.forms.fields import (
    ContentTypeMultipleChoiceField, DynamicModelMultipleChoiceField, TagFilterField,
)

__all__ = (
    'ContactAssignmentFilterForm',
    'ContactFilterForm',
    'ContactGroupFilterForm',
    'ContactRoleFilterForm',
    'TenantFilterForm',
    'TenantGroupFilterForm',
)


#
# Tenants
#

class TenantGroupFilterForm(NetBoxModelFilterSetForm):
    model = TenantGroup
    parent_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        label=_('Parent group')
    )
    tag = TagFilterField(model)


class TenantFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Tenant
    fieldsets = (
        (None, ('q', 'filter_id', 'tag', 'group_id')),
        ('Contacts', ('contact', 'contact_role', 'contact_group'))
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        null_option='None',
        label=_('Group')
    )
    tag = TagFilterField(model)


#
# Contacts
#

class ContactGroupFilterForm(NetBoxModelFilterSetForm):
    model = ContactGroup
    parent_id = DynamicModelMultipleChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        label=_('Parent group')
    )
    tag = TagFilterField(model)


class ContactRoleFilterForm(NetBoxModelFilterSetForm):
    model = ContactRole
    tag = TagFilterField(model)


class ContactFilterForm(NetBoxModelFilterSetForm):
    model = Contact
    group_id = DynamicModelMultipleChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        null_option='None',
        label=_('Group')
    )
    tag = TagFilterField(model)


class ContactAssignmentFilterForm(NetBoxModelFilterSetForm):
    model = ContactAssignment
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        (_('Assignment'), ('object_type_id', 'group_id', 'contact_id', 'role_id', 'priority')),
    )
    object_type_id = ContentTypeMultipleChoiceField(
        queryset=ObjectType.objects.with_feature('contacts'),
        required=False,
        label=_('Object type')
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        label=_('Group')
    )
    contact_id = DynamicModelMultipleChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        label=_('Contact')
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=ContactRole.objects.all(),
        required=False,
        label=_('Role')
    )
    priority = forms.MultipleChoiceField(
        label=_('Priority'),
        choices=ContactPriorityChoices,
        required=False
    )
    tag = TagFilterField(model)
