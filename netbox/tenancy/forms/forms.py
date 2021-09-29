from django import forms
from django.utils.translation import gettext as _

from tenancy.models import Tenant, TenantGroup
from utilities.forms import DynamicModelChoiceField, DynamicModelMultipleChoiceField

__all__ = (
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
        label=_('Tenant group'),
        fetch_trigger='open'
    )
    tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'group_id': '$tenant_group_id'
        },
        label=_('Tenant'),
        fetch_trigger='open'
    )
