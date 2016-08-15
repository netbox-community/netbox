from django import forms
from django.db.models import Count

from extras.forms import CustomFieldForm
from utilities.forms import BootstrapMixin, BulkImportForm, CommentField, CSVDataField, SlugField

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


class TenantBulkEditForm(forms.Form, BootstrapMixin):
    pk = forms.ModelMultipleChoiceField(queryset=Tenant.objects.all(), widget=forms.MultipleHiddenInput)
    group = forms.TypedChoiceField(choices=bulkedit_tenantgroup_choices, coerce=int, required=False, label='Group')


def tenant_group_choices():
    group_choices = TenantGroup.objects.annotate(tenant_count=Count('tenants'))
    return [(g.slug, u'{} ({})'.format(g.name, g.tenant_count)) for g in group_choices]


class TenantFilterForm(forms.Form, BootstrapMixin):
    group = forms.MultipleChoiceField(required=False, choices=tenant_group_choices,
                                      widget=forms.SelectMultiple(attrs={'size': 8}))
