import inspect

from django.utils.translation import gettext_lazy as _
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
            # Registration for multiple models
            models = template_extension.models
        elif template_extension.model:
            # Registration for a single model
            models = [template_extension.model]
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
