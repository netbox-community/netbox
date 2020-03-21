import collections
import importlib
import inspect

from django.apps import AppConfig
from django.template.loader import get_template

from extras.registry import registry
from .signals import register_detail_page_content_classes, register_nav_menu_link_classes


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
    url_slug = None

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
# Nav menu links
#

class PluginNavMenuLink:
    """
    This class represents a nav menu item. This constitutes primary link and its text, but also allows for
    specifying additional link buttons that appear to the right of the item in the van menu.

    Links are specified as Django reverse URL strings.
    Buttons are each specified as a list of PluginNavMenuButton instances.
    """
    link = None
    link_text = None
    link_permission = None
    buttons = []


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


def register_nav_menu_links():
    """
    Helper method that populates the registry with all nav menu link classes that have been registered by plugins
    """
    registry['plugin_nav_menu_link_classes'] = {}

    responses = register_nav_menu_link_classes.send('registration_event')
    for receiver, response in responses:

        # Import the app config for the plugin to get the name to be used as the nav menu section text
        module = importlib.import_module(receiver.__module__.split('.')[0])
        default_app_config = getattr(module, 'default_app_config')
        module, app_config = default_app_config.rsplit('.', 1)
        app_config = getattr(importlib.import_module(module), app_config)
        section_name = getattr(app_config, 'verbose_name', app_config.name)

        if not isinstance(response, list):
            response = [response]
        for link_class in response:
            if not inspect.isclass(link_class):
                raise TypeError('Plugin nav menu link class {} was passes as an instance!'.format(link_class))
            if not issubclass(link_class, PluginNavMenuLink):
                raise TypeError('{} is not a subclass of extras.plugins.PluginNavMenuLink!'.format(link_class))
            if link_class.link is None or link_class.link_text is None:
                raise TypeError('Plugin nav menu link {} must specify at least link and link_text'.format(link_class))

            for button in link_class.buttons:
                if not isinstance(button, PluginNavMenuButton):
                    raise TypeError('{} must be an instance of PluginNavMenuButton!'.format(button))

        registry['plugin_nav_menu_link_classes'][section_name] = response


def get_nav_menu_link_classes():
    """
    Return the list of all registered nav menu link classes.
    Populate the registry if it is empty.
    """
    if 'plugin_nav_menu_link_classes' not in registry:
        register_nav_menu_links()

    return registry['plugin_nav_menu_link_classes']
