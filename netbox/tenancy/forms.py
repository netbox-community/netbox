from django import forms
from django.utils.translation import gettext as _

from extras.forms import (
    AddRemoveTagsForm, CustomFieldModelForm, CustomFieldModelBulkEditForm, CustomFieldModelFilterForm, CustomFieldModelCSVForm,
)
from extras.models import Tag
from utilities.forms import (
    BootstrapMixin, CommentField, CSVModelChoiceField, DynamicModelChoiceField, DynamicModelMultipleChoiceField,
    SlugField, TagFilterField,
)
from .models import Tenant, TenantGroup


#
# Tenant groups
#

class TenantGroupForm(BootstrapMixin, CustomFieldModelForm):
    parent = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False
    )
    slug = SlugField()

    class Meta:
        model = TenantGroup
        fields = [
            'parent', 'name', 'slug', 'description',
        ]


class TenantGroupCSVForm(CustomFieldModelCSVForm):
    parent = CSVModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Parent group'
    )
    slug = SlugField()

    class Meta:
        model = TenantGroup
        fields = ('name', 'slug', 'parent', 'description')


class TenantGroupBulkEditForm(BootstrapMixin, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    parent = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    class Meta:
        nullable_fields = ['parent', 'description']


#
# Tenants
#

class TenantForm(BootstrapMixin, CustomFieldModelForm):
    slug = SlugField()
    group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Tenant
        fields = (
            'name', 'slug', 'group', 'description', 'comments', 'tags',
        )
        fieldsets = (
            ('Tenant', ('name', 'slug', 'group', 'description', 'tags')),
        )


class TenantCSVForm(CustomFieldModelCSVForm):
    slug = SlugField()
    group = CSVModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned group'
    )

    class Meta:
        model = Tenant
        fields = ('name', 'slug', 'group', 'description', 'comments')


class TenantBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False
    )

    class Meta:
        nullable_fields = [
            'group',
        ]


class TenantFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = Tenant
    q = forms.CharField(
        required=False,
        label=_('Search')
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        null_option='None',
        label=_('Group')
    )
    tag = TagFilterField(model)


#
# Form extensions
#

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
