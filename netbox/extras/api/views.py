import pydot
from rest_framework import generics
from rest_framework.views import APIView
import tempfile
from wsgiref.util import FileWrapper

from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404

from circuits.models import Provider
from dcim.models import Site, Device, Interface, InterfaceConnection
from extras.models import Graph, TopologyMap, GRAPH_TYPE_INTERFACE, GRAPH_TYPE_PROVIDER, GRAPH_TYPE_SITE

from .serializers import GraphSerializer


class GraphListView(generics.ListAPIView):
    """
    Returns a list of relevant graphs
    """
    serializer_class = GraphSerializer

    def get_serializer_context(self):
        cls = {
            GRAPH_TYPE_INTERFACE: Interface,
            GRAPH_TYPE_PROVIDER: Provider,
            GRAPH_TYPE_SITE: Site,
        }
        context = super(GraphListView, self).get_serializer_context()
        context.update({'graphed_object': get_object_or_404(cls[self.kwargs.get('type')], pk=self.kwargs['pk'])})
        return context

    def get_queryset(self):
        graph_type = self.kwargs.get('type', None)
        if not graph_type:
            raise Http404()
        queryset = Graph.objects.filter(type=graph_type)
        return queryset


class TopologyMapView(APIView):
    """
    Generate a topology diagram
    """

    def get(self, request, slug):

        tmap = get_object_or_404(TopologyMap, slug=slug)

        # Construct the graph
        graph = pydot.Dot(graph_type='graph', ranksep='1')
        for i, device_set in enumerate(tmap.device_sets):

            subgraph = pydot.Subgraph('sg{}'.format(i), rank='same')

            # Add a pseudonode for each device_set to enforce hierarchical layout
            subgraph.add_node(pydot.Node('set{}'.format(i), shape='none', width='0'))
            if i:
                graph.add_edge(pydot.Edge('set{}'.format(i - 1), 'set{}'.format(i), style='invis'))

            # Add each device to the graph
            devices = []
            for query in device_set.split(','):
                devices += Device.objects.filter(name__regex=query)
            for d in devices:
                node = pydot.Node(d.name)
                subgraph.add_node(node)

            # Add an invisible connection to each successive device in a set to enforce horizontal order
            for j in range(0, len(devices) - 1):
                edge = pydot.Edge(devices[j].name, devices[j + 1].name)
                # edge.set('style', 'invis') doesn't seem to work for some reason
                edge.set_style('invis')
                subgraph.add_edge(edge)

            graph.add_subgraph(subgraph)

        # Compile list of all devices
        device_superset = Q()
        for device_set in tmap.device_sets:
            for query in device_set.split(','):
                device_superset = device_superset | Q(name__regex=query)

        # Add all connections to the graph
        devices = Device.objects.filter(*(device_superset,))
        connections = InterfaceConnection.objects.filter(interface_a__device__in=devices,
                                                         interface_b__device__in=devices)
        for c in connections:
            edge = pydot.Edge(c.interface_a.device.name, c.interface_b.device.name)
            graph.add_edge(edge)

        # Write the image to disk and return
        topo_file = tempfile.NamedTemporaryFile()
        try:
            graph.write(topo_file.name, format='png')
        except:
            return HttpResponse("There was an error generating the requested graph. Ensure that the GraphViz "
                                "executables have been installed correctly.")
        response = HttpResponse(FileWrapper(topo_file), content_type='image/png')
        topo_file.close()

        return response
