import collections
import inspect

from django.apps import AppConfig
from django.template.loader import get_template
from django.utils.module_loading import import_string

from extras.registry import registry


# Initialize plugin registry stores
registry['plugin_template_content_classes'] = collections.defaultdict(list)
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

    # Default integration paths. Plugin authors can override these to customize the paths to
    # integrated components.
    template_content_classes = 'template_content.template_content_classes'
    menu_items = 'navigation.menu_items'

    def ready(self):

        # Register template content
        try:
            class_list = import_string(f"{self.__module__}.{self.template_content_classes}")
            register_template_content_classes(class_list)
        except ImportError:
            pass

        # Register navigation menu items (if defined)
        try:
            menu_items = import_string(f"{self.__module__}.{self.menu_items}")
            register_menu_items(self.verbose_name, menu_items)
        except ImportError:
            pass


#
# Template content injection
#

class PluginTemplateContent:
    """
    This class is used to register plugin content to be injected into core NetBox templates.
    It contains methods that are overridden by plugin authors to return template content.

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


def register_template_content_classes(class_list):
    """
    Register a list of PluginTemplateContent classes
    """
    # Validation
    for template_content_class in class_list:
        if not inspect.isclass(template_content_class):
            raise TypeError('Plugin content class {} was passes as an instance!'.format(template_content_class))
        if not issubclass(template_content_class, PluginTemplateContent):
            raise TypeError('{} is not a subclass of extras.plugins.PluginTemplateContent!'.format(template_content_class))
        if template_content_class.model is None:
            raise TypeError('Plugin content class {} does not define a valid model!'.format(template_content_class))

        registry['plugin_template_content_classes'][template_content_class.model].append(template_content_class)


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
        self.permission = permission
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
