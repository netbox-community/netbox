import datetime
import json
import re
from typing import Dict, Any

import yaml
from django import template
from django.conf import settings
from django.urls import NoReverseMatch, reverse
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from markdown import markdown

from utilities.forms import TableConfigForm
from utilities.utils import foreground_color

register = template.Library()


#
# Filters
#

@register.filter()
def placeholder(value):
    """
    Render a muted placeholder if value equates to False.
    """
    if value:
        return value
    placeholder = '<span class="text-muted">&mdash;</span>'
    return mark_safe(placeholder)


@register.filter(is_safe=True)
def render_markdown(value):
    """
    Render text as Markdown
    """
    # Strip HTML tags
    value = strip_tags(value)

    # Sanitize Markdown links
    schemes = '|'.join(settings.ALLOWED_URL_SCHEMES)
    pattern = fr'\[(.+)\]\((?!({schemes})).*:(.+)\)'
    value = re.sub(pattern, '[\\1](\\3)', value, flags=re.IGNORECASE)

    # Render Markdown
    html = markdown(value, extensions=['fenced_code', 'tables'])

    return mark_safe(html)


@register.filter()
def render_json(value):
    """
    Render a dictionary as formatted JSON.
    """
    return json.dumps(value, indent=4, sort_keys=True)


@register.filter()
def render_yaml(value):
    """
    Render a dictionary as formatted YAML.
    """
    return yaml.dump(json.loads(json.dumps(value)))


@register.filter()
def meta(obj, attr):
    """
    Return the specified Meta attribute of a model. This is needed because Django does not permit templates
    to access attributes which begin with an underscore (e.g. _meta).
    """
    return getattr(obj._meta, attr, '')


@register.filter()
def viewname(model, action):
    """
    Return the view name for the given model and action. Does not perform any validation.
    """
    return f'{model._meta.app_label}:{model._meta.model_name}_{action}'


@register.filter()
def validated_viewname(model, action):
    """
    Return the view name for the given model and action if valid, or None if invalid.
    """
    viewname = f'{model._meta.app_label}:{model._meta.model_name}_{action}'
    try:
        # Validate and return the view name. We don't return the actual URL yet because many of the templates
        # are written to pass a name to {% url %}.
        reverse(viewname)
        return viewname
    except NoReverseMatch:
        return None


@register.filter()
def bettertitle(value):
    """
    Alternative to the builtin title(); uppercases words without replacing letters that are already uppercase.
    """
    return ' '.join([w[0].upper() + w[1:] for w in value.split()])


@register.filter()
def humanize_speed(speed):
    """
    Humanize speeds given in Kbps. Examples:

        1544 => "1.544 Mbps"
        100000 => "100 Mbps"
        10000000 => "10 Gbps"
    """
    if not speed:
        return ''
    if speed >= 1000000000 and speed % 1000000000 == 0:
        return '{} Tbps'.format(int(speed / 1000000000))
    elif speed >= 1000000 and speed % 1000000 == 0:
        return '{} Gbps'.format(int(speed / 1000000))
    elif speed >= 1000 and speed % 1000 == 0:
        return '{} Mbps'.format(int(speed / 1000))
    elif speed >= 1000:
        return '{} Mbps'.format(float(speed) / 1000)
    else:
        return '{} Kbps'.format(speed)


@register.filter()
def tzoffset(value):
    """
    Returns the hour offset of a given time zone using the current time.
    """
    return datetime.datetime.now(value).strftime('%z')


@register.filter()
def fgcolor(value):
    """
    Return black (#000000) or white (#ffffff) given an arbitrary background color in RRGGBB format.
    """
    value = value.lower().strip('#')
    if not re.match('^[0-9a-f]{6}$', value):
        return ''
    return '#{}'.format(foreground_color(value))


@register.filter()
def divide(x, y):
    """
    Return x/y (rounded).
    """
    if x is None or y is None:
        return None
    return round(x / y)


@register.filter()
def percentage(x, y):
    """
    Return x/y as a percentage.
    """
    if x is None or y is None:
        return None
    return round(x / y * 100)


@register.filter()
def get_docs(model):
    """
    Render and return documentation for the specified model.
    """
    path = '{}/models/{}/{}.md'.format(
        settings.DOCS_ROOT,
        model._meta.app_label,
        model._meta.model_name
    )
    try:
        with open(path, encoding='utf-8') as docfile:
            content = docfile.read()
    except FileNotFoundError:
        return "Unable to load documentation, file not found: {}".format(path)
    except IOError:
        return "Unable to load documentation, error reading file: {}".format(path)

    # Render Markdown with the admonition extension
    content = markdown(content, extensions=['admonition', 'fenced_code', 'tables'])

    return mark_safe(content)


@register.filter()
def has_perms(user, permissions_list):
    """
    Return True if the user has *all* permissions in the list.
    """
    return user.has_perms(permissions_list)


@register.filter()
def split(string, sep=','):
    """
    Split a string by the given value (default: comma)
    """
    return string.split(sep)


@register.filter()
def as_range(n):
    """
    Return a range of n items.
    """
    try:
        int(n)
    except TypeError:
        return list()
    return range(n)


@register.filter()
def meters_to_feet(n):
    """
    Convert a length from meters to feet.
    """
    return float(n) * 3.28084


@register.filter("startswith")
def startswith(text: str, starts: str) -> bool:
    """
    Template implementation of `str.startswith()`.
    """
    if isinstance(text, str):
        return text.startswith(starts)
    return False


@register.filter
def get_key(value: Dict, arg: str) -> Any:
    """
    Template implementation of `dict.get()`, for accessing dict values
    by key when the key is not able to be used in a template. For
    example, `{"ui.colormode": "dark"}`.
    """
    return value.get(arg, None)


@register.filter
def get_item(value: object, attr: str) -> Any:
    """
    Template implementation of `__getitem__`, for accessing the `__getitem__` method
    of a class from a template.
    """
    return value[attr]


#
# Tags
#

@register.simple_tag()
def querystring(request, **kwargs):
    """
    Append or update the page number in a querystring.
    """
    querydict = request.GET.copy()
    for k, v in kwargs.items():
        if v is not None:
            querydict[k] = str(v)
        elif k in querydict:
            querydict.pop(k)
    querystring = querydict.urlencode(safe='/')
    if querystring:
        return '?' + querystring
    else:
        return ''


@register.inclusion_tag('utilities/templatetags/utilization_graph.html')
def utilization_graph(utilization, warning_threshold=75, danger_threshold=90):
    """
    Display a horizontal bar graph indicating a percentage of utilization.
    """
    if danger_threshold and utilization >= danger_threshold:
        bar_class = 'bg-danger'
    elif warning_threshold and utilization >= warning_threshold:
        bar_class = 'bg-warning'
    elif warning_threshold or danger_threshold:
        bar_class = 'bg-success'
    else:
        bar_class = 'bg-default'
    return {
        'utilization': utilization,
        'bar_class': bar_class,
    }


@register.inclusion_tag('utilities/templatetags/tag.html')
def tag(tag, url_name=None):
    """
    Display a tag, optionally linked to a filtered list of objects.
    """
    return {
        'tag': tag,
        'url_name': url_name,
    }


@register.inclusion_tag('utilities/templatetags/badge.html')
def badge(value, show_empty=False):
    """
    Display the specified number as a badge.
    """
    return {
        'value': value,
        'show_empty': show_empty,
    }


@register.inclusion_tag('utilities/templatetags/table_config_form.html')
def table_config_form(table, table_name=None):
    return {
        'table_name': table_name or table.__class__.__name__,
        'table_config_form': TableConfigForm(table=table),
    }
