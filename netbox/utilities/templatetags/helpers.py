import json
from typing import Any
from urllib.parse import quote

from django import template
from django.urls import NoReverseMatch, reverse
from django.utils.html import conditional_escape
from django.utils.translation import gettext_lazy as _

from core.models import ObjectType
from netbox.settings import DISK_BASE_UNIT, RAM_BASE_UNIT
from utilities.forms import TableConfigForm, get_selected_values
from utilities.forms.mixins import FORM_FIELD_LOOKUPS
from utilities.views import get_action_url, get_viewname

__all__ = (
    'action_url',
    'applied_filters',
    'as_range',
    'divide',
    'get_item',
    'get_key',
    'humanize_disk_megabytes',
    'humanize_ram_megabytes',
    'humanize_speed',
    'icon_from_status',
    'kg_to_pounds',
    'meters_to_feet',
    'percentage',
    'querystring',
    'startswith',
    'status_from_tag',
    'table_config_form',
    'utilization_graph',
    'validated_viewname',
    'viewname',
)

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


class ActionURLNode(template.Node):
    """Template node for the {% action_url %} template tag."""

    child_nodelists = ()

    def __init__(self, model, action, kwargs, asvar=None):
        self.model = model
        self.action = action
        self.kwargs = kwargs
        self.asvar = asvar

    def __repr__(self):
        return (
            f"<{self.__class__.__qualname__} "
            f"model='{self.model}' "
            f"action='{self.action}' "
            f"kwargs={repr(self.kwargs)} "
            f"as={repr(self.asvar)}>"
        )

    def render(self, context):
        """
        Render the action URL node.

        Args:
            context: The template context

        Returns:
            The resolved URL or empty string if using 'as' syntax

        Raises:
            NoReverseMatch: If the URL cannot be resolved and not using 'as' syntax
        """
        # Resolve model and kwargs from context
        model = self.model.resolve(context)
        kwargs = {k: v.resolve(context) for k, v in self.kwargs.items()}

        # Get the action URL using the utility function
        try:
            url = get_action_url(model, action=self.action, kwargs=kwargs)
        except NoReverseMatch:
            if self.asvar is None:
                raise
            url = ""

        # Handle variable assignment or return escaped URL
        if self.asvar:
            context[self.asvar] = url
            return ""

        return conditional_escape(url) if context.autoescape else url


@register.tag
def action_url(parser, token):
    """
    Return an absolute URL matching the given model and action.

    This is a way to define links that aren't tied to a particular URL
    configuration::

        {% action_url model "action_name" %}

        or

        {% action_url model "action_name" pk=object.pk %}

        or

        {% action_url model "action_name" pk=object.pk as variable_name %}

    The first argument is a model or instance. The second argument is the action name.
    Additional keyword arguments can be passed for URL parameters.

    For example, if you have a Device model and want to link to its edit action::

        {% action_url device "edit" %}

    This will generate a URL like ``/dcim/devices/123/edit/``.

    You can also pass additional parameters::

        {% action_url device "journal" pk=device.pk %}

    Or assign the URL to a variable::

        {% action_url device "edit" as edit_url %}
    """
    # Parse the token contents
    bits = token.split_contents()
    if len(bits) < 3:
        raise template.TemplateSyntaxError(
            f"'{bits[0]}' takes at least two arguments, a model and an action."
        )

    # Extract model and action
    model = parser.compile_filter(bits[1])
    action = bits[2].strip('"\'')  # Remove quotes from literal string
    kwargs = {}
    asvar = None
    bits = bits[3:]

    # Handle 'as' syntax for variable assignment
    if len(bits) >= 2 and bits[-2] == "as":
        asvar = bits[-1]
        bits = bits[:-2]

    # Parse remaining arguments as kwargs
    for bit in bits:
        if '=' not in bit:
            raise template.TemplateSyntaxError(
                f"'{token.contents.split()[0]}' keyword arguments must be in the format 'name=value'"
            )
        name, value = bit.split('=', 1)
        kwargs[name] = parser.compile_filter(value)

    return ActionURLNode(model, action, kwargs, asvar)


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
    if speed >= 1000000 and speed % 1000000 == 0:
        return '{} Gbps'.format(int(speed / 1000000))
    if speed >= 1000 and speed % 1000 == 0:
        return '{} Mbps'.format(int(speed / 1000))
    if speed >= 1000:
        return '{} Mbps'.format(float(speed) / 1000)
    return '{} Kbps'.format(speed)


