from collections import OrderedDict

from django.apps import apps
from django.conf import settings
from django.shortcuts import render
from django.urls.exceptions import NoReverseMatch
from django.views.generic import View
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


class InstalledPluginsAdminView(View):
    """
    Admin view for listing all installed plugins
    """
    def get(self, request):
        plugins = [apps.get_app_config(plugin) for plugin in settings.PLUGINS]
        return render(request, 'extras/admin/plugins_list.html', {
            'plugins': plugins,
        })


class InstalledPluginsAPIView(APIView):
    """
    API view for listing all installed plugins
    """
    permission_classes = [permissions.IsAdminUser]
    _ignore_model_permissions = True
    exclude_from_schema = True
    swagger_schema = None

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
            'verison': plugin_app_config.version
        }

    def get(self, request, format=None):
        return Response([self._get_plugin_data(apps.get_app_config(plugin)) for plugin in settings.PLUGINS])


class PluginsAPIRootView(APIView):
    _ignore_model_permissions = True
    exclude_from_schema = True
    swagger_schema = None

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
        for plugin in settings.PLUGINS:
            app_config = apps.get_app_config(plugin)
            entry = self._get_plugin_entry(plugin, app_config, request, format)
            if entry is not None:
                entries.append(entry)

        return Response(OrderedDict((
            ('installed-plugins', reverse('plugins-api:plugins-list', request=request, format=format)),
            *entries
        )))
