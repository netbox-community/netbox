import collections
import inspect

from django.core.exceptions import ImproperlyConfigured
from django.template.loader import get_template

from extras.utils import registry
from .signals import register_detail_page_content_classes


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
    registry.plugin_template_content_classes = collections.defaultdict(list)

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

            registry.plugin_template_content_classes[template_class.model].append(template_class)


def get_content_classes(model):
    if not hasattr(registry, 'plugin_template_content_classes'):
        register_content_classes()

    return registry.plugin_template_content_classes.get(model, [])
