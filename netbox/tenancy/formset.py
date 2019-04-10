from django import forms
from utilities.forms import APISelectMultiple, FilterChoiceField
from .models import Tenant, TenantGroup

#
# Tenancy filtering form extension
#
class TenancyFilterForm(forms.Form):
    tenant_group = FilterChoiceField(
        queryset=TenantGroup.objects.all(),
        to_field_name='slug',
        null_label='-- None --',
        widget=APISelectMultiple(
            api_url="/api/tenancy/tenant-groups/",
            value_field="slug",
            null_option=True,
            filter_for={
                'tenant': 'group'
            }
        )
    )
    tenant = FilterChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        null_label='-- None --',
        widget=APISelectMultiple(
            api_url="/api/tenancy/tenants/",
            value_field="slug",
            null_option=True,
        )
    )