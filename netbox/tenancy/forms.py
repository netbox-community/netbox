from __future__ import unicode_literals

from django import forms
from django.db.models import Count
from taggit.forms import TagField

from extras.forms import AddRemoveTagsForm, CustomFieldForm, CustomFieldBulkEditForm, CustomFieldFilterForm
from utilities.forms import (
    APISelect, BootstrapMixin, ChainedFieldsMixin, ChainedModelChoiceField, CommentField, FilterChoiceField, SlugField,
)
from .models import Tenant, TenantGroup


#
# Tenant groups
#

class TenantGroupForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = TenantGroup
        fields = ['name', 'slug']


class TenantGroupCSVForm(forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = TenantGroup
        fields = TenantGroup.csv_headers
        help_texts = {
            'name': 'Group name',
        }


#
# Tenants
#

class TenantForm(BootstrapMixin, CustomFieldForm):
    slug = SlugField()
    comments = CommentField()
    tags = TagField(required=False)

    class Meta:
        model = Tenant
        fields = ['name', 'slug', 'group', 'description', 'comments', 'tags']


class TenantCSVForm(forms.ModelForm):
    slug = SlugField()
    group = forms.ModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of parent group',
        error_messages={
            'invalid_choice': 'Group not found.'
        }
    )

    class Meta:
        model = Tenant
        fields = Tenant.csv_headers
        help_texts = {
            'name': 'Tenant name',
            'comments': 'Free-form comments'
        }


class TenantBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=Tenant.objects.all(), widget=forms.MultipleHiddenInput)
    group = forms.ModelChoiceField(queryset=TenantGroup.objects.all(), required=False)

    class Meta:
        nullable_fields = ['group']


class TenantFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Tenant
    q = forms.CharField(required=False, label='Search')
    group = FilterChoiceField(
        queryset=TenantGroup.objects.annotate(filter_count=Count('tenants')),
        to_field_name='slug',
        null_label='-- None --'
    )


#
# Tenancy form extension
#

class TenancyForm(ChainedFieldsMixin, forms.Form):
    tenant_group = forms.ModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={'filter-for': 'tenant', 'nullable': 'true'}
        )
    )
    tenant = ChainedModelChoiceField(
        queryset=Tenant.objects.all(),
        chains=(
            ('group', 'tenant_group'),
        ),
        required=False,
        widget=APISelect(
            api_url='/api/tenancy/tenants/?group_id={{tenant_group}}'
        )
    )

    def __init__(self, *args, **kwargs):

        # Initialize helper selector
        instance = kwargs.get('instance')
        if instance and instance.tenant is not None:
            initial = kwargs.get('initial', {}).copy()
            initial['tenant_group'] = instance.tenant.group
            kwargs['initial'] = initial

        super(TenancyForm, self).__init__(*args, **kwargs)
