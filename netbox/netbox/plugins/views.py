from collections import OrderedDict

from django.apps import apps
from django.urls.exceptions import NoReverseMatch
from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from netbox.registry import registry


@extend_schema(exclude=True)
class InstalledPluginsAPIView(APIView):
    """
    API view for listing all installed plugins
    """
    permission_classes = [permissions.IsAdminUser]
    _ignore_model_permissions = True
    schema = None

    def get_view_name(self):
        return "Installed Plugins"

    @staticmethod
    def _get_plugin_data(plugin_app_config):
        return {
            'name': plugin_app_config.verbose_name,
            'package': plugin_app_config.name,
            'author': plugin_app_config.author,
            'author_email': plugin_app_config.author_email,
            'description': plugin_app_config.description,
            'version': plugin_app_config.version,
            'release_track': plugin_app_config.release_track,
        }

    def get(self, request, format=None):
        return Response([
            self._get_plugin_data(apps.get_app_config(plugin))
            for plugin in registry['plugins']['installed']
        ])


@extend_schema(exclude=True)
class PluginsAPIRootView(APIView):
    _ignore_model_permissions = True
    schema = None

    def get_view_name(self):
        return "Plugins"

    @staticmethod
    def _get_plugin_entry(plugin, app_config, request, format):
        # Check if the plugin specifies any API URLs
        api_app_name = f'{app_config.name}-api'
        try:
            entry = (getattr(app_config, 'base_url', app_config.label), reverse(
                f"plugins-api:{api_app_name}:api-root",
                request=request,
                format=format
            ))
        except NoReverseMatch:
            # The plugin does not include an api-root url
            entry = None

        return entry

    def get(self, request, format=None):

        entries = []
        for plugin in registry['plugins']['installed']:
            app_config = apps.get_app_config(plugin)
            entry = self._get_plugin_entry(plugin, app_config, request, format)
            if entry is not None:
                entries.append(entry)

        return Response(OrderedDict((
            ('installed-plugins', reverse('plugins-api:plugins-list', request=request, format=format)),
            *entries
        )))
