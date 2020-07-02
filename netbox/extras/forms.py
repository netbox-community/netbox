from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from mptt.forms import TreeNodeMultipleChoiceField
from taggit.forms import TagField as TagField_

from dcim.models import DeviceRole, Platform, Region, Site
from tenancy.models import Tenant, TenantGroup
from utilities.forms import (
    add_blank_choice, APISelectMultiple, BootstrapMixin, BulkEditForm, BulkEditNullBooleanSelect, ColorSelect,
    ContentTypeSelect, CSVModelForm, DateTimePicker, DynamicModelMultipleChoiceField, JSONField, SlugField,
    StaticSelect2, StaticSelect2Multiple, BOOLEAN_WITH_BLANK_CHOICES,
)
from virtualization.models import Cluster, ClusterGroup
from .choices import *
from .models import ConfigContext, CustomField, CustomFieldValue, ImageAttachment, ObjectChange, Tag


#
# Custom fields
#

class CustomFieldModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        self.obj_type = ContentType.objects.get_for_model(self._meta.model)
        self.custom_fields = []
        self.custom_field_values = {}

        super().__init__(*args, **kwargs)

        self._append_customfield_fields()

    def _append_customfield_fields(self):
        """
        Append form fields for all CustomFields assigned to this model.
        """
        # Retrieve initial CustomField values for the instance
        if self.instance.pk:
            for cfv in CustomFieldValue.objects.filter(
                obj_type=self.obj_type,
                obj_id=self.instance.pk
            ).prefetch_related('field'):
                self.custom_field_values[cfv.field.name] = cfv.serialized_value

        # Append form fields; assign initial values if modifying and existing object
        for cf in CustomField.objects.filter(obj_type=self.obj_type):
            field_name = 'cf_{}'.format(cf.name)
            if self.instance.pk:
                self.fields[field_name] = cf.to_form_field(set_initial=False)
                self.fields[field_name].initial = self.custom_field_values.get(cf.name)
            else:
                self.fields[field_name] = cf.to_form_field()

            # Annotate the field in the list of CustomField form fields
            self.custom_fields.append(field_name)

    def _save_custom_fields(self):

        for field_name in self.custom_fields:
            try:
                cfv = CustomFieldValue.objects.prefetch_related('field').get(
                    field=self.fields[field_name].model,
                    obj_type=self.obj_type,
                    obj_id=self.instance.pk
                )
            except CustomFieldValue.DoesNotExist:
                # Skip this field if none exists already and its value is empty
                if self.cleaned_data[field_name] in [None, '']:
                    continue
                cfv = CustomFieldValue(
                    field=self.fields[field_name].model,
                    obj_type=self.obj_type,
                    obj_id=self.instance.pk
                )
            cfv.value = self.cleaned_data[field_name]
            cfv.save()

    def save(self, commit=True):
        obj = super().save(commit)

        # Handle custom fields the same way we do M2M fields
        if commit:
            self._save_custom_fields()
        else:
            self.save_custom_fields = self._save_custom_fields

        return obj


class CustomFieldModelCSVForm(CSVModelForm, CustomFieldModelForm):

    def _append_customfield_fields(self):

        # Append form fields
        for cf in CustomField.objects.filter(obj_type=self.obj_type):
            field_name = 'cf_{}'.format(cf.name)
            self.fields[field_name] = cf.to_form_field(for_csv_import=True)

            # Annotate the field in the list of CustomField form fields
            self.custom_fields.append(field_name)


