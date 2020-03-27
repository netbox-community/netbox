from django import forms
from taggit.forms import TagField

from extras.forms import (
    AddRemoveTagsForm, CustomFieldModelForm, CustomFieldBulkEditForm, CustomFieldFilterForm,
)
from utilities.forms import (
    APISelect, APISelectMultiple, BootstrapMixin, CommentField, DynamicModelChoiceField,
    DynamicModelMultipleChoiceField, SlugField, TagFilterField,
)
from .models import Tenant, TenantGroup


#
# Tenant groups
#

class TenantGroupForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = TenantGroup
        fields = [
            'name', 'slug',
        ]


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


class TenantCSVForm(CustomFieldModelForm):
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
