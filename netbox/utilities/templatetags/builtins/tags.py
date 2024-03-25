from django import template

from extras.choices import CustomFieldTypeChoices
from utilities.querydict import dict_to_querydict

__all__ = (
    'badge',
    'checkmark',
    'copy_content',
    'customfield_value',
    'formaction',
    'tag',
)

register = template.Library()


@register.inclusion_tag('builtins/tag.html')
def tag(value, viewname=None):
    """
    Display a tag, optionally linked to a filtered list of objects.

    Args:
        value: A Tag instance
        viewname: If provided, the tag will be a hyperlink to the specified view's URL
    """
    return {
        'tag': value,
        'viewname': viewname,
    }


@register.inclusion_tag('builtins/customfield_value.html')
def customfield_value(customfield, value):
    """
    Render a custom field value according to the field type.

    Args:
        customfield: A CustomField instance
        value: The custom field value applied to an object
    """
    if value:
        if customfield.type == CustomFieldTypeChoices.TYPE_SELECT:
            value = customfield.get_choice_label(value)
        elif customfield.type == CustomFieldTypeChoices.TYPE_MULTISELECT:
            value = [customfield.get_choice_label(v) for v in value]
    return {
        'customfield': customfield,
        'value': value,
    }


@register.inclusion_tag('builtins/badge.html')
def badge(value, bg_color=None, show_empty=False):
    """
    Display the specified number as a badge.

    Args:
        value: The value to be displayed within the badge
        bg_color: Background color CSS name
        show_empty: If true, display the badge even if value is None or zero
    """
    return {
        'value': value,
        'bg_color': bg_color or 'secondary',
        'show_empty': show_empty,
    }


@register.inclusion_tag('builtins/checkmark.html')
def checkmark(value, show_false=True, true='Yes', false='No'):
    """
    Display either a green checkmark or red X to indicate a boolean value.

    Args:
        value: True or False
        show_false: Show false values
        true: Text label for true values
        false: Text label for false values
    """
    return {
        'value': bool(value),
        'show_false': show_false,
        'true_label': true,
        'false_label': false,
    }


@register.inclusion_tag('builtins/copy_content.html')
def copy_content(target, prefix=None, color='primary', classes=None):
    """
    Display a copy button to copy the content of a field.
    """
    return {
        'target': f'#{prefix or ""}{target}',
        'color': f'btn-{color}',
        'classes': classes or '',
    }


@register.inclusion_tag('builtins/htmx_table.html', takes_context=True)
def htmx_table(context, viewname, return_url=None, **kwargs):
    """
    Embed an object list table retrieved using HTMX. Any extra keyword arguments are passed as URL query parameters.

    Args:
        context: The current request context
        viewname: The name of the view to use for the HTMX request (e.g. `dcim:site_list`)
        return_url: The URL to pass as the `return_url`. If not provided, the current request's path will be used.
    """
    url_params = dict_to_querydict(kwargs)
    url_params['return_url'] = return_url or context['request'].path
    return {
        'viewname': viewname,
        'url_params': url_params,
    }


@register.simple_tag(takes_context=True)
def formaction(context):
    """
    Replace the 'formaction' attribute on an HTML element with the appropriate HTMX attributes
    if HTMX navigation is enabled (per the user's preferences).
    """
    if context.get('htmx_navigation', False):
        return 'hx-push-url="true" hx-post'
    return 'formaction'
