from django import forms
from django.utils.translation import gettext as _

from extras.forms import CustomFieldModelFilterForm
from tenancy.models import *
from utilities.forms import BootstrapMixin, DynamicModelMultipleChoiceField, TagFilterField

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

class TenantGroupFilterForm(CustomFieldModelFilterForm):
    model = TenantGroup
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    parent_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        label=_('Parent group'),
        fetch_trigger='open'
    )
    tag = TagFilterField(model)


class TenantFilterForm(CustomFieldModelFilterForm):
    model = Tenant
    field_groups = (
        ('q', 'tag'),
        ('group_id',),
    )
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        null_option='None',
        label=_('Group'),
        fetch_trigger='open'
    )
    tag = TagFilterField(model)


#
# Contacts
#

class ContactGroupFilterForm(CustomFieldModelFilterForm):
    model = ContactGroup
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    parent_id = DynamicModelMultipleChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        label=_('Parent group'),
        fetch_trigger='open'
    )
    tag = TagFilterField(model)


class ContactRoleFilterForm(CustomFieldModelFilterForm):
    model = ContactRole
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    tag = TagFilterField(model)


class ContactFilterForm(CustomFieldModelFilterForm):
    model = Contact
    field_groups = (
        ('q', 'tag'),
        ('group_id',),
    )
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        null_option='None',
        label=_('Group'),
        fetch_trigger='open'
    )
    tag = TagFilterField(model)
