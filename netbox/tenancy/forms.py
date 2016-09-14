from django import forms

from extras.forms import CustomFieldForm, CustomFieldBulkEditForm, CustomFieldFilterForm
from utilities.forms import (
    BootstrapMixin, BulkImportForm, CommentField, CSVDataField, FilterChoiceField, SlugField, get_filter_choices,
)

from .models import Tenant, TenantGroup


def bulkedit_tenantgroup_choices():
    """
    Include an option to remove the currently assigned TenantGroup from a Tenant.
    """
    choices = [
        (None, '---------'),
        (0, 'None'),
    ]
    choices += [(g.pk, g.name) for g in TenantGroup.objects.all()]
    return choices


def bulkedit_tenant_choices():
    """
    Include an option to remove the currently assigned Tenant from an object.
    """
    choices = [
        (None, '---------'),
        (0, 'None'),
    ]
    choices += [(t.pk, t.name) for t in Tenant.objects.all()]
    return choices


#
# Tenant groups
#

class TenantGroupForm(forms.ModelForm, BootstrapMixin):
    slug = SlugField()

    class Meta:
        model = TenantGroup
        fields = ['name', 'slug']


#
# Tenants
#

class TenantForm(BootstrapMixin, CustomFieldForm):
    slug = SlugField()
    comments = CommentField()

    class Meta:
        model = Tenant
        fields = ['name', 'slug', 'group', 'description', 'comments']


class TenantFromCSVForm(forms.ModelForm):
    group = forms.ModelChoiceField(TenantGroup.objects.all(), required=False, to_field_name='name',
                                   error_messages={'invalid_choice': 'Group not found.'})

    class Meta:
        model = Tenant
        fields = ['name', 'slug', 'group', 'description']


class TenantImportForm(BulkImportForm, BootstrapMixin):
    csv = CSVDataField(csv_form=TenantFromCSVForm)


class TenantBulkEditForm(BootstrapMixin, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=Tenant.objects.all(), widget=forms.MultipleHiddenInput)
    group = forms.TypedChoiceField(choices=bulkedit_tenantgroup_choices, coerce=int, required=False, label='Group')


class TenantFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Tenant
    group = FilterChoiceField(choices=get_filter_choices(TenantGroup, id_field='slug', count_field='tenants'))
