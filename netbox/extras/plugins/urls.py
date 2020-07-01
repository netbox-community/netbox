import importlib
import sys

from django.apps import apps
from django.conf import settings
from django.conf.urls import include
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from . import views

# Initialize URL base, API, and admin URL patterns for plugins
plugin_patterns = []
plugin_api_patterns = [
    path('', views.PluginsAPIRootView.as_view(), name='api-root'),
    path('installed-plugins/', views.InstalledPluginsAPIView.as_view(), name='plugins-list')
]
plugin_admin_patterns = [
    path('installed-plugins/', staff_member_required(views.InstalledPluginsAdminView.as_view()), name='plugins_list')
]

# Register base/API URL patterns for each plugin
for plugin_path in settings.PLUGINS:
    plugin_name = plugin_path.split('.')[-1]
    app = apps.get_app_config(plugin_name)
    base_url = getattr(app, 'base_url') or app.label

    # Check if the plugin specifies any base URLs
    spec = importlib.util.find_spec(f"{plugin_path}.urls")
    if spec is not None:
        # The plugin has a .urls module - import it
        urls = importlib.util.module_from_spec(spec)
        sys.modules[f"{plugin_path}.urls"] = urls
        spec.loader.exec_module(urls)
        if hasattr(urls, "urlpatterns"):
            urlpatterns = urls.urlpatterns
            plugin_patterns.append(
                path(f"{base_url}/", include((urlpatterns, app.label)))
            )

    # Check if the plugin specifies any API URLs
    spec = importlib.util.find_spec(f"{plugin_path}.api")
    if spec is not None:
        spec = importlib.util.find_spec(f"{plugin_path}.api.urls")
        if spec is not None:
            # The plugin has a .api.urls module - import it
            api_urls = importlib.util.module_from_spec(spec)
            sys.modules[f"{plugin_path}.api.urls"] = api_urls
            spec.loader.exec_module(api_urls)
            if hasattr(api_urls, "urlpatterns"):
                urlpatterns = api_urls.urlpatterns
                plugin_api_patterns.append(
                    path(f"{base_url}/", include((urlpatterns, f"{app.label}-api")))
                )
