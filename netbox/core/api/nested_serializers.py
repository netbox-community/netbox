from rest_framework import serializers

from core.models import *
from netbox.api.serializers import WritableNestedSerializer

__all__ = [
    'NestedDataFileSerializer',
    'NestedDataSourceSerializer',
]


class NestedDataSourceSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='core-api:datasource-detail')

    class Meta:
        model = DataSource
        fields = ['id', 'url', 'display', 'name']


class NestedDataFileSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='core-api:datafile-detail')

    class Meta:
        model = DataFile
        fields = ['id', 'url', 'display', 'path']
