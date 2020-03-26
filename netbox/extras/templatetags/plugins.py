from django import template as template_
from django.conf import settings
from django.utils.safestring import mark_safe

from extras.registry import registry

register = template_.Library()


def _get_registered_content(obj, method, template_context):
    """
    Given an object and a PluginTemplateExtension method name and the template context, return all the
    registered content for the object's model.
    """
    html = ''
    context = {
        'obj': obj,
        'request': template_context['request'],
        'settings': template_context['settings'],
        'config': {},  # Defined per-plugin
    }

    model_name = obj._meta.label_lower
    template_extensions = registry['plugin_template_extensions'].get(model_name, [])
    for template_extension in template_extensions:

        # Update context with plugin-specific configuration parameters
        plugin_name = template_extension.__module__.split('.')[0]
        context['config'] = settings.PLUGINS_CONFIG.get(plugin_name)

        instance = template_extension(context)
        try:
            content = getattr(instance, method)()
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
