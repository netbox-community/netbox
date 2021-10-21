import datetime
import decimal
import json
import re
from typing import Dict, Any

import yaml
from django import template
from django.conf import settings
from django.template.defaultfilters import date
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from markdown import markdown

from utilities.forms import get_selected_values, TableConfigForm
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
    return json.dumps(value, ensure_ascii=False, indent=4, sort_keys=True)


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
def humanize_megabytes(mb):
    """
    Express a number of megabytes in the most suitable unit (e.g. gigabytes or terabytes).
    """
    if not mb:
        return ''
    if mb >= 1048576:
        return f'{int(mb / 1048576)} TB'
    if mb >= 1024:
        return f'{int(mb / 1024)} GB'
    return f'{mb} MB'


@register.filter()
def simplify_decimal(value):
    """
    Return the simplest expression of a decimal value. Examples:
      1.00 => '1'
      1.20 => '1.2'
      1.23 => '1.23'
    """
    if type(value) is not decimal.Decimal:
        return value
    return str(value).rstrip('0').rstrip('.')


@register.filter()
def tzoffset(value):
    """
    Returns the hour offset of a given time zone using the current time.
    """
    return datetime.datetime.now(value).strftime('%z')


@register.filter(expects_localtime=True)
def annotated_date(date_value):
    """
    Returns date as HTML span with short date format as the content and the
    (long) date format as the title.
    """
    if not date_value:
        return ''

    if type(date_value) == datetime.date:
        long_ts = date(date_value, 'DATE_FORMAT')
        short_ts = date(date_value, 'SHORT_DATE_FORMAT')
    else:
        long_ts = date(date_value, 'DATETIME_FORMAT')
        short_ts = date(date_value, 'SHORT_DATETIME_FORMAT')

    span = f'<span title="{long_ts}">{short_ts}</span>'

    return mark_safe(span)


@register.simple_tag
def annotated_now():
    """
    Returns the current date piped through the annotated_date filter.
    """
    tzinfo = timezone.get_current_timezone() if settings.USE_TZ else None
    return annotated_date(datetime.datetime.now(tz=tzinfo))


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
def get_docs_url(model):
    """
    Return the documentation URL for the specified model.
    """
    return f'{settings.STATIC_URL}docs/models/{model._meta.app_label}/{model._meta.model_name}/'


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


@register.filter
def status_from_tag(tag: str = "info") -> str:
    """
    Determine Bootstrap theme status/level from Django's Message.level_tag.
    """
    status_map = {
        'warning': 'warning',
        'success': 'success',
        'error': 'danger',
        'debug': 'info',
        'info': 'info',
    }
    return status_map.get(tag.lower(), 'info')


@register.filter
def icon_from_status(status: str = "info") -> str:
    """
    Determine icon class name from Bootstrap theme status/level.
    """
    icon_map = {
        'warning': 'alert',
        'success': 'check-circle',
        'danger': 'alert',
        'info': 'information',
    }
    return icon_map.get(status.lower(), 'information')


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
        bar_class = 'bg-gray'
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
def badge(value, bg_class='secondary', show_empty=False):
    """
    Display the specified number as a badge.
    """
    return {
        'value': value,
        'bg_class': bg_class,
        'show_empty': show_empty,
    }


@register.inclusion_tag('utilities/templatetags/table_config_form.html')
def table_config_form(table, table_name=None):
    return {
        'table_name': table_name or table.__class__.__name__,
        'form': TableConfigForm(table=table),
    }


@register.inclusion_tag('utilities/templatetags/applied_filters.html')
def applied_filters(form, query_params):
    """
    Display the active filters for a given filter form.
    """
    form.is_valid()

    applied_filters = []
    for filter_name in form.changed_data:
        if filter_name not in form.cleaned_data:
            continue

        querydict = query_params.copy()
        if filter_name not in querydict:
            continue

        bound_field = form.fields[filter_name].get_bound_field(form, filter_name)
        querydict.pop(filter_name)
        display_value = ', '.join([str(v) for v in get_selected_values(form, filter_name)])

        applied_filters.append({
            'name': filter_name,
            'value': form.cleaned_data[filter_name],
            'link_url': f'?{querydict.urlencode()}',
            'link_text': f'{bound_field.label}: {display_value}',
        })

    return {
        'applied_filters': applied_filters,
    }
