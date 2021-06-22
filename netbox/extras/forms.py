from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from dcim.models import DeviceRole, DeviceType, Platform, Region, Site, SiteGroup
from tenancy.models import Tenant, TenantGroup
from utilities.forms import (
    add_blank_choice, APISelectMultiple, BootstrapMixin, BulkEditForm, BulkEditNullBooleanSelect, ColorField,
    CommentField, ContentTypeMultipleChoiceField, CSVModelForm, DateTimePicker, DynamicModelMultipleChoiceField,
    JSONField, SlugField, StaticSelect2, BOOLEAN_WITH_BLANK_CHOICES,
)
from virtualization.models import Cluster, ClusterGroup
from .choices import *
from .models import ConfigContext, CustomField, ImageAttachment, JournalEntry, ObjectChange, Tag
from .utils import FeatureQuery


#
# Custom fields
#

class CustomFieldsMixin:
    """
    Extend a Form to include custom field support.
    """
    def __init__(self, *args, **kwargs):
        self.custom_fields = []

        super().__init__(*args, **kwargs)

        self._append_customfield_fields()

    def _get_content_type(self):
        """
        Return the ContentType of the form's model.
        """
        if not hasattr(self, 'model'):
            raise NotImplementedError(f"{self.__class__.__name__} must specify a model class.")
        return ContentType.objects.get_for_model(self.model)

    def _get_form_field(self, customfield):
        return customfield.to_form_field()

    def _append_customfield_fields(self):
        """
        Append form fields for all CustomFields assigned to this object type.
        """
        content_type = self._get_content_type()

        # Append form fields; assign initial values if modifying and existing object
        for customfield in CustomField.objects.filter(content_types=content_type):
            field_name = f'cf_{customfield.name}'
            self.fields[field_name] = self._get_form_field(customfield)

            # Annotate the field in the list of CustomField form fields
            self.custom_fields.append(field_name)


class CustomFieldModelForm(CustomFieldsMixin, forms.ModelForm):
    """
    Extend ModelForm to include custom field support.
    """
    def _get_content_type(self):
        return ContentType.objects.get_for_model(self._meta.model)

    def _get_form_field(self, customfield):
        if self.instance.pk:
            form_field = customfield.to_form_field(set_initial=False)
            form_field.initial = self.instance.custom_field_data.get(customfield.name, None)
            return form_field

        return customfield.to_form_field()

    def clean(self):

        # Save custom field data on instance
        for cf_name in self.custom_fields:
            self.instance.custom_field_data[cf_name[3:]] = self.cleaned_data.get(cf_name)

        return super().clean()


class CustomFieldModelCSVForm(CSVModelForm, CustomFieldModelForm):

    def _get_form_field(self, customfield):
        return customfield.to_form_field(for_csv_import=True)


class CustomFieldBulkEditForm(BulkEditForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.custom_fields = []
        self.obj_type = ContentType.objects.get_for_model(self.model)

        # Add all applicable CustomFields to the form
        custom_fields = CustomField.objects.filter(content_types=self.obj_type)
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
        custom_fields = CustomField.objects.filter(content_types=self.obj_type).exclude(
            filter_logic=CustomFieldFilterLogicChoices.FILTER_DISABLED
        )
        for cf in custom_fields:
            field_name = 'cf_{}'.format(cf.name)
            self.fields[field_name] = cf.to_form_field(set_initial=True, enforce_required=False)


#
# Tags
#

class TagForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = Tag
        fields = [
            'name', 'slug', 'color', 'description'
        ]
        fieldsets = (
            ('Tag', ('name', 'slug', 'color', 'description')),
        )


class TagCSVForm(CSVModelForm):
    slug = SlugField()

    class Meta:
        model = Tag
        fields = ('name', 'slug', 'color', 'description')
        help_texts = {
            'color': mark_safe('RGB color in hexadecimal (e.g. <code>00ff00</code>)'),
        }


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
        label=_('Search')
    )
    content_type_id = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.filter(FeatureQuery('tags').get_query()),
        required=False,
        label=_('Tagged object type')
    )


class TagBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    color = ColorField(
        required=False
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
    regions = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False
    )
    site_groups = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False
    )
    sites = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    device_types = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
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
            'name', 'weight', 'description', 'is_active', 'regions', 'site_groups', 'sites', 'roles', 'device_types',
            'platforms', 'cluster_groups', 'clusters', 'tenant_groups', 'tenants', 'tags', 'data',
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
    field_order = [
        'region_id', 'site_group_id', 'site_id', 'role_id', 'platform_id', 'cluster_group_id', 'cluster_id',
        'tenant_group_id', 'tenant_id',
    ]
    field_groups = [
        ['region_id', 'site_group_id', 'site_id'],
        ['device_type_id', 'role_id', 'platform_id'],
        ['cluster_group_id', 'cluster_id'],
        ['tenant_group_id', 'tenant_id', 'tag']
    ]
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Regions')
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site groups')
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_('Sites')
    )
    device_type_id = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        label=_('Device types')
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        label=_('Roles')
    )
    platform_id = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        label=_('Platforms')
    )
    cluster_group_id = DynamicModelMultipleChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        label=_('Cluster groups')
    )
    cluster_id = DynamicModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        label=_('Clusters')
    )
    tenant_group_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        label=_('Tenant groups')
    )
    tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_('Tenant')
    )
    tag = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        to_field_name='slug',
        required=False,
        label=_('Tags')
    )


#
# Filter form for local config context data
#

class LocalConfigContextFilterForm(forms.Form):
    local_context_data = forms.NullBooleanField(
        required=False,
        label=_('Has local config context data'),
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
# Journal entries
#

class JournalEntryForm(BootstrapMixin, forms.ModelForm):
    comments = CommentField()

    kind = forms.ChoiceField(
        choices=add_blank_choice(JournalEntryKindChoices),
        required=False,
        widget=StaticSelect2()
    )

    class Meta:
        model = JournalEntry
        fields = ['assigned_object_type', 'assigned_object_id', 'kind', 'comments']
        widgets = {
            'assigned_object_type': forms.HiddenInput,
            'assigned_object_id': forms.HiddenInput,
        }


class JournalEntryBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=JournalEntry.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    kind = forms.ChoiceField(
        choices=JournalEntryKindChoices,
        required=False
    )
    comments = forms.CharField(
        required=False,
        widget=forms.Textarea()
    )

    class Meta:
        nullable_fields = []


class JournalEntryFilterForm(BootstrapMixin, forms.Form):
    model = JournalEntry
    field_groups = [
        ['created_before', 'created_after', 'created_by_id'],
        ['assigned_object_type_id', 'kind']
    ]
    created_after = forms.DateTimeField(
        required=False,
        label=_('After'),
        widget=DateTimePicker()
    )
    created_before = forms.DateTimeField(
        required=False,
        label=_('Before'),
        widget=DateTimePicker()
    )
    created_by_id = DynamicModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        label=_('User'),
        widget=APISelectMultiple(
            api_url='/api/users/users/',
        )
    )
    assigned_object_type_id = DynamicModelMultipleChoiceField(
        queryset=ContentType.objects.all(),
        required=False,
        label=_('Object Type'),
        widget=APISelectMultiple(
            api_url='/api/extras/content-types/',
        )
    )
    kind = forms.ChoiceField(
        choices=add_blank_choice(JournalEntryKindChoices),
        required=False,
        widget=StaticSelect2()
    )


#
# Change logging
#

class ObjectChangeFilterForm(BootstrapMixin, forms.Form):
    model = ObjectChange
    field_groups = [
        ['time_before', 'time_after', 'action'],
        ['user_id', 'changed_object_type_id'],
    ]
    time_after = forms.DateTimeField(
        required=False,
        label=_('After'),
        widget=DateTimePicker()
    )
    time_before = forms.DateTimeField(
        required=False,
        label=_('Before'),
        widget=DateTimePicker()
    )
    action = forms.ChoiceField(
        choices=add_blank_choice(ObjectChangeActionChoices),
        required=False,
        widget=StaticSelect2()
    )
    user_id = DynamicModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        label=_('User'),
        widget=APISelectMultiple(
            api_url='/api/users/users/',
        )
    )
    changed_object_type_id = DynamicModelMultipleChoiceField(
        queryset=ContentType.objects.all(),
        required=False,
        label=_('Object Type'),
        widget=APISelectMultiple(
            api_url='/api/extras/content-types/',
        )
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
