from jinja2.exceptions import TemplateError
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from netbox.api.renderers import TextRenderer
from .serializers import ConfigTemplateSerializer

__all__ = (
    'ConfigContextQuerySetMixin',
    'ConfigTemplateRenderMixin',
    'RenderConfigMixin',
)


class ConfigContextQuerySetMixin:
    """
    Used by views that work with config context models (device and virtual machine).
    Provides a get_queryset() method which deals with adding the config context
    data annotation or not.
    """
    def get_queryset(self):
        """
        Build the proper queryset based on the request context

        If the `brief` query param equates to True or the `exclude` query param
        includes `config_context` as a value, return the base queryset.

        Else, return the queryset annotated with config context data
        """
        queryset = super().get_queryset()
        request = self.get_serializer_context()['request']
        if self.brief or 'config_context' in request.query_params.get('exclude', []):
            return queryset
        return queryset.annotate_config_context_data()


class ConfigTemplateRenderMixin:
    """
    Provides a method to return a rendered ConfigTemplate as REST API data.
    """
    def render_configtemplate(self, request, configtemplate, context):
        try:
            output = configtemplate.render(context=context)
        except TemplateError as e:
            return Response({
                'detail': f"An error occurred while rendering the template (line {e.lineno}): {e}"
            }, status=500)

        # If the client has requested "text/plain", return the raw content.
        if request.accepted_renderer.format == 'txt':
            return Response(output)

        template_serializer = ConfigTemplateSerializer(configtemplate, nested=True, context={'request': request})

        return Response({
            'configtemplate': template_serializer.data,
            'content': output
        })


class RenderConfigMixin(ConfigTemplateRenderMixin):
    """
    Provides a /render-config/ endpoint for REST API views whose model may have a ConfigTemplate assigned.
    """
    @action(detail=True, methods=['post'], url_path='render-config', renderer_classes=[JSONRenderer, TextRenderer])
    def render_config(self, request, pk):
        """
        Resolve and render the preferred ConfigTemplate for this Device.
        """
        instance = self.get_object()
        object_type = instance._meta.model_name
        configtemplate = instance.get_config_template()
        if not configtemplate:
            return Response({
                'error': f'No config template found for this {object_type}.'
            }, status=HTTP_400_BAD_REQUEST)

        # Compile context data
        context_data = instance.get_config_context()
        context_data.update(request.data)
        context_data.update({object_type: instance})

        return self.render_configtemplate(request, configtemplate, context_data)
