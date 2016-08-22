import graphviz
from rest_framework import generics
from rest_framework.views import APIView

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404

from circuits.models import Provider
from dcim.models import Site, Device, Interface, InterfaceConnection
from extras.models import CustomFieldChoice, Graph, TopologyMap, GRAPH_TYPE_INTERFACE, GRAPH_TYPE_PROVIDER, GRAPH_TYPE_SITE

from .serializers import GraphSerializer


class CustomFieldModelAPIView(object):
    """
    Include the applicable set of CustomField in the view context.
    """

    def __init__(self):
        super(CustomFieldModelAPIView, self).__init__()
        self.content_type = ContentType.objects.get_for_model(self.queryset.model)
        self.custom_fields = self.content_type.custom_fields.prefetch_related('choices')

        # Cache all relevant CustomFieldChoices. This saves us from having to do a lookup per select field per object.
        custom_field_choices = {}
        for field in self.custom_fields:
            for cfc in field.choices.all():
                custom_field_choices[cfc.id] = cfc.value
        self.custom_field_choices = custom_field_choices


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
        graph = graphviz.Graph()
        graph.graph_attr['ranksep'] = '1'
        for i, device_set in enumerate(tmap.device_sets):

            subgraph = graphviz.Graph(name='sg{}'.format(i))
            subgraph.graph_attr['rank'] = 'same'

            # Add a pseudonode for each device_set to enforce hierarchical layout
            subgraph.node('set{}'.format(i), label='', shape='none', width='0')
            if i:
                graph.edge('set{}'.format(i - 1), 'set{}'.format(i), style='invis')

            # Add each device to the graph
            devices = []
            for query in device_set.split(','):
                devices += Device.objects.filter(name__regex=query)
            for d in devices:
                subgraph.node(d.name)

            # Add an invisible connection to each successive device in a set to enforce horizontal order
            for j in range(0, len(devices) - 1):
                subgraph.edge(devices[j].name, devices[j + 1].name, style='invis')

            graph.subgraph(subgraph)

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
            graph.edge(c.interface_a.device.name, c.interface_b.device.name)

        # Get the image data and return
        try:
            topo_data = graph.pipe(format='png')
        except:
            return HttpResponse("There was an error generating the requested graph. Ensure that the GraphViz "
                                "executables have been installed correctly.")
        response = HttpResponse(topo_data, content_type='image/png')

        return response
