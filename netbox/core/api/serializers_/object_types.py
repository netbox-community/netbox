import inspect

from django.urls import NoReverseMatch
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.models import ObjectType
from netbox.api.serializers import BaseModelSerializer
from utilities.views import get_action_url

__all__ = (
    'ObjectTypeSerializer',
)


class ObjectTypeSerializer(BaseModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='core-api:objecttype-detail')
    app_name = serializers.CharField(source='app_verbose_name', read_only=True)
    model_name = serializers.CharField(source='model_verbose_name', read_only=True)
    model_name_plural = serializers.CharField(source='model_verbose_name_plural', read_only=True)
    is_plugin_model = serializers.BooleanField(read_only=True)
    rest_api_endpoint = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = ObjectType
        fields = [
            'id', 'url', 'display', 'app_label', 'app_name', 'model', 'model_name', 'model_name_plural', 'public',
            'features', 'is_plugin_model', 'rest_api_endpoint', 'description',
        ]
        read_only_fields = ['public', 'features']

    @extend_schema_field(OpenApiTypes.STR)
    def get_rest_api_endpoint(self, obj):
        if not (model := obj.model_class()):
            return
        try:
            return get_action_url(model, action='list', rest_api=True)
        except NoReverseMatch:
            return

    @extend_schema_field(OpenApiTypes.STR)
    def get_description(self, obj):
        if not (model := obj.model_class()):
            return
        return inspect.getdoc(model)
