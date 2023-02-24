import graphene


class CabledObjectMixin:
    link_peers = graphene.List('dcim.graphql.gfk_mixins.LinkPeerType')

    def resolve_cable_end(self, info):
        # Handle empty values
        return self.cable_end or None

    def resolve_link_peers(self, info):
        return self.link_peers


class PathEndpointMixin:
    connected_endpoints = graphene.List('dcim.graphql.gfk_mixins.LinkPeerType')

    def resolve_connected_endpoints(self, info):
        # Handle empty values
        return self.connected_endpoints or None
