import datetime
import decimal
from itertools import count, groupby
from urllib.parse import urlencode

import nh3
from django.db.models import Count, ManyToOneRel, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.http import QueryDict
from django.utils import timezone
from django.utils.datastructures import MultiValueDict
from django.utils.timezone import localtime
from jinja2.sandbox import SandboxedEnvironment

from netbox.config import get_config
from .constants import HTML_ALLOWED_ATTRIBUTES, HTML_ALLOWED_TAGS
from .string import title


def csv_format(data):
    """
    Encapsulate any data which contains a comma within double quotes.
    """
    csv = []
    for value in data:

        # Represent None or False with empty string
        if value is None or value is False:
            csv.append('')
            continue

        # Convert dates to ISO format
        if isinstance(value, (datetime.date, datetime.datetime)):
            value = value.isoformat()

        # Force conversion to string first so we can check for any commas
        if not isinstance(value, str):
            value = '{}'.format(value)

        # Double-quote the value if it contains a comma or line break
        if ',' in value or '\n' in value:
            value = value.replace('"', '""')  # Escape double-quotes
            csv.append('"{}"'.format(value))
        else:
            csv.append('{}'.format(value))

    return ','.join(csv)


def foreground_color(bg_color, dark='000000', light='ffffff'):
    """
    Return the ideal foreground color (dark or light) for a given background color in hexadecimal RGB format.

    :param dark: RBG color code for dark text
    :param light: RBG color code for light text
    """
    THRESHOLD = 150
    bg_color = bg_color.strip('#')
    r, g, b = [int(bg_color[c:c + 2], 16) for c in (0, 2, 4)]
    if r * 0.299 + g * 0.587 + b * 0.114 > THRESHOLD:
        return dark
    else:
        return light


def dynamic_import(name):
    """
    Dynamically import a class from an absolute path string
    """
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def count_related(model, field):
    """
    Return a Subquery suitable for annotating a child object count.
    """
    subquery = Subquery(
        model.objects.filter(
            **{field: OuterRef('pk')}
        ).order_by().values(
            field
        ).annotate(
            c=Count('*')
        ).values('c')
    )

    return Coalesce(subquery, 0)


def dict_to_filter_params(d, prefix=''):
    """
    Translate a dictionary of attributes to a nested set of parameters suitable for QuerySet filtering. For example:

        {
            "name": "Foo",
            "rack": {
                "facility_id": "R101"
            }
        }

    Becomes:

        {
            "name": "Foo",
            "rack__facility_id": "R101"
        }

    And can be employed as filter parameters:

        Device.objects.filter(**dict_to_filter(attrs_dict))
    """
    params = {}
    for key, val in d.items():
        k = prefix + key
        if isinstance(val, dict):
            params.update(dict_to_filter_params(val, k + '__'))
        else:
            params[k] = val
    return params


def dict_to_querydict(d, mutable=True):
    """
    Create a QueryDict instance from a regular Python dictionary.
    """
    qd = QueryDict(mutable=True)
    for k, v in d.items():
        item = MultiValueDict({k: v}) if isinstance(v, (list, tuple, set)) else {k: v}
        qd.update(item)
    if not mutable:
        qd._mutable = False
    return qd


def normalize_querydict(querydict):
    """
    Convert a QueryDict to a normal, mutable dictionary, preserving list values. For example,

        QueryDict('foo=1&bar=2&bar=3&baz=')

    becomes:

        {'foo': '1', 'bar': ['2', '3'], 'baz': ''}

    This function is necessary because QueryDict does not provide any built-in mechanism which preserves multiple
    values.
    """
    return {
        k: v if len(v) > 1 else v[0] for k, v in querydict.lists()
    }


def deepmerge(original, new):
    """
    Deep merge two dictionaries (new into original) and return a new dict
    """
    merged = dict(original)
    for key, val in new.items():
        if key in original and isinstance(original[key], dict) and val and isinstance(val, dict):
            merged[key] = deepmerge(original[key], val)
        else:
            merged[key] = val
    return merged


def drange(start, end, step=decimal.Decimal(1)):
    """
    Decimal-compatible implementation of Python's range()
    """
    start, end, step = decimal.Decimal(start), decimal.Decimal(end), decimal.Decimal(step)
    if start < end:
        while start < end:
            yield start
            start += step
    else:
        while start > end:
            yield start
            start += step


