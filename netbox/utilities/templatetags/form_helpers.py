import warnings
from collections.abc import Sequence
from typing import Any, NamedTuple

from django import forms, template
from django.conf import settings

from utilities.forms.rendering import InlineFields, M2MAddRemoveFields, ObjectAttribute, TabbedGroups

__all__ = (
    'any_required',
    'getfield',
    'render_custom_fields',
    'render_errors',
    'render_field',
    'render_field_with_aria',
    'render_form',
    'widget_type',
)


register = template.Library()


class FieldsetRow(NamedTuple):
    """
    A single row within a rendered fieldset. `layout` determines how the row's items are
    rendered by the template (e.g. 'field', 'inline', 'tabs', 'attribute').
    """
    layout: str
    items: Sequence
    title: Any = None
    help_text: Any = None


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


@register.filter()
def any_required(fields):
    """
    Return True if any of the given bound form fields is required.
    """
    return any(getattr(f, 'field', None) and f.field.required for f in fields)


@register.filter(name='widget_type')
def widget_type(field):
    """
    Return the widget type
    """
    if hasattr(field, 'widget'):
        return field.widget.__class__.__name__.lower()
    if hasattr(field, 'field'):
        return field.field.widget.__class__.__name__.lower()
    return None


@register.simple_tag
def render_field_with_aria(field, has_helptext=None, element_id=None):
    """Render a bound form field with aria-describedby/aria-invalid/aria-label wired up.

    Pass ``element_id`` to override the widget's HTML ``id``. This is needed when the same
    field is rendered more than once on a page (e.g. the saved-filter selector, which appears
    both in the list controls and the filter drawer), to keep element IDs unique so that label
    associations resolve correctly for assistive technology.
    """
    if has_helptext is None:
        has_helptext = bool(field.help_text)
    widget_attrs = field.field.widget.attrs
    described_by = []
    if field.errors:
        described_by.append(f'{field.auto_id}_errors')
    if has_helptext:
        described_by.append(f'{field.auto_id}_helptext')
    extra_attrs = {}
    if element_id:
        extra_attrs['id'] = element_id
    if described_by:
        # Merge with any aria-describedby already set on the widget so we
        # append to (rather than clobber) descriptions defined elsewhere.
        existing = widget_attrs.get('aria-describedby', '').strip()
        extra_attrs['aria-describedby'] = ' '.join(
            filter(None, [existing, *described_by])
        )
    if field.errors:
        extra_attrs['aria-invalid'] = 'true'
    # Mirror field.label onto <select> widgets hidden by Tom Select
    # (ts-hidden-accessible, tabindex=-1), where scanners drop the <label for=>
    # association. Skip selects opted out of Tom Select (``.no-ts`` class or a
    # ``size`` attribute) since they stay visible and keep their association.
    #
    # When a field has no label at all (label=''), we deliberately do NOT
    # synthesize one from the field name: that would inject an untranslated
    # English string into the rendered DOM and degrade the experience for
    # non-English locales. In DEBUG we emit a warning so developers add a
    # proper translated label on the field.
    if 'aria-label' not in widget_attrs:
        if isinstance(field.field.widget, forms.Select) and field.label:
            tom_select_excluded = (
                'no-ts' in widget_attrs.get('class', '').split()
                or 'size' in widget_attrs
            )
            if not tom_select_excluded:
                extra_attrs['aria-label'] = str(field.label)
        elif not field.label and settings.DEBUG:
            form_name = getattr(getattr(field, 'form', None), '__class__', type(None)).__name__
            warnings.warn(
                f"Form field {form_name}.{field.name} has no label; no aria-label "
                "will be set. Add a translated label to the field for proper "
                "accessibility.",
                stacklevel=2,
            )
    return field.as_widget(attrs=extra_attrs)


#
# Inclusion tags
#

@register.inclusion_tag('form_helpers/render_fieldset.html')
def render_fieldset(form, fieldset):
    """
    Render a group set of fields.
    """
    rows = []
    for item in fieldset.items:

        # Multiple fields side-by-side
        if type(item) is InlineFields:
            fields = [
                form[name] for name in item.fields if name in form.fields
            ]
            rows.append(
                FieldsetRow('inline', fields, title=item.label, help_text=item.help_text)
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
                FieldsetRow('tabs', tabs)
            )

        elif type(item) is M2MAddRemoveFields:
            if item.name in form.fields:
                # Simple mode: render a single multi-select field
                rows.append(
                    FieldsetRow('field', [form[item.name]])
                )
            else:
                # Add/remove mode: render separate add and remove fields
                for field_name in (f'add_{item.name}', f'remove_{item.name}'):
                    if field_name in form.fields:
                        rows.append(
                            FieldsetRow('field', [form[field_name]])
                        )

        elif type(item) is ObjectAttribute:
            value = getattr(form.instance, item.name)
            label = value._meta.verbose_name if hasattr(value, '_meta') else item.name
            rows.append(
                FieldsetRow('attribute', [value], title=label.title())
            )

        # A single form field
        elif item in form.fields:
            field = form[item]
            # Annotate nullability for bulk editing
            if field.name in getattr(form, 'nullable_fields', []):
                field._nullable = True
            rows.append(
                FieldsetRow('field', [field])
            )

    return {
        'heading': fieldset.name,
        'html_id': fieldset.html_id,
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
        'bulk_nullable': bulk_nullable or getattr(field, '_nullable', False),
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
