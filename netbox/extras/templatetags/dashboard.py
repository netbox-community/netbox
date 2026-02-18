from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

register = template.Library()


@register.simple_tag(takes_context=True)
def render_widget(context, widget):
    request = context['request']

    try:
        return widget.render(request)
    except Exception as e:
        message1 = _('An error was encountered when attempting to render this widget:')
        message2 = _('Please try reconfiguring the widget, or remove it from your dashboard.')
        return mark_safe(f"""
            <p>
              <span class="text-danger"><i class="mdi mdi-alert"></i></span>
              {message1}
            </p>
            <p class="font-monospace ps-3">{e}</p>
            <p>{message2}</p>
        """)
