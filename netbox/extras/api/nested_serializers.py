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


class NestedEventRuleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:eventrule-detail')

    class Meta:
        model = models.EventRule
        fields = ['id', 'url', 'display', 'name']


class NestedWebhookSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:webhook-detail')

    class Meta:
        model = models.Webhook
        fields = ['id', 'url', 'display', 'name']


class NestedCustomFieldSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:customfield-detail')

    class Meta:
        model = models.CustomField
        fields = ['id', 'url', 'display', 'name']


class NestedCustomFieldChoiceSetSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:customfieldchoiceset-detail')

    class Meta:
        model = models.CustomFieldChoiceSet
        fields = ['id', 'url', 'display', 'name', 'choices_count']


class NestedCustomLinkSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:customlink-detail')

    class Meta:
        model = models.CustomLink
        fields = ['id', 'url', 'display', 'name']


class NestedConfigContextSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:configcontext-detail')

    class Meta:
        model = models.ConfigContext
        fields = ['id', 'url', 'display', 'name']


class NestedConfigTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:configtemplate-detail')

    class Meta:
        model = models.ConfigTemplate
        fields = ['id', 'url', 'display', 'name']


class NestedExportTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:exporttemplate-detail')

    class Meta:
        model = models.ExportTemplate
        fields = ['id', 'url', 'display', 'name']


class NestedSavedFilterSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:savedfilter-detail')

    class Meta:
        model = models.SavedFilter
        fields = ['id', 'url', 'display', 'name', 'slug']


class NestedBookmarkSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:bookmark-detail')

    class Meta:
        model = models.Bookmark
        fields = ['id', 'url', 'display', 'object_id', 'object_type']


class NestedImageAttachmentSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:imageattachment-detail')

    class Meta:
        model = models.ImageAttachment
        fields = ['id', 'url', 'display', 'name', 'image']


class NestedJournalEntrySerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:journalentry-detail')

    class Meta:
        model = models.JournalEntry
        fields = ['id', 'url', 'display', 'created']


class NestedScriptSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='extras-api:script-detail',
        lookup_field='full_name',
        lookup_url_kwarg='pk'
    )
    name = serializers.CharField(read_only=True)
    display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Script
        fields = ['id', 'url', 'display', 'name']

    def get_display(self, obj):
        return f'{obj.name} ({obj.module})'
