from collections import OrderedDict

from django import template
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe

from extras.models import CustomLink
from utilities.utils import render_jinja2


register = template.Library()

LINK_BUTTON = '<a href="{}"{} class="btn btn-sm btn-{} m-1">{}</a>\n'

GROUP_BUTTON = """
<div class="dropdown m-1">
    <button
        class="btn btn-sm btn-{} dropdown-toggle"
        type="button"
        data-bs-toggle="dropdown"
        aria-expanded="false">
        {}
    </button>
    <ul class="dropdown-menu dropdown-menu-end">
        {}
    </ul>
</div>
"""

GROUP_LINK = '<li><a class="dropdown-item" href="{}"{}>{}</a></li>\n'


@register.simple_tag(takes_context=True)
def custom_links(context, obj):
    """
    Render all applicable links for the given object.
    """
    content_type = ContentType.objects.get_for_model(obj)
    custom_links = CustomLink.objects.filter(content_type=content_type)
    if not custom_links:
        return ''

    # Pass select context data when rendering the CustomLink
    link_context = {
        'obj': obj,
        'debug': context.get('debug', False),  # django.template.context_processors.debug
        'request': context['request'],  # django.template.context_processors.request
        'user': context['user'],  # django.contrib.auth.context_processors.auth
        'perms': context['perms'],  # django.contrib.auth.context_processors.auth
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
            try:
                text_rendered = render_jinja2(cl.link_text, link_context)
                if text_rendered:
                    link_rendered = render_jinja2(cl.link_url, link_context)
                    link_target = ' target="_blank"' if cl.new_window else ''
                    template_code += LINK_BUTTON.format(
                        link_rendered, link_target, cl.button_class, text_rendered
                    )
            except Exception as e:
                template_code += '<a class="btn btn-sm btn-outline-dark" disabled="disabled" title="{}">' \
                                 '<i class="mdi mdi-alert"></i> {}</a>\n'.format(e, cl.name)

    # Add grouped links to template
    for group, links in group_names.items():

        links_rendered = []

        for cl in links:
            try:
                text_rendered = render_jinja2(cl.link_text, link_context)
                if text_rendered:
                    link_target = ' target="_blank"' if cl.new_window else ''
                    link_rendered = render_jinja2(cl.link_url, link_context)
                    links_rendered.append(
                        GROUP_LINK.format(link_rendered, link_target, text_rendered)
                    )
            except Exception as e:
                links_rendered.append(
                    '<li><a class="dropdown-item" disabled="disabled" title="{}"><span class="text-muted">'
                    '<i class="mdi mdi-alert"></i> {}</span></a></li>'.format(e, cl.name)
                )

        if links_rendered:
            template_code += GROUP_BUTTON.format(
                links[0].button_class, group, ''.join(links_rendered)
            )

    return mark_safe(template_code)
