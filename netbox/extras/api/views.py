from rest_framework import generics
from rest_framework.decorators import detail_route
from rest_framework.viewsets import ModelViewSet

from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404

from circuits.models import Provider
from dcim.models import Site, Interface
from extras import filters
from extras.models import Graph, TopologyMap, GRAPH_TYPE_INTERFACE, GRAPH_TYPE_PROVIDER, GRAPH_TYPE_SITE
from utilities.api import WritableSerializerMixin
from . import serializers


class CustomFieldModelViewSet(ModelViewSet):
    """
    Include the applicable set of CustomField in the ModelViewSet context.
    """

    def get_serializer_context(self):

        # Gather all custom fields for the model
        content_type = ContentType.objects.get_for_model(self.queryset.model)
        custom_fields = content_type.custom_fields.prefetch_related('choices')

        # Cache all relevant CustomFieldChoices. This saves us from having to do a lookup per select field per object.
        custom_field_choices = {}
        for field in custom_fields:
            for cfc in field.choices.all():
                custom_field_choices[cfc.id] = cfc.value
        custom_field_choices = custom_field_choices

        context = super(CustomFieldModelViewSet, self).get_serializer_context()
        context.update({
            'custom_fields': custom_fields,
            'custom_field_choices': custom_field_choices,
        })
        return context

    def get_queryset(self):
        # Prefetch custom field values
        return super(CustomFieldModelViewSet, self).get_queryset().prefetch_related('custom_field_values__field')


class GraphListView(generics.ListAPIView):
    """
    Returns a list of relevant graphs
    """
    serializer_class = serializers.GraphSerializer

    def get_serializer_context(self):
        cls = {
            GRAPH_TYPE_INTERFACE: Interface,
            GRAPH_TYPE_PROVIDER: Provider,
            GRAPH_TYPE_SITE: Site,
        }
        obj = get_object_or_404(cls[self.kwargs.get('type')], pk=self.kwargs['pk'])
        context = super(GraphListView, self).get_serializer_context()
        context.update({
            'graphed_object': obj,
        })
        return context

    def get_queryset(self):
        graph_type = self.kwargs.get('type', None)
        if not graph_type:
            raise Http404()
        queryset = Graph.objects.filter(type=graph_type)
        return queryset


class TopologyMapViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = TopologyMap.objects.select_related('site')
    serializer_class = serializers.TopologyMapSerializer
    write_serializer_class = serializers.WritableTopologyMapSerializer
    filter_class = filters.TopologyMapFilter

    @detail_route()
    def render(self, request, pk):

        tmap = get_object_or_404(TopologyMap, pk=pk)
        img_format = 'png'

        try:
            data = tmap.render(img_format=img_format)
        except:
            return HttpResponse(
                "There was an error generating the requested graph. Ensure that the GraphViz executables have been "
                "installed correctly."
            )

        response = HttpResponse(data, content_type='image/{}'.format(img_format))
        response['Content-Disposition'] = 'inline; filename="{}.{}"'.format(tmap.slug, img_format)

        return response
