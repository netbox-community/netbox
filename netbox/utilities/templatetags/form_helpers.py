from django import template

from utilities.forms.rendering import FieldSet, InlineFields, ObjectAttribute, TabbedGroups

__all__ = (
    'getfield',
    'render_custom_fields',
    'render_errors',
    'render_field',
    'render_form',
    'widget_type',
)


register = template.Library()


#
# Filters
#

@register.filter()
def getfield(form, fieldname):
    """
    Return the specified bound field of a Form.
    """
    try:
        return form[fieldname]
    except KeyError:
        return None


@register.filter(name='widget_type')
def widget_type(field):
    """
    Return the widget type
    """
    if hasattr(field, 'widget'):
        return field.widget.__class__.__name__.lower()
    elif hasattr(field, 'field'):
        return field.field.widget.__class__.__name__.lower()
    else:
        return None


#
# Inclusion tags
#

@register.inclusion_tag('form_helpers/render_fieldset.html')
def render_fieldset(form, fieldset):
    """
    Render a group set of fields.
    """
    # Handle legacy tuple-based fieldset definitions, e.g. (_('Label'), ('field1, 'field2', 'field3'))
    if type(fieldset) is not FieldSet:
        name, fields = fieldset
        fieldset = FieldSet(*fields, name=name)

    rows = []
    for item in fieldset.fields:

        # Multiple fields side-by-side
        if type(item) is InlineFields:
            fields = [
                form[name] for name in item.fields if name in form.fields
            ]
            rows.append(
                ('inline', item.label, fields)
            )

        # Tabbed groups of fields
        elif type(item) is TabbedGroups:
            tabs = [
                {
                    'id': tab['id'],
                    'title': tab['title'],
                    'active': bool(form.initial.get(tab['fields'][0], False)),
                    'fields': [form[name] for name in tab['fields'] if name in form.fields]
                } for tab in item.tabs
            ]
            # If none of the tabs has been marked as active, activate the first one
            if not any(tab['active'] for tab in tabs):
                tabs[0]['active'] = True
            rows.append(
                ('tabs', None, tabs)
            )

        elif type(item) is ObjectAttribute:
            value = getattr(form.instance, item.name)
            label = value._meta.verbose_name if hasattr(value, '_meta') else item.name
            rows.append(
                ('attribute', label.title(), [value])
            )

        # A single form field
        elif item in form.fields:
            rows.append(
                ('field', None, [form[item]])
            )

    return {
        'heading': fieldset.name,
        'rows': rows,
    }


@register.inclusion_tag('form_helpers/render_field.html')
def render_field(field, bulk_nullable=False, label=None):
    """
    Render a single form field from template
    """
    return {
        'field': field,
        'label': label or field.label,
        'bulk_nullable': bulk_nullable,
    }


@register.inclusion_tag('form_helpers/render_custom_fields.html')
def render_custom_fields(form):
    """
    Render all custom fields in a form
    """
    return {
        'form': form,
    }


@register.inclusion_tag('form_helpers/render_form.html')
def render_form(form):
    """
    Render an entire form from template
    """
    return {
        'form': form,
    }


@register.inclusion_tag('form_helpers/render_errors.html')
def render_errors(form):
    """
    Render form errors, if they exist.
    """
    return {
        "form": form
    }
