from rest_framework.decorators import detail_route
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from extras import filters
from extras.models import Graph, TopologyMap, UserAction
from utilities.api import WritableSerializerMixin
from . import serializers


class CustomFieldModelViewSet(ModelViewSet):
    """
    Include the applicable set of CustomFields in the ModelViewSet context.
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


class GraphViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = Graph.objects.all()
    serializer_class = serializers.GraphSerializer
    write_serializer_class = serializers.WritableGraphSerializer
    filter_class = filters.GraphFilter


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


class RecentActivityViewSet(ReadOnlyModelViewSet):
    """
    List all UserActions to provide a log of recent activity.
    """
    queryset = UserAction.objects.all()
    serializer_class = serializers.UserActionSerializer
    filter_class = filters.UserActionFilter
