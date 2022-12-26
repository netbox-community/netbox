from django.utils.translation import gettext as _

from netbox.forms import NetBoxModelFilterSetForm
from tenancy.models import *
from tenancy.forms import ContactModelFilterForm
from utilities.forms import DynamicModelMultipleChoiceField, TagFilterField

__all__ = (
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
