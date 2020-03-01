from django import template as template_
from django.template.loader import get_template
from django.utils.safestring import mark_safe

from extras.plugins.signals import register_detail_page_buttons


register = template_.Library()


@register.simple_tag()
def plugin_buttons(obj):
    """
    Fire signal to collect all buttons registered by plugins
    """
    html = ''
    responses = register_detail_page_buttons.send(obj)
    for receiver, response in responses:
        if not isinstance(response, list):
            response = [response]
        for template in response:
            if isinstance(template, str):
                template_text = get_template(template).render({'obj': obj})
                html += template_text

    return mark_safe(html)

