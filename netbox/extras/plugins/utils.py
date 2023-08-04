from django.apps import apps
from django.conf import settings

__all__ = (
    'get_installed_plugins',
)


def get_installed_plugins():
    """
    Return a dictionary mapping the names of installed plugins to their versions.
    """
    plugins = {}
    for plugin_name in settings.PLUGINS:
        plugin_name = plugin_name.rsplit('.', 1)[-1]
        plugin_config = apps.get_app_config(plugin_name)
        plugins[plugin_name] = getattr(plugin_config, 'version', None)

    return dict(sorted(plugins.items()))
