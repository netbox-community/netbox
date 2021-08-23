from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from dcim.models import DeviceRole, DeviceType, Platform, Region, Site, SiteGroup
from tenancy.models import Tenant, TenantGroup
from utilities.forms import (
    add_blank_choice, APISelectMultiple, BootstrapMixin, BulkEditForm, BulkEditNullBooleanSelect, ColorField,
    CommentField, ContentTypeChoiceField, ContentTypeMultipleChoiceField, CSVContentTypeField, CSVModelForm,
    CSVMultipleContentTypeField, DateTimePicker, DynamicModelMultipleChoiceField, JSONField, SlugField, StaticSelect,
    StaticSelectMultiple, BOOLEAN_WITH_BLANK_CHOICES,
)
from virtualization.models import Cluster, ClusterGroup
from .choices import *
from .models import *
from .utils import FeatureQuery


#
# Custom fields
#

class CustomFieldForm(BootstrapMixin, forms.ModelForm):
    content_types = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_fields')
    )

    class Meta:
        model = CustomField
        fields = '__all__'
        fieldsets = (
            ('Custom Field', ('name', 'label', 'type', 'weight', 'required', 'description')),
            ('Assigned Models', ('content_types',)),
            ('Behavior', ('filter_logic',)),
            ('Values', ('default', 'choices')),
            ('Validation', ('validation_minimum', 'validation_maximum', 'validation_regex')),
        )


class CustomFieldCSVForm(CSVModelForm):
    content_types = CSVMultipleContentTypeField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_fields'),
        help_text="One or more assigned object types"
    )

    class Meta:
        model = CustomField
        fields = (
            'name', 'label', 'type', 'content_types', 'required', 'description', 'weight', 'filter_logic', 'default',
            'weight',
        )


class CustomFieldBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=CustomField.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    description = forms.CharField(
        required=False
    )
    required = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    weight = forms.IntegerField(
        required=False
    )

    class Meta:
        nullable_fields = []


class CustomFieldFilterForm(BootstrapMixin, forms.Form):
    field_groups = [
        ['q'],
        ['type', 'content_types'],
        ['weight', 'required'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    content_types = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_fields')
    )
    type = forms.MultipleChoiceField(
        choices=CustomFieldTypeChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    weight = forms.IntegerField(
        required=False
    )
    required = forms.NullBooleanField(
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


#
# Custom links
#

class CustomLinkForm(BootstrapMixin, forms.ModelForm):
    content_type = ContentTypeChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_links')
    )

    class Meta:
        model = CustomLink
        fields = '__all__'
        fieldsets = (
            ('Custom Link', ('name', 'content_type', 'weight', 'group_name', 'button_class', 'new_window')),
            ('Templates', ('link_text', 'link_url')),
        )
        help_texts = {
            'link_text': 'Jinja2 template code for the link text. Reference the object as <code>{{ obj }}</code>. '
                         'Links which render as empty text will not be displayed.',
            'link_url': 'Jinja2 template code for the link URL. Reference the object as <code>{{ obj }}</code>.',
        }


class CustomLinkCSVForm(CSVModelForm):
    content_type = CSVContentTypeField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_links'),
        help_text="Assigned object type"
    )

    class Meta:
        model = CustomLink
        fields = (
            'name', 'content_type', 'weight', 'group_name', 'button_class', 'new_window', 'link_text', 'link_url',
        )


class CustomLinkBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=CustomLink.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    content_type = ContentTypeChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_fields'),
        required=False
    )
    new_window = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    weight = forms.IntegerField(
        required=False
    )
    button_class = forms.ChoiceField(
        choices=CustomLinkButtonClassChoices,
        required=False,
        widget=StaticSelect()
    )

    class Meta:
        nullable_fields = []


