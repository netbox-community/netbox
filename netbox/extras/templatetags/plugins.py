from django import template as template_
from django.utils.safestring import mark_safe

from extras.registry import registry

register = template_.Library()


def _get_registered_content(obj, method, context):
    """
    Given an object and a PluginTemplateExtension method name and the template context, return all the
    registered content for the object's model.
    """
    html = ''

    model_name = obj._meta.label_lower
    for template_extension_class in registry['plugin_template_extensions'].get(model_name, []):
        template_extension_instance = template_extension_class(obj, context)
        try:
            content = getattr(template_extension_instance, method)()
        except NotImplementedError:
            # This content renderer class does not define content for this method
            continue
        html += content

    return mark_safe(html)


@register.simple_tag(takes_context=True)
def plugin_buttons(context, obj):
    """
    Render all buttons registered by plugins
    """
    return _get_registered_content(obj, 'buttons', context)


@register.simple_tag(takes_context=True)
def plugin_left_page(context, obj):
    """
    Render all left page content registered by plugins
    """
    return _get_registered_content(obj, 'left_page', context)


@register.simple_tag(takes_context=True)
def plugin_right_page(context, obj):
    """
    Render all right page content registered by plugins
    """
    return _get_registered_content(obj, 'right_page', context)


@register.simple_tag(takes_context=True)
def plugin_full_width_page(context, obj):
    """
    Render all full width page content registered by plugins
    """
    return _get_registered_content(obj, 'full_width_page', context)
