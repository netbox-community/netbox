from rest_framework import serializers

from extras import choices, models
from users.api.nested_serializers import NestedUserSerializer
from utilities.api import ChoiceField, WritableNestedSerializer

__all__ = [
    'NestedConfigContextSerializer',
    'NestedExportTemplateSerializer',
    'NestedGraphSerializer',
    'NestedJobResultSerializer',
    'NestedTagSerializer',
]


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


class NestedGraphSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:graph-detail')

    class Meta:
        model = models.Graph
        fields = ['id', 'url', 'name']


class NestedTagSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:tag-detail')

    class Meta:
        model = models.Tag
        fields = ['id', 'url', 'name', 'slug', 'color']


class NestedJobResultSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:jobresult-detail')
    status = ChoiceField(choices=choices.JobResultStatusChoices)
    user = NestedUserSerializer(
        read_only=True
    )

    class Meta:
        model = models.JobResult
        fields = ['url', 'created', 'completed', 'user', 'status']