class CustomLinkFilterForm(BootstrapMixin, forms.Form):
    field_groups = [
        ['q'],
        ['content_type'],
        ['weight', 'new_window'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    content_type = ContentTypeChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_fields')
    )
    weight = forms.IntegerField(
        required=False
    )
    new_window = forms.NullBooleanField(
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


#
# Export templates
#

class ExportTemplateForm(BootstrapMixin, forms.ModelForm):
    content_type = ContentTypeChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_links')
    )

    class Meta:
        model = ExportTemplate
        fields = '__all__'
        fieldsets = (
            ('Custom Link', ('name', 'content_type', 'description')),
            ('Template', ('template_code',)),
            ('Rendering', ('mime_type', 'file_extension', 'as_attachment')),
        )


class ExportTemplateCSVForm(CSVModelForm):
    content_type = CSVContentTypeField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('export_templates'),
        help_text="Assigned object type"
    )

    class Meta:
        model = ExportTemplate
        fields = (
            'name', 'content_type', 'description', 'mime_type', 'file_extension', 'as_attachment', 'template_code',
        )


class ExportTemplateBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ExportTemplate.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    content_type = ContentTypeChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_fields'),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    mime_type = forms.CharField(
        max_length=50,
        required=False
    )
    file_extension = forms.CharField(
        max_length=15,
        required=False
    )
    as_attachment = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect()
    )

    class Meta:
        nullable_fields = ['description', 'mime_type', 'file_extension']


class ExportTemplateFilterForm(BootstrapMixin, forms.Form):
    field_groups = [
        ['q'],
        ['content_type', 'mime_type'],
        ['file_extension', 'as_attachment'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    content_type = ContentTypeChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_fields')
    )
    mime_type = forms.CharField(
        required=False
    )
    file_extension = forms.CharField(
        required=False
    )
    as_attachment = forms.NullBooleanField(
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


#
# Webhooks
#

class WebhookForm(BootstrapMixin, forms.ModelForm):
    content_types = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('webhooks')
    )

    class Meta:
        model = Webhook
        fields = '__all__'
        fieldsets = (
            ('Webhook', ('name', 'enabled')),
            ('Assigned Models', ('content_types',)),
            ('Events', ('type_create', 'type_update', 'type_delete')),
            ('HTTP Request', (
                'payload_url', 'http_method', 'http_content_type', 'additional_headers', 'body_template', 'secret',
            )),
            ('SSL', ('ssl_verification', 'ca_file_path')),
        )


class WebhookCSVForm(CSVModelForm):
    content_types = CSVMultipleContentTypeField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('webhooks'),
        help_text="One or more assigned object types"
    )

    class Meta:
        model = Webhook
        fields = (
            'name', 'enabled', 'content_types', 'type_create', 'type_update', 'type_delete', 'payload_url',
            'http_method', 'http_content_type', 'additional_headers', 'body_template', 'secret', 'ssl_verification',
            'ca_file_path'
        )


class WebhookBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Webhook.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    enabled = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    type_create = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    type_update = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    type_delete = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    http_method = forms.ChoiceField(
        choices=WebhookHttpMethodChoices,
        required=False
    )
    payload_url = forms.CharField(
        required=False
    )
    ssl_verification = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    secret = forms.CharField(
        required=False
    )
    ca_file_path = forms.CharField(
        required=False
    )

    class Meta:
        nullable_fields = ['secret', 'ca_file_path']


