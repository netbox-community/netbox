from django import template


register = template.Library()


@register.inclusion_tag('utilities/render_field.html')
def render_field(field):
    """
    Render a single form field from template
    """
    return {
        'field': field,
    }


@register.inclusion_tag('utilities/render_custom_fields.html')
def render_custom_fields(form):
    """
    Render all custom fields in a form
    """
    return {
        'form': form,
    }


@register.inclusion_tag('utilities/render_form.html')
def render_form(form):
    """
    Render an entire form from template
    """
    return {
        'form': form,
    }


@register.filter(name='widget_type')
def widget_type(field):
    """
    Return the widget type
    """
    try:
        return field.field.widget.__class__.__name__.lower()
    except AttributeError:
        return None