def _humanize_megabytes(mb, divisor=1000):
    """
    Express a number of megabytes in the most suitable unit (e.g. gigabytes, terabytes, etc.).
    """
    if not mb:
        return ""

    PB_SIZE = divisor**3
    TB_SIZE = divisor**2
    GB_SIZE = divisor

    if mb >= PB_SIZE:
        return f"{mb / PB_SIZE:.2f} PB"
    if mb >= TB_SIZE:
        return f"{mb / TB_SIZE:.2f} TB"
    if mb >= GB_SIZE:
        return f"{mb / GB_SIZE:.2f} GB"
    return f"{mb} MB"


@register.filter()
def humanize_disk_megabytes(mb):
    """
    Express a number of megabytes in the most suitable unit (e.g. gigabytes, terabytes, etc.).
    Use the DISK_BASE_UNIT setting to determine the divisor. Default is 1000.
    """
    return _humanize_megabytes(mb, DISK_BASE_UNIT)


@register.filter()
def humanize_ram_megabytes(mb):
    """
    Express a number of megabytes in the most suitable unit (e.g. gigabytes, terabytes, etc.).
    Use the RAM_BASE_UNIT setting to determine the divisor. Default is 1000.
    """
    return _humanize_megabytes(mb, RAM_BASE_UNIT)


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
def get_key(value: dict, arg: str) -> Any:
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

        # Check if this is a modifier-enhanced field
        # Field may be in querydict as field__lookup instead of field
        param_name = None
        if filter_name in querydict:
            param_name = filter_name
        else:
            # Check for modifier variants (field__ic, field__isw, etc.)
            for key in querydict.keys():
                if key.startswith(f'{filter_name}__'):
                    param_name = key
                    break

        if param_name is None:
            continue

        # Skip saved filters, as they're displayed alongside the quick search widget
        if filter_name == 'filter_id':
            continue

        bound_field = form.fields[filter_name].get_bound_field(form, filter_name)
        querydict.pop(param_name)

        # Extract modifier from parameter name (e.g., "serial__ic" → "ic")
        if '__' in param_name:
            modifier = param_name.split('__', 1)[1]
        else:
            modifier = 'exact'

        # Get display value
        display_value = ', '.join([str(v) for v in get_selected_values(form, filter_name)])

        # Get the correct lookup label for this field's type
        lookup_label = None
        if modifier != 'exact':
            field = form.fields[filter_name]
            for field_class in field.__class__.__mro__:
                if field_lookups := FORM_FIELD_LOOKUPS.get(field_class):
                    for lookup_code, label in field_lookups:
                        if lookup_code == modifier:
                            lookup_label = label
                            break
                    if lookup_label:
                        break

        # Special handling for empty lookup (boolean value)
        if modifier == 'empty':
            if display_value.lower() in ('true', '1'):
                link_text = f'{bound_field.label} {_("is empty")}'
            else:
                link_text = f'{bound_field.label} {_("is not empty")}'
        elif lookup_label:
            link_text = f'{bound_field.label} {lookup_label}: {display_value}'
        else:
            link_text = f'{bound_field.label}: {display_value}'

        applied_filters.append({
            'name': param_name,  # Use actual param name for removal link
            'value': form.cleaned_data.get(filter_name),
            'link_url': f'?{querydict.urlencode()}',
            'link_text': link_text,
        })

    save_link = None
    if user.has_perm('extras.add_savedfilter') and 'filter_id' not in context['request'].GET:
        object_type = ObjectType.objects.get_for_model(model).pk
        parameters = json.dumps(dict(context['request'].GET.lists()))
        url = reverse('extras:savedfilter_add')
        save_link = f"{url}?object_types={object_type}&parameters={quote(parameters)}"

    return {
        'applied_filters': applied_filters,
        'save_link': save_link,
    }
