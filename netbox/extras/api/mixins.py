from jinja2.exceptions import TemplateError
from rest_framework.response import Response

from .nested_serializers import NestedConfigTemplateSerializer

__all__ = (
    'ConfigContextQuerySetMixin',
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

        template_serializer = NestedConfigTemplateSerializer(configtemplate, context={'request': request})

        return Response({
            'configtemplate': template_serializer.data,
            'content': output
        })
