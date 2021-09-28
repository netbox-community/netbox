from django import forms
from django.contrib.contenttypes.models import ContentType

from dcim.models import DeviceRole, DeviceType, Platform, Region, Site, SiteGroup
from extras.choices import *
from extras.models import *
from extras.utils import FeatureQuery
from tenancy.models import Tenant, TenantGroup
from utilities.forms import (
    add_blank_choice, BootstrapMixin, CommentField, ContentTypeChoiceField,
    ContentTypeMultipleChoiceField, DynamicModelMultipleChoiceField, JSONField, SlugField, StaticSelect,
)
from virtualization.models import Cluster, ClusterGroup

__all__ = (
    'AddRemoveTagsForm',
    'ConfigContextForm',
    'CustomFieldForm',
    'CustomLinkForm',
    'ExportTemplateForm',
    'ImageAttachmentForm',
    'JournalEntryForm',
    'TagForm',
    'WebhookForm',
)


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
        widgets = {
            'link_text': forms.Textarea(attrs={'class': 'font-monospace'}),
            'link_url': forms.Textarea(attrs={'class': 'font-monospace'}),
        }
        help_texts = {
            'link_text': 'Jinja2 template code for the link text. Reference the object as <code>{{ obj }}</code>. '
                         'Links which render as empty text will not be displayed.',
            'link_url': 'Jinja2 template code for the link URL. Reference the object as <code>{{ obj }}</code>.',
        }


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
        widgets = {
            'template_code': forms.Textarea(attrs={'class': 'font-monospace'}),
        }


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
        widgets = {
            'additional_headers': forms.Textarea(attrs={'class': 'font-monospace'}),
            'body_template': forms.Textarea(attrs={'class': 'font-monospace'}),
        }


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


class ImageAttachmentForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = ImageAttachment
        fields = [
            'name', 'image',
        ]


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
