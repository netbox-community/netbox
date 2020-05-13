from django import forms

from extras.forms import (
    AddRemoveTagsForm, CustomFieldModelForm, CustomFieldBulkEditForm, CustomFieldFilterForm, CustomFieldModelCSVForm,
    TagField,
)
from utilities.forms import (
    APISelect, APISelectMultiple, BootstrapMixin, CommentField, CSVModelChoiceField, CSVModelForm,
    DynamicModelChoiceField, DynamicModelMultipleChoiceField, SlugField, TagFilterField,
)
from .models import Tenant, TenantGroup


#
# Tenant groups
#

class TenantGroupForm(BootstrapMixin, forms.ModelForm):
    parent = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/tenancy/tenant-groups/"
        )
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
    tags = TagField(
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
        widget=APISelectMultiple(
            value_field="slug",
            null_option=True,
        )
    )
    tag = TagFilterField(model)


#
# Form extensions
#

class TenancyForm(forms.Form):
    tenant_group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        widget=APISelect(
            filter_for={
                'tenant': 'group_id',
            },
            attrs={
                'nullable': 'true',
            }
        )
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )

    def __init__(self, *args, **kwargs):

        # Initialize helper selector
        instance = kwargs.get('instance')
        if instance and instance.tenant is not None:
            initial = kwargs.get('initial', {}).copy()
            initial['tenant_group'] = instance.tenant.group
            kwargs['initial'] = initial

        super().__init__(*args, **kwargs)


class TenancyFilterForm(forms.Form):
    tenant_group = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
            null_option=True,
            filter_for={
                'tenant': 'group'
            }
        )
    )
    tenant = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
            null_option=True,
        )
    )
