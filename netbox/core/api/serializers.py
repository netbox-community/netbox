from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.choices import *
from core.models import *
from core.utils import get_data_backend_choices
from netbox.api.fields import ChoiceField, ContentTypeField
from netbox.api.serializers import BaseModelSerializer, NetBoxModelSerializer
from users.api.nested_serializers import NestedUserSerializer
from .nested_serializers import *

__all__ = (
    'DataFileSerializer',
    'DataSourceSerializer',
    'JobSerializer',
)


class DataSourceSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='core-api:datasource-detail'
    )
    type = ChoiceField(
        choices=get_data_backend_choices()
    )
    status = ChoiceField(
        choices=DataSourceStatusChoices,
        read_only=True
    )

    # Related object counts
    file_count = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        model = DataSource
        fields = [
            'id', 'url', 'display', 'name', 'type', 'source_url', 'enabled', 'status', 'description', 'comments',
            'parameters', 'ignore_rules', 'created', 'last_updated', 'file_count',
        ]

    def clean(self):

        if self.type and self.type not in get_data_backend_choices():
            raise ValidationError({
                'type': _("Unknown backend type: {type}".format(type=self.type))
            })


class DataFileSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='core-api:datafile-detail'
    )
    source = NestedDataSourceSerializer(
        read_only=True
    )

    class Meta:
        model = DataFile
        fields = [
            'id', 'url', 'display', 'source', 'path', 'last_updated', 'size', 'hash',
        ]


class JobSerializer(BaseModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='core-api:job-detail')
    user = NestedUserSerializer(
        read_only=True
    )
    status = ChoiceField(choices=JobStatusChoices, read_only=True)
    object_type = ContentTypeField(
        read_only=True
    )

    class Meta:
        model = Job
        fields = [
            'id', 'url', 'display', 'object_type', 'object_id', 'name', 'status', 'created', 'scheduled', 'interval',
            'started', 'completed', 'user', 'data', 'job_id',
        ]
