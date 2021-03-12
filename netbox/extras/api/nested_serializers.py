from rest_framework import serializers

from extras import choices, models
from netbox.api import ChoiceField, WritableNestedSerializer
from netbox.api.serializers import NestedTagSerializer
from users.api.nested_serializers import NestedUserSerializer

__all__ = [
    'NestedConfigContextSerializer',
    'NestedCustomFieldSerializer',
    'NestedCustomLinkSerializer',
    'NestedExportTemplateSerializer',
    'NestedImageAttachmentSerializer',
    'NestedJobResultSerializer',
    'NestedTagSerializer',  # Defined in netbox.api.serializers
    'NestedWebhookSerializer',
]


class NestedWebhookSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:webhook-detail')

    class Meta:
        model = models.Webhook
        fields = ['id', 'url', 'name']


class NestedCustomFieldSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:customfield-detail')

    class Meta:
        model = models.CustomField
        fields = ['id', 'url', 'name']


class NestedCustomLinkSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:customlink-detail')

    class Meta:
        model = models.CustomLink
        fields = ['id', 'url', 'name']


class NestedConfigContextSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:configcontext-detail')

    class Meta:
        model = models.ConfigContext
        fields = ['id', 'url', 'name']


class NestedExportTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:exporttemplate-detail')

    class Meta:
        model = models.ExportTemplate
        fields = ['id', 'url', 'name']


class NestedImageAttachmentSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:imageattachment-detail')

    class Meta:
        model = models.ImageAttachment
        fields = ['id', 'url', 'name', 'image']


class NestedJobResultSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:jobresult-detail')
    status = ChoiceField(choices=choices.JobResultStatusChoices)
    user = NestedUserSerializer(
        read_only=True
    )

    class Meta:
        model = models.JobResult
        fields = ['url', 'created', 'completed', 'user', 'status']
