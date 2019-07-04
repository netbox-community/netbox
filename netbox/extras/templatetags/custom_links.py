from collections import OrderedDict

from django import template
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from jinja2 import Environment

from extras.models import CustomLink


register = template.Library()

LINK_BUTTON = '<a href="{}"{} class="btn btn-sm btn-{}">{}</a>\n'
GROUP_BUTTON = '<div class="btn-group">\n' \
               '<button type="button" class="btn btn-sm btn-{} dropdown-toggle" data-toggle="dropdown">\n' \
               '{} <span class="caret"></span>\n' \
               '</button>\n' \
               '<ul class="dropdown-menu pull-right">\n' \
               '{}</ul></div>'
GROUP_LINK = '<li><a href="{}"{}>{}</a></li>\n'


@register.simple_tag()
def custom_links(obj):
    """
    Render all applicable links for the given object.
    """
    content_type = ContentType.objects.get_for_model(obj)
    custom_links = CustomLink.objects.filter(content_type=content_type)
    if not custom_links:
        return ''

    context = {
        'obj': obj,
    }
    template_code = ''
    group_names = OrderedDict()

    for cl in custom_links:

        # Organize custom links by group
        if cl.group_name and cl.group_name in group_names:
            group_names[cl.group_name].append(cl)
        elif cl.group_name:
            group_names[cl.group_name] = [cl]

        # Add non-grouped links
        else:
            text_rendered = Environment().from_string(source=cl.text).render(**context)
            if text_rendered:
                link_target = ' target="_blank"' if cl.new_window else ''
                template_code += LINK_BUTTON.format(
                    cl.url, link_target, cl.button_class, text_rendered
                )

    # Add grouped links to template
    for group, links in group_names.items():

        links_rendered = []

        for cl in links:
            text_rendered = Environment().from_string(source=cl.text).render(**context)
            if text_rendered:
                link_target = ' target="_blank"' if cl.new_window else ''
                links_rendered.append(
                    GROUP_LINK.format(cl.url, link_target, cl.text)
                )

        if links_rendered:
            template_code += GROUP_BUTTON.format(
                links[0].button_class, group, ''.join(links_rendered)
            )

    # Render template
    rendered = Environment().from_string(source=template_code).render(**context)

    return mark_safe(rendered)
