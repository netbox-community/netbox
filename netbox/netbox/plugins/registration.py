import inspect
import logging

from django.utils.translation import gettext_lazy as _

from netbox.registry import registry

from .navigation import PluginMenu, PluginMenuButton, PluginMenuItem
from .templates import PluginTemplateExtension

logger = logging.getLogger(__name__)

__all__ = (
    'register_graphql_schema',
    'register_jinja2_filters',
    'register_menu',
    'register_menu_items',
    'register_serializer_resolver',
    'register_template_extensions',
    'register_user_preferences',
)


def register_jinja2_filters(filters):
    """
    Register a dict of Jinja2 filter functions provided by a plugin. Each key is the
    filter name as it will appear in templates; the value is the callable implementing it.
    Plugin-registered filters have lower precedence than instance-level JINJA2_FILTERS
    so that site admins can always override them in configuration.py.
    """
    if not isinstance(filters, dict):
        raise TypeError(_("jinja2_filters must be a dict mapping filter names to callables"))
    for name, fn in filters.items():
        if not callable(fn):
            raise TypeError(_("Jinja2 filter '{name}' must be callable").format(name=name))
        if name in registry['plugins']['jinja2_filters']:
            logger.warning(
                "Jinja2 filter '%s' registered by a plugin is being overridden by a later-loaded plugin",
                name,
            )
    registry['plugins']['jinja2_filters'].update(filters)


def register_template_extensions(class_list):
    """
    Register a list of PluginTemplateExtension classes
    """
    for template_extension in class_list:
        # Validation
        if not inspect.isclass(template_extension):
            raise TypeError(
                _("PluginTemplateExtension class {template_extension} was passed as an instance!").format(
                    template_extension=template_extension
                )
            )
        if not issubclass(template_extension, PluginTemplateExtension):
            raise TypeError(
                _("{template_extension} is not a subclass of netbox.plugins.PluginTemplateExtension!").format(
                    template_extension=template_extension
                )
            )

        if template_extension.models:
            # Registration for specific models
            models = template_extension.models
        else:
            # Global registration (no specific models)
            models = [None]
        for model in models:
            registry['plugins']['template_extensions'][model].append(template_extension)


def register_menu(menu):
    if not isinstance(menu, PluginMenu):
        raise TypeError(_("{item} must be an instance of netbox.plugins.PluginMenuItem").format(item=menu))
    registry['plugins']['menus'].append(menu)


def register_menu_items(section_name, class_list):
    """
    Register a list of PluginMenuItem instances for a given menu section (e.g. plugin name)
    """
    # Validation
    for menu_link in class_list:
        if not isinstance(menu_link, PluginMenuItem):
            raise TypeError(_("{menu_link} must be an instance of netbox.plugins.PluginMenuItem").format(
                menu_link=menu_link
            ))
        for button in menu_link.buttons:
            if not isinstance(button, PluginMenuButton):
                raise TypeError(_("{button} must be an instance of netbox.plugins.PluginMenuButton").format(
                    button=button
                ))

    registry['plugins']['menu_items'][section_name] = class_list


def register_graphql_schema(graphql_schema):
    """
    Register a GraphQL schema class for inclusion in NetBox's GraphQL API.
    """
    registry['plugins']['graphql_schemas'].extend(graphql_schema)


def register_user_preferences(plugin_name, preferences):
    """
    Register a list of user preferences defined by a plugin.
    """
    registry['plugins']['preferences'][plugin_name] = preferences


def register_serializer_resolver(app_label, resolver):
    """
    Register a callable that returns a DRF serializer class for a model in
    the given app, or None if the resolver does not handle the model. The
    resolver is consulted by utilities.api.get_serializer_for_model() before
    the default import-path lookup, but only for models belonging to
    `app_label`. Plugins (and internal apps) should only register resolvers
    for their own models.

    This is the supported extension point for plugins whose models are
    generated dynamically (and therefore have no importable serializer at
    the {app_label}.api.serializers.{Model}Serializer path) or that need
    to override serializer resolution for specific models.

    Resolver signature: resolver(model, prefix='') -> serializer class or None
    """
    if not callable(resolver):
        raise TypeError(_("Serializer resolver must be callable"))
    if app_label in registry['serializer_resolvers']:
        raise ValueError(
            _("A serializer resolver is already registered for app '{app_label}'").format(app_label=app_label)
        )
    registry['serializer_resolvers'][app_label] = resolver
