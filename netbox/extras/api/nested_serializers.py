from rest_framework import serializers

from extras import models
from utilities.api import WritableNestedSerializer

__all__ = [
    'NestedConfigContextSerializer',
    'NestedExportTemplateSerializer',
    'NestedGraphSerializer',
    'NestedReportResultSerializer',
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
    tagged_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Tag
        fields = ['id', 'url', 'name', 'slug', 'color', 'tagged_items']


class NestedReportResultSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='extras-api:report-detail',
        lookup_field='report',
        lookup_url_kwarg='pk'
    )

    class Meta:
        model = models.ReportResult
        fields = ['url', 'created', 'user', 'failed']
