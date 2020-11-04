from django import forms

from extras.forms import (
    AddRemoveTagsForm, CustomFieldModelForm, CustomFieldBulkEditForm, CustomFieldFilterForm, CustomFieldModelCSVForm,
)
from extras.models import Tag
from utilities.forms import (
    BootstrapMixin, CommentField, CSVModelChoiceField, CSVModelForm, DynamicModelChoiceField,
    DynamicModelMultipleChoiceField, SlugField, TagFilterField,
)
from .models import Tenant, TenantGroup


#
# Tenant groups
#

class TenantGroupForm(BootstrapMixin, forms.ModelForm):
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


class TenantGroupCSVForm(CSVModelForm):
    parent = CSVModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Parent group'
    )
    slug = SlugField()

    class Meta:
        model = TenantGroup
        fields = TenantGroup.csv_headers


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
        fields = Tenant.csv_headers


class TenantBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
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


class TenantFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Tenant
    q = forms.CharField(
        required=False,
        label='Search'
    )
    group = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        to_field_name='slug',
        required=False,
        null_option='None'
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
    tenant_group = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        to_field_name='slug',
        required=False,
        null_option='None'
    )
    tenant = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        required=False,
        null_option='None',
        query_params={
            'group': '$tenant_group'
        }
    )
