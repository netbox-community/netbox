import inspect

from netbox.registry import registry
from .navigation import PluginMenu, PluginMenuButton, PluginMenuItem
from .templates import PluginTemplateExtension

__all__ = (
    'register_graphql_schema',
    'register_menu',
    'register_menu_items',
    'register_template_extensions',
    'register_user_preferences',
)


def register_template_extensions(class_list):
    """
    Register a list of PluginTemplateExtension classes
    """
    # Validation
    for template_extension in class_list:
        if not inspect.isclass(template_extension):
            raise TypeError(f"PluginTemplateExtension class {template_extension} was passed as an instance!")
        if not issubclass(template_extension, PluginTemplateExtension):
            raise TypeError(f"{template_extension} is not a subclass of extras.plugins.PluginTemplateExtension!")
        if template_extension.model is None:
            raise TypeError(f"PluginTemplateExtension class {template_extension} does not define a valid model!")

        registry['plugins']['template_extensions'][template_extension.model].append(template_extension)


def register_menu(menu):
    if not isinstance(menu, PluginMenu):
        raise TypeError(f"{menu} must be an instance of extras.plugins.PluginMenu")
    registry['plugins']['menus'].append(menu)


def register_menu_items(section_name, class_list):
    """
    Register a list of PluginMenuItem instances for a given menu section (e.g. plugin name)
    """
    # Validation
    for menu_link in class_list:
        if not isinstance(menu_link, PluginMenuItem):
            raise TypeError(f"{menu_link} must be an instance of extras.plugins.PluginMenuItem")
        for button in menu_link.buttons:
            if not isinstance(button, PluginMenuButton):
                raise TypeError(f"{button} must be an instance of extras.plugins.PluginMenuButton")

    registry['plugins']['menu_items'][section_name] = class_list


def register_graphql_schema(graphql_schema):
    """
    Register a GraphQL schema class for inclusion in NetBox's GraphQL API.
    """
    registry['plugins']['graphql_schemas'].append(graphql_schema)


def register_user_preferences(plugin_name, preferences):
    """
    Register a list of user preferences defined by a plugin.
    """
    registry['plugins']['preferences'][plugin_name] = preferences
