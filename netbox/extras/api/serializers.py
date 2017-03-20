from rest_framework import serializers

from dcim.api.serializers import NestedSiteSerializer
from extras.models import ACTION_CHOICES, Graph, GRAPH_TYPE_CHOICES, ExportTemplate, TopologyMap, UserAction
from users.api.serializers import NestedUserSerializer
from utilities.api import ChoiceFieldSerializer


#
# Graphs
#

class GraphSerializer(serializers.ModelSerializer):
    type = ChoiceFieldSerializer(choices=GRAPH_TYPE_CHOICES)

    class Meta:
        model = Graph
        fields = ['id', 'type', 'weight', 'name', 'source', 'link']


class WritableGraphSerializer(serializers.ModelSerializer):

    class Meta:
        model = Graph
        fields = ['id', 'type', 'weight', 'name', 'source', 'link']


class RenderedGraphSerializer(serializers.ModelSerializer):
    embed_url = serializers.SerializerMethodField()
    embed_link = serializers.SerializerMethodField()
    type = ChoiceFieldSerializer(choices=GRAPH_TYPE_CHOICES)

    class Meta:
        model = Graph
        fields = ['id', 'type', 'weight', 'name', 'embed_url', 'embed_link']

    def get_embed_url(self, obj):
        return obj.embed_url(self.context['graphed_object'])

    def get_embed_link(self, obj):
        return obj.embed_link(self.context['graphed_object'])


#
# Export templates
#

class ExportTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExportTemplate
        fields = ['id', 'content_type', 'name', 'description', 'template_code', 'mime_type', 'file_extension']


#
# Topology maps
#

class TopologyMapSerializer(serializers.ModelSerializer):
    site = NestedSiteSerializer()

    class Meta:
        model = TopologyMap
        fields = ['id', 'name', 'slug', 'site', 'device_patterns', 'description']


class WritableTopologyMapSerializer(serializers.ModelSerializer):

    class Meta:
        model = TopologyMap
        fields = ['id', 'name', 'slug', 'site', 'device_patterns', 'description']


#
# User actions
#

class UserActionSerializer(serializers.ModelSerializer):
    user = NestedUserSerializer()
    action = ChoiceFieldSerializer(choices=ACTION_CHOICES)

    class Meta:
        model = UserAction
        fields = ['id', 'time', 'user', 'action', 'message']