class CustomFieldBulkEditForm(BulkEditForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.custom_fields = []
        self.obj_type = ContentType.objects.get_for_model(self.model)

        # Add all applicable CustomFields to the form
        custom_fields = CustomField.objects.filter(obj_type=self.obj_type)
        for cf in custom_fields:
            # Annotate non-required custom fields as nullable
            if not cf.required:
                self.nullable_fields.append(cf.name)
            self.fields[cf.name] = cf.to_form_field(set_initial=False, enforce_required=False)
            # Annotate this as a custom field
            self.custom_fields.append(cf.name)


class CustomFieldFilterForm(forms.Form):

    def __init__(self, *args, **kwargs):

        self.obj_type = ContentType.objects.get_for_model(self.model)

        super().__init__(*args, **kwargs)

        # Add all applicable CustomFields to the form
        custom_fields = CustomField.objects.filter(obj_type=self.obj_type).exclude(
            filter_logic=CustomFieldFilterLogicChoices.FILTER_DISABLED
        )
        for cf in custom_fields:
            field_name = 'cf_{}'.format(cf.name)
            self.fields[field_name] = cf.to_form_field(set_initial=True, enforce_required=False)


#
# Tags
#

class TagField(TagField_):

    def widget_attrs(self, widget):
        # Apply the "tagfield" CSS class to trigger the special API-based selection widget for tags
        return {
            'class': 'tagfield'
        }


class TagForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = Tag
        fields = [
            'name', 'slug', 'color', 'description'
        ]


class AddRemoveTagsForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add add/remove tags fields
        self.fields['add_tags'] = DynamicModelMultipleChoiceField(
            queryset=Tag.objects.all(),
            required=False
        )
        self.fields['remove_tags'] = DynamicModelMultipleChoiceField(
            queryset=Tag.objects.all(),
            required=False
        )


class TagFilterForm(BootstrapMixin, forms.Form):
    model = Tag
    q = forms.CharField(
        required=False,
        label='Search'
    )


class TagBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    color = forms.CharField(
        max_length=6,
        required=False,
        widget=ColorSelect()
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    class Meta:
        nullable_fields = ['description']


#
# Config contexts
#

class ConfigContextForm(BootstrapMixin, forms.ModelForm):
    regions = TreeNodeMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        widget=StaticSelect2Multiple()
    )
    sites = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    roles = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False
    )
    platforms = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        required=False
    )
    cluster_groups = DynamicModelMultipleChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False
    )
    clusters = DynamicModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        required=False
    )
    tenant_groups = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False
    )
    tenants = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )
    data = JSONField(
        label=''
    )

    class Meta:
        model = ConfigContext
        fields = (
            'name', 'weight', 'description', 'is_active', 'regions', 'sites', 'roles', 'platforms', 'cluster_groups',
            'clusters', 'tenant_groups', 'tenants', 'tags', 'data',
        )


class ConfigContextBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ConfigContext.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    weight = forms.IntegerField(
        required=False,
        min_value=0
    )
    is_active = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    description = forms.CharField(
        required=False,
        max_length=100
    )

    class Meta:
        nullable_fields = [
            'description',
        ]


class ConfigContextFilterForm(BootstrapMixin, forms.Form):
    q = forms.CharField(
        required=False,
        label='Search'
    )
    region = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
        )
    )
    site = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
        )
    )
    role = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
        )
    )
    platform = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
        )
    )
    cluster_group = DynamicModelMultipleChoiceField(
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
        )
    )
    cluster_id = DynamicModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        label='Cluster'
    )
    tenant_group = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
        )
    )
    tenant = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
        )
    )
    tag = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
        )
    )


#
# Filter form for local config context data
#

class LocalConfigContextFilterForm(forms.Form):
    local_context_data = forms.NullBooleanField(
        required=False,
        label='Has local config context data',
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


#
# Image attachments
#

class ImageAttachmentForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = ImageAttachment
        fields = [
            'name', 'image',
        ]


#
# Change logging
#

class ObjectChangeFilterForm(BootstrapMixin, forms.Form):
    model = ObjectChange
    q = forms.CharField(
        required=False,
        label='Search'
    )
    time_after = forms.DateTimeField(
        label='After',
        required=False,
        widget=DateTimePicker()
    )
    time_before = forms.DateTimeField(
        label='Before',
        required=False,
        widget=DateTimePicker()
    )
    action = forms.ChoiceField(
        choices=add_blank_choice(ObjectChangeActionChoices),
        required=False,
        widget=StaticSelect2()
    )
    # TODO: Convert to DynamicModelMultipleChoiceField once we have an API endpoint for users
    user = forms.ModelChoiceField(
        queryset=User.objects.order_by('username'),
        required=False,
        widget=StaticSelect2()
    )
    changed_object_type = forms.ModelChoiceField(
        queryset=ContentType.objects.order_by('model'),
        required=False,
        widget=ContentTypeSelect(),
        label='Object Type'
    )


#
# Scripts
#

class ScriptForm(BootstrapMixin, forms.Form):
    _commit = forms.BooleanField(
        required=False,
        initial=True,
        label="Commit changes",
        help_text="Commit changes to the database (uncheck for a dry-run)"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Move _commit to the end of the form
        commit = self.fields.pop('_commit')
        self.fields['_commit'] = commit

    @property
    def requires_input(self):
        """
        A boolean indicating whether the form requires user input (ignore the _commit field).
        """
        return bool(len(self.fields) > 1)
