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

class TenantGroupFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
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


class TenantFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
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

class ContactGroupFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
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


class ContactRoleFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = ContactRole
    field_groups = [
        ['q'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )


class ContactFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
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