def render_jinja2(template_code, context):
    """
    Render a Jinja2 template with the provided context. Return the rendered content.
    """
    environment = SandboxedEnvironment()
    environment.filters.update(get_config().JINJA2_FILTERS)
    return environment.from_string(source=template_code).render(**context)


def prepare_cloned_fields(instance):
    """
    Generate a QueryDict comprising attributes from an object's clone() method.
    """
    # Generate the clone attributes from the instance
    if not hasattr(instance, 'clone'):
        return QueryDict(mutable=True)
    attrs = instance.clone()

    # Prepare querydict parameters
    params = []
    for key, value in attrs.items():
        if type(value) in (list, tuple):
            params.extend([(key, v) for v in value])
        elif value not in (False, None):
            params.append((key, value))
        else:
            params.append((key, ''))

    # Return a QueryDict with the parameters
    return QueryDict(urlencode(params), mutable=True)


def shallow_compare_dict(source_dict, destination_dict, exclude=tuple()):
    """
    Return a new dictionary of the different keys. The values of `destination_dict` are returned. Only the equality of
    the first layer of keys/values is checked. `exclude` is a list or tuple of keys to be ignored.
    """
    difference = {}

    for key, value in destination_dict.items():
        if key in exclude:
            continue
        if source_dict.get(key) != value:
            difference[key] = value

    return difference


def flatten_dict(d, prefix='', separator='.'):
    """
    Flatten netsted dictionaries into a single level by joining key names with a separator.

    :param d: The dictionary to be flattened
    :param prefix: Initial prefix (if any)
    :param separator: The character to use when concatenating key names
    """
    ret = {}
    for k, v in d.items():
        key = separator.join([prefix, k]) if prefix else k
        if type(v) is dict:
            ret.update(flatten_dict(v, prefix=key, separator=separator))
        else:
            ret[key] = v
    return ret


def array_to_ranges(array):
    """
    Convert an arbitrary array of integers to a list of consecutive values. Nonconsecutive values are returned as
    single-item tuples. For example:
        [0, 1, 2, 10, 14, 15, 16] => [(0, 2), (10,), (14, 16)]"
    """
    group = (
        list(x) for _, x in groupby(sorted(array), lambda x, c=count(): next(c) - x)
    )
    return [
        (g[0], g[-1])[:len(g)] for g in group
    ]


def array_to_string(array):
    """
    Generate an efficient, human-friendly string from a set of integers. Intended for use with ArrayField.
    For example:
        [0, 1, 2, 10, 14, 15, 16] => "0-2, 10, 14-16"
    """
    ret = []
    ranges = array_to_ranges(array)
    for value in ranges:
        if len(value) == 1:
            ret.append(str(value[0]))
        else:
            ret.append(f'{value[0]}-{value[1]}')
    return ', '.join(ret)


def content_type_name(ct, include_app=True):
    """
    Return a human-friendly ContentType name (e.g. "DCIM > Site").
    """
    try:
        meta = ct.model_class()._meta
        app_label = title(meta.app_config.verbose_name)
        model_name = title(meta.verbose_name)
        if include_app:
            return f'{app_label} > {model_name}'
        return model_name
    except AttributeError:
        # Model no longer exists
        return f'{ct.app_label} > {ct.model}'


def content_type_identifier(ct):
    """
    Return a "raw" ContentType identifier string suitable for bulk import/export (e.g. "dcim.site").
    """
    return f'{ct.app_label}.{ct.model}'


def clean_html(html, schemes):
    """
    Sanitizes HTML based on a whitelist of allowed tags and attributes.
    Also takes a list of allowed URI schemes.
    """
    return nh3.clean(
        html,
        tags=HTML_ALLOWED_TAGS,
        attributes=HTML_ALLOWED_ATTRIBUTES,
        url_schemes=set(schemes)
    )


def local_now():
    """
    Return the current date & time in the system timezone.
    """
    return localtime(timezone.now())


def get_related_models(model, ordered=True):
    """
    Return a list of all models which have a ForeignKey to the given model and the name of the field. For example,
    `get_related_models(Tenant)` will return all models which have a ForeignKey relationship to Tenant.
    """
    related_models = [
        (field.related_model, field.remote_field.name)
        for field in model._meta.related_objects
        if type(field) is ManyToOneRel
    ]

    if ordered:
        return sorted(related_models, key=lambda x: x[0]._meta.verbose_name.lower())

    return related_models
