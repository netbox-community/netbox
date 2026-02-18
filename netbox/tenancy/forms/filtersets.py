from django import forms
from django.utils.translation import gettext_lazy as _

from core.models import ObjectType
from netbox.forms import (
    NestedGroupModelFilterSetForm,
    NetBoxModelFilterSetForm,
    OrganizationalModelFilterSetForm,
    PrimaryModelFilterSetForm,
)
from utilities.forms.fields import (
    ContentTypeMultipleChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet

from ..choices import *
from ..models import *
from .forms import ContactModelFilterForm

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

class TenantGroupFilterForm(NestedGroupModelFilterSetForm):
    model = TenantGroup
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('parent_id', name=_('Tenant Group')),
        FieldSet('owner_group_id', 'owner_id', name=_('Ownership')),
    )
    parent_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        label=_('Parent group')
    )
    tag = TagFilterField(model)


class TenantFilterForm(ContactModelFilterForm, PrimaryModelFilterSetForm):
    model = Tenant
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('group_id', name=_('Tenant')),
        FieldSet('owner_group_id', 'owner_id', name=_('Ownership')),
        FieldSet('contact', 'contact_role', 'contact_group', name=_('Contacts'))
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

class ContactGroupFilterForm(NestedGroupModelFilterSetForm):
    model = ContactGroup
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('parent_id', name=_('Contact Group')),
        FieldSet('owner_group_id', 'owner_id', name=_('Ownership')),
    )
    parent_id = DynamicModelMultipleChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        label=_('Parent group')
    )
    tag = TagFilterField(model)


class ContactRoleFilterForm(OrganizationalModelFilterSetForm):
    model = ContactRole
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('owner_group_id', 'owner_id', name=_('Ownership')),
    )
    tag = TagFilterField(model)


class ContactFilterForm(PrimaryModelFilterSetForm):
    model = Contact
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('group_id', name=_('Contact')),
        FieldSet('owner_group_id', 'owner_id', name=_('Ownership')),
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        null_option='None',
        label=_('Groups')
    )
    tag = TagFilterField(model)


class ContactAssignmentFilterForm(NetBoxModelFilterSetForm):
    model = ContactAssignment
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('object_type_id', 'group_id', 'contact_id', 'role_id', 'priority', name=_('Assignment')),
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
