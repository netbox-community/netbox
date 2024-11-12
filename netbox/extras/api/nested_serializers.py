import warnings

from rest_framework import serializers

from extras import models
from netbox.api.serializers import NestedTagSerializer, WritableNestedSerializer

__all__ = [
    'NestedBookmarkSerializer',
    'NestedConfigContextSerializer',
    'NestedConfigTemplateSerializer',
    'NestedCustomFieldChoiceSetSerializer',
    'NestedCustomFieldSerializer',
    'NestedCustomLinkSerializer',
    'NestedEventRuleSerializer',
    'NestedExportTemplateSerializer',
    'NestedImageAttachmentSerializer',
    'NestedJournalEntrySerializer',
    'NestedSavedFilterSerializer',
    'NestedScriptSerializer',
    'NestedTagSerializer',  # Defined in netbox.api.serializers
    'NestedWebhookSerializer',
]

# TODO: Remove in v4.2
warnings.warn(
    "Dedicated nested serializers will be removed in NetBox v4.2. Use Serializer(nested=True) instead.",
    DeprecationWarning
)


class NestedEventRuleSerializer(WritableNestedSerializer):

    class Meta:
        model = models.EventRule
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedWebhookSerializer(WritableNestedSerializer):

    class Meta:
        model = models.Webhook
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedCustomFieldSerializer(WritableNestedSerializer):

    class Meta:
        model = models.CustomField
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedCustomFieldChoiceSetSerializer(WritableNestedSerializer):

    class Meta:
        model = models.CustomFieldChoiceSet
        fields = ['id', 'url', 'display_url', 'display', 'name', 'choices_count']


class NestedCustomLinkSerializer(WritableNestedSerializer):

    class Meta:
        model = models.CustomLink
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedConfigContextSerializer(WritableNestedSerializer):

    class Meta:
        model = models.ConfigContext
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedConfigTemplateSerializer(WritableNestedSerializer):

    class Meta:
        model = models.ConfigTemplate
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedExportTemplateSerializer(WritableNestedSerializer):

    class Meta:
        model = models.ExportTemplate
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedSavedFilterSerializer(WritableNestedSerializer):

    class Meta:
        model = models.SavedFilter
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug']


class NestedBookmarkSerializer(WritableNestedSerializer):

    class Meta:
        model = models.Bookmark
        fields = ['id', 'url', 'display', 'object_id', 'object_type']


class NestedImageAttachmentSerializer(WritableNestedSerializer):

    class Meta:
        model = models.ImageAttachment
        fields = ['id', 'url', 'display', 'name', 'image']


class NestedJournalEntrySerializer(WritableNestedSerializer):

    class Meta:
        model = models.JournalEntry
        fields = ['id', 'url', 'display_url', 'display', 'created']


class NestedScriptSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='extras-api:script-detail',
        lookup_field='full_name',
        lookup_url_kwarg='pk'
    )
    display_url = serializers.HyperlinkedIdentityField(
        view_name='extras:script',
        lookup_field='full_name',
        lookup_url_kwarg='pk'
    )
    name = serializers.CharField(read_only=True)
    display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Script
        fields = ['id', 'url', 'display_url', 'display', 'name']

    def get_display(self, obj):
        return f'{obj.name} ({obj.module})'