class WebhookFilterForm(BootstrapMixin, forms.Form):
    field_groups = [
        ['q'],
        ['content_types', 'http_method'],
        ['enabled', 'type_create', 'type_update', 'type_delete'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    content_types = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_fields')
    )
    http_method = forms.MultipleChoiceField(
        choices=WebhookHttpMethodChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    enabled = forms.NullBooleanField(
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    type_create = forms.NullBooleanField(
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    type_update = forms.NullBooleanField(
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    type_delete = forms.NullBooleanField(
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


#
# Custom field models
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
            key = cf_name[3:]  # Strip "cf_" from field name
            value = self.cleaned_data.get(cf_name)
            empty_values = self.fields[cf_name].empty_values
            # Convert "empty" values to null
            self.instance.custom_field_data[key] = value if value not in empty_values else None

        return super().clean()


class CustomFieldModelCSVForm(CSVModelForm, CustomFieldModelForm):

    def _get_form_field(self, customfield):
        return customfield.to_form_field(for_csv_import=True)


class CustomFieldModelBulkEditForm(BulkEditForm):

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


class CustomFieldModelFilterForm(forms.Form):

    def __init__(self, *args, **kwargs):

        self.obj_type = ContentType.objects.get_for_model(self.model)

        super().__init__(*args, **kwargs)

        # Add all applicable CustomFields to the form
        self.custom_field_filters = []
        custom_fields = CustomField.objects.filter(content_types=self.obj_type).exclude(
            filter_logic=CustomFieldFilterLogicChoices.FILTER_DISABLED
        )
        for cf in custom_fields:
            field_name = 'cf_{}'.format(cf.name)
            self.fields[field_name] = cf.to_form_field(set_initial=True, enforce_required=False)
            self.custom_field_filters.append(field_name)


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
        'q', 'region_id', 'site_group_id', 'site_id', 'role_id', 'platform_id', 'cluster_group_id',
        'cluster_id', 'tenant_group_id', 'tenant_id',
    ]
    field_groups = [
        ['q'],
        ['region_id', 'site_group_id', 'site_id'],
        ['device_type_id', 'role_id', 'platform_id'],
        ['cluster_group_id', 'cluster_id'],
        ['tenant_group_id', 'tenant_id', 'tag']
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Regions'),
        fetch_trigger='open'
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site groups'),
        fetch_trigger='open'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_('Sites'),
        fetch_trigger='open'
    )
    device_type_id = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        label=_('Device types'),
        fetch_trigger='open'
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        label=_('Roles'),
        fetch_trigger='open'
    )
    platform_id = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        label=_('Platforms'),
        fetch_trigger='open'
    )
    cluster_group_id = DynamicModelMultipleChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        label=_('Cluster groups'),
        fetch_trigger='open'
    )
    cluster_id = DynamicModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        label=_('Clusters'),
        fetch_trigger='open'
    )
    tenant_group_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        label=_('Tenant groups'),
        fetch_trigger='open'
    )
    tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_('Tenant'),
        fetch_trigger='open'
    )
    tag = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        to_field_name='slug',
        required=False,
        label=_('Tags'),
        fetch_trigger='open'
    )


#
# Filter form for local config context data
#

class LocalConfigContextFilterForm(forms.Form):
    local_context_data = forms.NullBooleanField(
        required=False,
        label=_('Has local config context data'),
        widget=StaticSelect(
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
        widget=StaticSelect()
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
        ['q'],
        ['created_before', 'created_after', 'created_by_id'],
        ['assigned_object_type_id', 'kind']
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
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
        ),
        fetch_trigger='open'
    )
    assigned_object_type_id = DynamicModelMultipleChoiceField(
        queryset=ContentType.objects.all(),
        required=False,
        label=_('Object Type'),
        widget=APISelectMultiple(
            api_url='/api/extras/content-types/',
        ),
        fetch_trigger='open'
    )
    kind = forms.ChoiceField(
        choices=add_blank_choice(JournalEntryKindChoices),
        required=False,
        widget=StaticSelect()
    )


#
# Change logging
#

class ObjectChangeFilterForm(BootstrapMixin, forms.Form):
    model = ObjectChange
    field_groups = [
        ['q'],
        ['time_before', 'time_after', 'action'],
        ['user_id', 'changed_object_type_id'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
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
        widget=StaticSelect()
    )
    user_id = DynamicModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        label=_('User'),
        widget=APISelectMultiple(
            api_url='/api/users/users/',
        ),
        fetch_trigger='open'
    )
    changed_object_type_id = DynamicModelMultipleChoiceField(
        queryset=ContentType.objects.all(),
        required=False,
        label=_('Object Type'),
        widget=APISelectMultiple(
            api_url='/api/extras/content-types/',
        ),
        fetch_trigger='open'
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
