import datetime
import decimal
import json
from urllib.parse import quote
from typing import Dict, Any

from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import date
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

from utilities.forms import get_selected_values, TableConfigForm
from utilities.utils import get_viewname

register = template.Library()


#
# Filters
#


@register.filter()
def viewname(model, action):
    """
    Return the view name for the given model and action. Does not perform any validation.
    """
    return get_viewname(model, action)


@register.filter()
def validated_viewname(model, action):
    """
    Return the view name for the given model and action if valid, or None if invalid.
    """
    viewname = get_viewname(model, action)

    # Validate the view name
    try:
        reverse(viewname)
        return viewname
    except NoReverseMatch:
        return None


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
    if not mb % 1048576:  # 1024^2
        return f'{int(mb / 1048576)} TB'
    if not mb % 1024:
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

    return mark_safe(f'<span title="{long_ts}">{short_ts}</span>')


@register.simple_tag
def annotated_now():
    """
    Returns the current date piped through the annotated_date filter.
    """
    tzinfo = timezone.get_current_timezone() if settings.USE_TZ else None
    return annotated_date(datetime.datetime.now(tz=tzinfo))


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

    return round(x / y * 100, 1)


@register.filter()
def has_perms(user, permissions_list):
    """
    Return True if the user has *all* permissions in the list.
    """
    return user.has_perms(permissions_list)


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


@register.filter()
def kg_to_pounds(n):
    """
    Convert a weight from kilograms to pounds.
    """
    return float(n) * 2.204623


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
        'danger': 'danger',
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


@register.inclusion_tag('helpers/utilization_graph.html')
def utilization_graph(utilization, warning_threshold=75, danger_threshold=90):
    """
    Display a horizontal bar graph indicating a percentage of utilization.
    """
    if utilization == 100:
        bar_class = 'bg-secondary'
    elif danger_threshold and utilization >= danger_threshold:
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


@register.inclusion_tag('helpers/table_config_form.html')
def table_config_form(table, table_name=None):
    return {
        'table_name': table_name or table.__class__.__name__,
        'form': TableConfigForm(table=table),
    }


@register.inclusion_tag('helpers/applied_filters.html', takes_context=True)
def applied_filters(context, model, form, query_params):
    """
    Display the active filters for a given filter form.
    """
    user = context['request'].user
    form.is_valid()  # Ensure cleaned_data has been set

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

    save_link = None
    if user.has_perm('extras.add_savedfilter') and 'filter_id' not in context['request'].GET:
        content_type = ContentType.objects.get_for_model(model).pk
        parameters = json.dumps(dict(context['request'].GET.lists()))
        url = reverse('extras:savedfilter_add')
        save_link = f"{url}?content_types={content_type}&parameters={quote(parameters)}"

    return {
        'applied_filters': applied_filters,
        'save_link': save_link,
    }
