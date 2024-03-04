import collections
from importlib import import_module

from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from packaging import version

from netbox.registry import registry
from netbox.search import register_search
from netbox.utils import register_data_backend
from .navigation import *
from .registration import *
from .templates import *
from .utils import *

# Initialize plugin registry
registry['plugins'].update({
    'graphql_schemas': [],
    'menus': [],
    'menu_items': {},
    'preferences': {},
    'template_extensions': collections.defaultdict(list),
})

DEFAULT_RESOURCE_PATHS = {
    'search_indexes': 'search.indexes',
    'data_backends': 'data_backends.backends',
    'graphql_schema': 'graphql.schema',
    'menu': 'navigation.menu',
    'menu_items': 'navigation.menu_items',
    'template_extensions': 'template_content.template_extensions',
    'user_preferences': 'preferences.preferences',
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

    # Optional plugin resources
    search_indexes = None
    data_backends = None
    graphql_schema = None
    menu = None
    menu_items = None
    template_extensions = None
    user_preferences = None

    def _load_resource(self, name):
        # Import from the configured path, if defined.
        if path := getattr(self, name, None):
            return import_string(f"{self.__module__}.{path}")

        # Fall back to the resource's default path. Return None if the module has not been provided.
        default_path = f'{self.__module__}.{DEFAULT_RESOURCE_PATHS[name]}'
        default_module, resource_name = default_path.rsplit('.', 1)
        try:
            module = import_module(default_module)
            return getattr(module, resource_name, None)
        except ModuleNotFoundError:
            pass

    def ready(self):
        from netbox.models.features import register_models

        # Register models
        register_models(*self.get_models())

        plugin_name = self.name.rsplit('.', 1)[-1]

        # Register search extensions (if defined)
        search_indexes = self._load_resource('search_indexes') or []
        for idx in search_indexes:
            register_search(idx)

        # Register data backends (if defined)
        data_backends = self._load_resource('data_backends') or []
        for backend in data_backends:
            register_data_backend()(backend)

        # Register template content (if defined)
        if template_extensions := self._load_resource('template_extensions'):
            register_template_extensions(template_extensions)

        # Register navigation menu and/or menu items (if defined)
        if menu := self._load_resource('menu'):
            register_menu(menu)
        if menu_items := self._load_resource('menu_items'):
            register_menu_items(self.verbose_name, menu_items)

        # Register GraphQL schema (if defined)
        if graphql_schema := self._load_resource('graphql_schema'):
            register_graphql_schema(graphql_schema)

        # Register user preferences (if defined)
        if user_preferences := self._load_resource('user_preferences'):
            register_user_preferences(plugin_name, user_preferences)

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
