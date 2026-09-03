import collections
from importlib import import_module

from django.apps import AppConfig, apps
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from packaging import version

from core.exceptions import IncompatiblePluginError
from netbox.event_rules import register_event_rule_action
from netbox.registry import registry
from netbox.search import register_search
from netbox.utils import register_data_backend

from .navigation import *
from .registration import *
from .templates import *
from .utils import *

# Initialize plugin registry
registry['plugins'].update({
    'installed': [],
    'graphql_schemas': [],
    'jinja_filters': {},
    'graphql_type_extensions': collections.defaultdict(list),
    'graphql_filter_extensions': collections.defaultdict(list),
    # Assembled (store key, model label) pairs. Registering an extension for an assembled target raises.
    'graphql_extensions_assembled': set(),
    'menus': [],
    'menu_items': {},
    'preferences': {},
    'template_extensions': collections.defaultdict(list),
})

DEFAULT_RESOURCE_PATHS = {
    'search_indexes': 'search.indexes',
    'data_backends': 'data_backends.backends',
    'event_rule_actions': 'event_rules.event_rule_actions',
    'graphql_schema': 'graphql.schema',
    'graphql_type_extensions': 'graphql_extensions.type_extensions',
    'graphql_filter_extensions': 'graphql_extensions.filter_extensions',
    'jinja_filters': 'jinja_env.filters',
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
    release_track = ''

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
    event_rule_actions = None
    graphql_schema = None
    jinja_filters = None
    # Extension resources load from ready() and must not import core GraphQL modules. Schemas load at assembly.
    graphql_type_extensions = None
    graphql_filter_extensions = None
    menu = None
    menu_items = None
    serializer_resolver = None
    template_extensions = None
    user_preferences = None
    events_pipeline = []

    def get_jinja_context(self):
        """
        Return a dict of additional variables to inject into the Jinja template context
        when rendering ConfigTemplates. Override this in a PluginConfig subclass to expose
        plugin-managed data to config templates without requiring template authors to know
        internal model names.

        The returned dict is merged into the template context after the standard
        ObjectType-based model population, so keys here can shadow the auto-populated
        entries if needed.
        """
        return {}

    def _load_resource(self, name):
        # Import from the configured path, if defined.
        if path := getattr(self, name, None):
            return import_string(f"{self.__module__}.{path}")

        # Fall back to the default path. Only the module's own absence returns None, nested errors propagate.
        default_path = f'{self.__module__}.{DEFAULT_RESOURCE_PATHS[name]}'
        default_module, resource_name = default_path.rsplit('.', 1)
        try:
            module = import_module(default_module)
        except ModuleNotFoundError as exc:
            if exc.name and (default_module == exc.name or default_module.startswith(f'{exc.name}.')):
                return None
            raise
        return getattr(module, resource_name, None)

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

        # Register event rule actions (if defined)
        event_rule_actions = self._load_resource('event_rule_actions') or []
        for action in event_rule_actions:
            register_event_rule_action(action)

        # Register Jinja filters (if defined)
        if jinja_filters := self._load_resource('jinja_filters'):
            register_jinja_filters(jinja_filters)

        # Register template content (if defined)
        if template_extensions := self._load_resource('template_extensions'):
            register_template_extensions(template_extensions)

        # Register navigation menu and/or menu items (if defined)
        if menu := self._load_resource('menu'):
            register_menu(menu)
        if menu_items := self._load_resource('menu_items'):
            register_menu_items(self.verbose_name, menu_items)

        # Register GraphQL type & filter extensions (if defined)
        if graphql_type_extensions := self._load_resource('graphql_type_extensions'):
            register_graphql_type_extensions(graphql_type_extensions)
        if graphql_filter_extensions := self._load_resource('graphql_filter_extensions'):
            register_graphql_filter_extensions(graphql_filter_extensions)

        # Register user preferences (if defined)
        if user_preferences := self._load_resource('user_preferences'):
            register_user_preferences(plugin_name, user_preferences)

        # Register serializer resolver (if defined)
        if self.serializer_resolver:
            resolver_path = f"{self.__module__}.{self.serializer_resolver}"
            try:
                resolver = import_string(resolver_path)
            except ImportError as e:
                raise ImproperlyConfigured(
                    f"Invalid serializer resolver path for plugin {self.__module__}: {resolver_path}"
                ) from e
            register_serializer_resolver(self.label, resolver)

    @classmethod
    def validate(cls, user_config, netbox_version):

        # Enforce version constraints
        current_version = version.parse(netbox_version)
        if cls.min_version is not None:
            min_version = version.parse(cls.min_version)
            if current_version < min_version:
                raise IncompatiblePluginError(
                    f"Plugin {cls.__module__} requires NetBox minimum version {cls.min_version} (current: "
                    f"{netbox_version})."
                )
        if cls.max_version is not None:
            max_version = version.parse(cls.max_version)
            if current_version > max_version:
                raise IncompatiblePluginError(
                    f"Plugin {cls.__module__} requires NetBox maximum version {cls.max_version} (current: "
                    f"{netbox_version})."
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


def _load_plugin_graphql_schemas():
    """
    Load and register every installed plugin's GraphQL schema resource. Runs during root schema assembly, after
    all plugins have initialized, so plugin schema modules may import core GraphQL types freely.
    """
    configs = {config.name: config for config in apps.get_app_configs()}
    for plugin_name in registry['plugins']['installed']:
        if (config := configs.get(plugin_name)) is None:
            raise ImproperlyConfigured(
                f"Plugin '{plugin_name}' has no AppConfig named after its PLUGINS entry. PluginConfig.name "
                f"must match the configured plugin name."
            )
        if graphql_schema := config._load_resource('graphql_schema'):
            # Avoid duplicate registration if the loader is invoked more than once.
            registered = registry['plugins']['graphql_schemas']
            register_graphql_schema([cls for cls in graphql_schema if cls not in registered])
