from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from netbox.registry import registry

__all__ = (
    'get_installed_plugins',
    'get_plugin_config',
)


def get_installed_plugins():
    """
    Return a dictionary mapping the names of installed plugins to their versions.
    """
    plugins = {}
    for plugin_name in registry['plugins']['installed']:
        plugin_name = plugin_name.rsplit('.', 1)[-1]
        plugin_config = apps.get_app_config(plugin_name)
        plugins[plugin_name] = getattr(plugin_config, 'version', None)

    return dict(sorted(plugins.items()))


def get_plugin_config(plugin_name, parameter, default=None):
    """
    Return the value of the specified plugin configuration parameter.

    Args:
        plugin_name: The name of the plugin
        parameter: The name of the configuration parameter
        default: The value to return if the parameter is not defined (default: None)
    """
    try:
        plugin_config = settings.PLUGINS_CONFIG[plugin_name]
        return plugin_config.get(parameter, default)
    except KeyError:
        raise ImproperlyConfigured(f"Plugin {plugin_name} is not registered.")
