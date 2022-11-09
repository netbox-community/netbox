import collections

from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from packaging import version

from netbox.registry import registry
from netbox.search import register_search
from .navigation import *
from .registration import *
from .templates import *

# Initialize plugin registry
registry['plugins'] = {
    'graphql_schemas': [],
    'menus': [],
    'menu_items': {},
    'preferences': {},
    'template_extensions': collections.defaultdict(list),
}


#
# Plugin AppConfig class
#

class PluginConfig(AppConfig):
    """
    Subclass of Django's built-in AppConfig class, to be used for NetBox plugins.
    """
    # Plugin metadata
    author = ''
    author_email = ''
    description = ''
    version = ''

    # Root URL path under /plugins. If not set, the plugin's label will be used.
    base_url = None

    # Minimum/maximum compatible versions of NetBox
    min_version = None
    max_version = None

    # Default configuration parameters
    default_settings = {}

    # Mandatory configuration parameters
    required_settings = []

    # Middleware classes provided by the plugin
    middleware = []

    # Django-rq queues dedicated to the plugin
    queues = []

    # Django apps to append to INSTALLED_APPS when plugin requires them.
    django_apps = []

    # Default integration paths. Plugin authors can override these to customize the paths to
    # integrated components.
    search_indexes = 'search.indexes'
    graphql_schema = 'graphql.schema'
    menu = 'navigation.menu'
    menu_items = 'navigation.menu_items'
    template_extensions = 'template_content.template_extensions'
    user_preferences = 'preferences.preferences'

    def ready(self):
        plugin_name = self.name.rsplit('.', 1)[-1]

        # Register search extensions (if defined)
        try:
            search_indexes = import_string(f"{self.__module__}.{self.search_indexes}")
            for idx in search_indexes:
                register_search(idx)
        except ImportError:
            pass

        # Register template content (if defined)
        try:
            template_extensions = import_string(f"{self.__module__}.{self.template_extensions}")
            register_template_extensions(template_extensions)
        except ImportError:
            pass

        # Register navigation menu and/or menu items (if defined)
        try:
            menu = import_string(f"{self.__module__}.{self.menu}")
            register_menu(menu)
        except ImportError:
            pass
        try:
            menu_items = import_string(f"{self.__module__}.{self.menu_items}")
            register_menu_items(self.verbose_name, menu_items)
        except ImportError:
            pass

        # Register GraphQL schema (if defined)
        try:
            graphql_schema = import_string(f"{self.__module__}.{self.graphql_schema}")
            register_graphql_schema(graphql_schema)
        except ImportError:
            pass

        # Register user preferences (if defined)
        try:
            user_preferences = import_string(f"{self.__module__}.{self.user_preferences}")
            register_user_preferences(plugin_name, user_preferences)
        except ImportError:
            pass

    @classmethod
    def validate(cls, user_config, netbox_version):

        # Enforce version constraints
        current_version = version.parse(netbox_version)
        if cls.min_version is not None:
            min_version = version.parse(cls.min_version)
            if current_version < min_version:
                raise ImproperlyConfigured(
                    f"Plugin {cls.__module__} requires NetBox minimum version {cls.min_version}."
                )
        if cls.max_version is not None:
            max_version = version.parse(cls.max_version)
            if current_version > max_version:
                raise ImproperlyConfigured(
                    f"Plugin {cls.__module__} requires NetBox maximum version {cls.max_version}."
                )

        # Verify required configuration settings
        for setting in cls.required_settings:
            if setting not in user_config:
                raise ImproperlyConfigured(
                    f"Plugin {cls.__module__} requires '{setting}' to be present in the PLUGINS_CONFIG section of "
                    f"configuration.py."
                )

        # Apply default configuration values
        for setting, value in cls.default_settings.items():
            if setting not in user_config:
                user_config[setting] = value


#
# Utilities
#

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
