from rest_framework import serializers

from dcim.api.serializers import NestedSiteSerializer
from extras.models import Graph, TopologyMap


#
# Graphs
#

class GraphSerializer(serializers.ModelSerializer):
    embed_url = serializers.SerializerMethodField()
    embed_link = serializers.SerializerMethodField()

    class Meta:
        model = Graph
        fields = ['name', 'embed_url', 'embed_link']

    def get_embed_url(self, obj):
        return obj.embed_url(self.context['graphed_object'])

    def get_embed_link(self, obj):
        return obj.embed_link(self.context['graphed_object'])


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
        fields = ['name', 'slug', 'site', 'device_patterns', 'description']
