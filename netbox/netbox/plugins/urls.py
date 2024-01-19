from importlib import import_module

from django.apps import apps
from django.conf import settings
from django.conf.urls import include
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path
from django.utils.module_loading import import_string, module_has_submodule

from . import views

# Initialize URL base, API, and admin URL patterns for plugins
plugin_patterns = []
plugin_api_patterns = [
    path('', views.PluginsAPIRootView.as_view(), name='api-root'),
    path('installed-plugins/', views.InstalledPluginsAPIView.as_view(), name='plugins-list')
]

# Register base/API URL patterns for each plugin
for plugin_path in settings.PLUGINS:
    plugin = import_module(plugin_path)
    plugin_name = plugin_path.split('.')[-1]
    app = apps.get_app_config(plugin_name)
    base_url = getattr(app, 'base_url') or app.label

    # Check if the plugin specifies any base URLs
    if module_has_submodule(plugin, 'urls'):
        urlpatterns = import_string(f"{plugin_path}.urls.urlpatterns")
        plugin_patterns.append(
            path(f"{base_url}/", include((urlpatterns, app.label)))
        )

    # Check if the plugin specifies any API URLs
    if module_has_submodule(plugin, 'api.urls'):
        urlpatterns = import_string(f"{plugin_path}.api.urls.urlpatterns")
        plugin_api_patterns.append(
            path(f"{base_url}/", include((urlpatterns, f"{app.label}-api")))
        )
