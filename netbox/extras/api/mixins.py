from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from extras.models import ConfigTemplate
from netbox.api.authentication import TokenWritePermission
from netbox.api.renderers import TextRenderer

from .serializers import RenderConfigInputSerializer, RenderedConfigSerializer

__all__ = (
    'ConfigTemplateRenderMixin',
    'RenderConfigMixin',
)


class ConfigTemplateRenderMixin:
    """
    Provides a method to return a rendered ConfigTemplate as REST API data.
    """
    def render_configtemplate(self, request, configtemplate, context):
        try:
            output = configtemplate.render(context=context)
        except Exception as e:
            detail = configtemplate.format_render_error(e)
            if request.accepted_renderer.format == 'txt':
                return Response(detail, status=HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({'detail': detail}, status=HTTP_500_INTERNAL_SERVER_ERROR)

        # If the client has requested "text/plain", return the raw content.
        if request.accepted_renderer.format == 'txt':
            return Response(output)

        serializer = RenderedConfigSerializer(
            instance={'configtemplate': configtemplate, 'content': output},
            context={'request': request},
        )
        return Response(serializer.data)


class RenderConfigMixin(ConfigTemplateRenderMixin):
    """
    Provides a /render-config/ endpoint for REST API views whose model may have a ConfigTemplate assigned.
    """

    def get_permissions(self):
        # For render_config action, check only token write ability (not model permissions)
        if self.action == 'render_config':
            return [TokenWritePermission()]
        return super().get_permissions()

    @extend_schema(
        request=RenderConfigInputSerializer,
        responses={
            200: OpenApiResponse(
                response=RenderedConfigSerializer,
                description=_(
                    "The rendered config template. When the client requests `text/plain`, the raw "
                    "rendered content is returned in place of the JSON object."
                ),
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description=_("No config template could be resolved for this object."),
            ),
            500: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description=_("An error occurred while rendering the config template."),
            ),
        },
    )
    @action(detail=True, methods=['post'], url_path='render-config', renderer_classes=[JSONRenderer, TextRenderer])
    def render_config(self, request, pk):
        """
        Resolve and render the preferred ConfigTemplate for this Device or Virtual Machine.
        """
        # Override restrict() on the default queryset to enforce the render_config & view actions
        self.queryset = self.queryset.model.objects.restrict(request.user, 'render_config').restrict(
            request.user, 'view'
        )
        instance = self.get_object()

        object_type = instance._meta.model_name

        # Check for an optional config_template_id override in the request data
        if config_template_id := request.data.get('config_template_id'):
            try:
                configtemplate = ConfigTemplate.objects.restrict(request.user, 'view').get(pk=config_template_id)
            except (ConfigTemplate.DoesNotExist, ValueError):
                return Response({
                    'error': _('Config template with ID {id} not found.').format(id=config_template_id)
                }, status=HTTP_400_BAD_REQUEST)
        else:
            configtemplate = instance.get_config_template()
            if not configtemplate:
                return Response({
                    'error': _('No config template found for this {object_type}.').format(object_type=object_type)
                }, status=HTTP_400_BAD_REQUEST)

        # Compile context data
        context_data = instance.get_config_context()
        context_data.update({k: v for k, v in request.data.items() if k != 'config_template_id'})
        context_data.update({object_type: instance})

        return self.render_configtemplate(request, configtemplate, context_data)
