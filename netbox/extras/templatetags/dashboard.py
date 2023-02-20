from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def render_widget(context, widget):
    request = context['request']

    return widget.render(request)
