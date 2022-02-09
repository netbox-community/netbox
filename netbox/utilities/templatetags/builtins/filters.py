import datetime
import json
import re

import yaml
from django import template
from django.contrib.contenttypes.models import ContentType
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from markdown import markdown

from netbox.config import get_config
from utilities.markdown import StrikethroughExtension
from utilities.utils import foreground_color

register = template.Library()


#
# General
#

@register.filter()
def bettertitle(value):
    """
    Alternative to the builtin title(). Ensures that the first letter of each word is uppercase but retains the
    original case of all others.
    """
    return ' '.join([w[0].upper() + w[1:] for w in value.split()])


@register.filter()
def fgcolor(value, dark='000000', light='ffffff'):
    """
    Return black (#000000) or white (#ffffff) given an arbitrary background color in RRGGBB format. The foreground
    color with the better contrast is returned.

    Args:
        value: The background color
        dark: The foreground color to use for light backgrounds
        light: The foreground color to use for dark backgrounds
    """
    value = value.lower().strip('#')
    if not re.match('^[0-9a-f]{6}$', value):
        return ''
    return f'#{foreground_color(value, dark, light)}'


@register.filter()
def meta(model, attr):
    """
    Return the specified Meta attribute of a model. This is needed because Django does not permit templates
    to access attributes which begin with an underscore (e.g. _meta).

    Args:
        model: A Django model class or instance
        attr: The attribute name
    """
    return getattr(model._meta, attr, '')


@register.filter()
def placeholder(value):
    """
    Render a muted placeholder if the value equates to False.
    """
    if value not in ('', None):
        return value
    placeholder = '<span class="text-muted">&mdash;</span>'
    return mark_safe(placeholder)


@register.filter()
def split(value, separator=','):
    """
    Wrapper for Python's `split()` string method.

    Args:
        value: A string
        separator: String on which the value will be split
    """
    return value.split(separator)


@register.filter()
def tzoffset(value):
    """
    Returns the hour offset of a given time zone using the current time.
    """
    return datetime.datetime.now(value).strftime('%z')


#
# Content types
#

@register.filter()
def content_type(model):
    """
    Return the ContentType for the given object.
    """
    return ContentType.objects.get_for_model(model)


@register.filter()
def content_type_id(model):
    """
    Return the ContentType ID for the given object.
    """
    content_type = ContentType.objects.get_for_model(model)
    if content_type:
        return content_type.pk
    return None


#
# Rendering
#

@register.filter('markdown', is_safe=True)
def render_markdown(value):
    """
    Render a string as Markdown. This filter is invoked as "markdown":

        {{ md_source_text|markdown }}
    """
    schemes = '|'.join(get_config().ALLOWED_URL_SCHEMES)

    # Strip HTML tags
    value = strip_tags(value)

    # Sanitize Markdown links
    pattern = fr'\[([^\]]+)\]\((?!({schemes})).*:(.+)\)'
    value = re.sub(pattern, '[\\1](\\3)', value, flags=re.IGNORECASE)

    # Sanitize Markdown reference links
    pattern = fr'\[(.+)\]:\s*(?!({schemes}))\w*:(.+)'
    value = re.sub(pattern, '[\\1]: \\3', value, flags=re.IGNORECASE)

    # Render Markdown
    html = markdown(value, extensions=['fenced_code', 'tables', StrikethroughExtension()])

    # If the string is not empty wrap it in rendered-markdown to style tables
    if html:
        html = f'<div class="rendered-markdown">{html}</div>'

    return mark_safe(html)


@register.filter('json')
def render_json(value):
    """
    Render a dictionary as formatted JSON. This filter is invoked as "json":

        {{ data_dict|json }}
    """
    return json.dumps(value, ensure_ascii=False, indent=4, sort_keys=True)


@register.filter('yaml')
def render_yaml(value):
    """
    Render a dictionary as formatted YAML. This filter is invoked as "yaml":

        {{ data_dict|yaml }}
    """
    return yaml.dump(json.loads(json.dumps(value)))
