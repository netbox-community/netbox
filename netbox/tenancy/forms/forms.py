from django import forms
from django.utils.translation import gettext as _

from tenancy.models import *
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField

__all__ = (
    'ContactModelFilterForm',
    'TenancyForm',
    'TenancyFilterForm',
)


class TenancyForm(forms.Form):
    tenant_group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        null_option='None',
        initial_params={
            'tenants': '$tenant'
        }
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        query_params={
            'group_id': '$tenant_group'
        }
    )


class TenancyFilterForm(forms.Form):
    tenant_group_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        null_option='None',
        label=_('Tenant group')
    )
    tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'group_id': '$tenant_group_id'
        },
        label=_('Tenant')
    )


class ContactModelFilterForm(forms.Form):
    contact = DynamicModelMultipleChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        label=_('Contact')
    )
    contact_role = DynamicModelMultipleChoiceField(
        queryset=ContactRole.objects.all(),
        required=False,
        label=_('Contact Role')
    )
    contact_group = DynamicModelMultipleChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        label=_('Contact Group')
    )
