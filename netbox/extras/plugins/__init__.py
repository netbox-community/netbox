import collections
import inspect

from django.apps import AppConfig
from django.template.loader import get_template
from django.utils.module_loading import import_string

from extras.registry import registry
from .signals import register_detail_page_content_classes


# Initialize plugin registry stores
registry['plugin_nav_menu_links'] = {}


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

    # Caching configuration
    caching_config = {}

    def ready(self):

        # Register navigation menu items (if defined)
        register_menu_items(self.verbose_name, self.get_menu_items())

    def get_menu_items(self):
        """
        Default method to import navigation menu items for a plugin from the default location (menu_items in a
        file named navigation.py). This method may be overridden by a plugin author to import menu items from
        a different location if needed.
        """
        try:
            menu_items = import_string(f"{self.__module__}.navigation.menu_items")
            return menu_items
        except ImportError:
            return []


#
# Template content injection
#

class PluginTemplateContent:
    """
    This class is used to register plugin content to be injected into core NetBox templates.
    It contains methods that are overriden by plugin authors to return template content.

    The `model` attribute on the class defines the which model detail page this class renders
    content for. It should be set as a string in the form '<app_label>.<model_name>'.
    """
    model = None

    def __init__(self, obj, context):
        self.obj = obj
        self.context = context

    def render(self, template, extra_context=None):
        """
        Convenience menthod for rendering the provided template name. The detail page object is automatically
        passed into the template context as `obj` and the origional detail page's context is available as
        `obj_context`. An additional context dictionary may be passed as `extra_context`.
        """
        context = {
            'obj': self.obj,
            'obj_context': self.context
        }
        if isinstance(extra_context, dict):
            context.update(extra_context)

        return get_template(template).render(context)

    def left_page(self):
        """
        Content that will be rendered on the left of the detail page view. Content should be returned as an
        HTML string. Note that content does not need to be marked as safe because this is automatically handled.
        """
        raise NotImplementedError

    def right_page(self):
        """
        Content that will be rendered on the right of the detail page view. Content should be returned as an
        HTML string. Note that content does not need to be marked as safe because this is automatically handled.
        """
        raise NotImplementedError

    def full_width_page(self):
        """
        Content that will be rendered within the full width of the detail page view. Content should be returned as an
        HTML string. Note that content does not need to be marked as safe because this is automatically handled.
        """
        raise NotImplementedError

    def buttons(self):
        """
        Buttons that will be rendered and added to the existing list of buttons on the detail page view. Content
        should be returned as an HTML string. Note that content does not need to be marked as safe because this is
        automatically handled.
        """
        raise NotImplementedError


def register_content_classes():
    """
    Helper method that populates the registry with all template content classes that have been registered by plugins
    """
    registry['plugin_template_content_classes'] = collections.defaultdict(list)

    responses = register_detail_page_content_classes.send('registration_event')
    for receiver, response in responses:
        if not isinstance(response, list):
            response = [response]
        for template_class in response:
            if not inspect.isclass(template_class):
                raise TypeError('Plugin content class {} was passes as an instance!'.format(template_class))
            if not issubclass(template_class, PluginTemplateContent):
                raise TypeError('{} is not a subclass of extras.plugins.PluginTemplateContent!'.format(template_class))
            if template_class.model is None:
                raise TypeError('Plugin content class {} does not define a valid model!'.format(template_class))

            registry['plugin_template_content_classes'][template_class.model].append(template_class)


def get_content_classes(model):
    """
    Given a model string, return the list of all registered template content classes.
    Populate the registry if it is empty.
    """
    if 'plugin_template_content_classes' not in registry:
        register_content_classes()

    return registry['plugin_template_content_classes'].get(model, [])


#
# Navigation menu links
#

class PluginNavMenuLink:
    """
    This class represents a nav menu item. This constitutes primary link and its text, but also allows for
    specifying additional link buttons that appear to the right of the item in the van menu.

    Links are specified as Django reverse URL strings.
    Buttons are each specified as a list of PluginNavMenuButton instances.
    """
    def __init__(self, link, link_text, permission=None, buttons=None):
        self.link = link
        self.link_text = link_text
        self.link_permission = permission
        if buttons is None:
            self.buttons = []
        else:
            self.buttons = buttons


class PluginNavMenuButton:
    """
    This class represents a button which is a part of the nav menu link item.
    Note that button colors should come from ButtonColorChoices
    """
    def __init__(self, link, title, icon_class, color, permission=None):
        self.link = link
        self.title = title
        self.icon_class = icon_class
        self.color = color
        self.permission = permission


def register_menu_items(section_name, class_list):
    """
    Register a list of PluginNavMenuLink instances for a given menu section (e.g. plugin name)
    """
    # Validation
    for menu_link in class_list:
        if not isinstance(menu_link, PluginNavMenuLink):
            raise TypeError(f"{menu_link} must be an instance of extras.plugins.PluginNavMenuLink")
        for button in menu_link.buttons:
            if not isinstance(button, PluginNavMenuButton):
                raise TypeError(f"{button} must be an instance of extras.plugins.PluginNavMenuButton")

    registry['plugin_nav_menu_links'][section_name] = class_list
