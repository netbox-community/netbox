from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from netbox.config import get_config
from netbox.ui.utils import build_coords_url, is_coordinate_map_url
from utilities.data import resolve_attr_path

__all__ = (
    'AddressAttr',
    'BooleanAttr',
    'ChoiceAttr',
    'ColorAttr',
    'DateTimeAttr',
    'DistanceAttr',
    'GPSCoordinatesAttr',
    'GenericForeignKeyAttr',
    'ImageAttr',
    'NestedObjectAttr',
    'NumericAttr',
    'ObjectAttribute',
    'RelatedObjectAttr',
    'RelatedObjectListAttr',
    'TemplatedAttr',
    'TextAttr',
    'TimezoneAttr',
    'UtilizationAttr',
    'WeightAttr',
)

PLACEHOLDER_HTML = '<span class="text-muted">&mdash;</span>'

IMAGE_DECODING_CHOICES = ('auto', 'async', 'sync')


#
# Mixins
#

class MapURLMixin:
    _map_url = None

    @property
    def map_url(self):
        if self._map_url is True:
            return get_config().MAPS_URL
        if self._map_url:
            return self._map_url
        return None


#
# Attributes
#

class ObjectAttribute:
    """
    Base class for representing an attribute of an object.

    Attributes:
        template_name (str): The name of the template to render
        placeholder (str): HTML to render for empty/null values

    Parameters:
        accessor (str): The dotted path to the attribute being rendered (e.g. "site.region.name")
        label (str): Human-friendly label for the rendered attribute
    """
    template_name = None
    label = None
    placeholder = mark_safe(PLACEHOLDER_HTML)

    def __init__(self, accessor, label=None):
        self.accessor = accessor
        if label is not None:
            self.label = label

    def get_value(self, obj):
        """
        Return the value of the attribute.

        Parameters:
            obj (object): The object for which the attribute is being rendered
        """
        return resolve_attr_path(obj, self.accessor)

    def get_context(self, obj, attr, value, context):
        """
        Return any additional template context used to render the attribute value.

        Parameters:
            obj (object): The object for which the attribute is being rendered
            attr (str): The name of the attribute being rendered
            value: The value of the attribute on the object
            context (dict): The panel template context
        """
        return {}

    def render(self, obj, context):
        name = context['name']
        value = self.get_value(obj)

        # If the value is empty, render a placeholder
        if value in (None, ''):
            return self.placeholder

        return render_to_string(self.template_name, {
            **self.get_context(obj, name, value, context),
            'name': name,
            'value': value,
        })


class TextAttr(ObjectAttribute):
    """
    A text attribute.

    Parameters:
         style (str): CSS class to apply to the rendered attribute
         format_string (str): If specified, the value will be formatted using this string when rendering
         copy_button (bool): Set to True to include a copy-to-clipboard button
    """
    template_name = 'ui/attrs/text.html'

    def __init__(self, *args, style=None, format_string=None, copy_button=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = style
        self.format_string = format_string
        self.copy_button = copy_button

    def get_value(self, obj):
        value = resolve_attr_path(obj, self.accessor)
        # Apply format string (if any)
        if value is not None and value != '' and self.format_string:
            return self.format_string.format(value)
        return value

    def get_context(self, obj, attr, value, context):
        return {
            'style': self.style,
            'copy_button': self.copy_button,
        }


class NumericAttr(ObjectAttribute):
    """
    An integer or float attribute.

    Parameters:
         unit_accessor (str): Accessor for the unit of measurement to display alongside the value (if any)
         copy_button (bool): Set to True to include a copy-to-clipboard button
    """
    template_name = 'ui/attrs/numeric.html'

    def __init__(self, *args, unit_accessor=None, copy_button=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.unit_accessor = unit_accessor
        self.copy_button = copy_button

    def get_context(self, obj, attr, value, context):
        unit = resolve_attr_path(obj, self.unit_accessor) if self.unit_accessor else None
        return {
            'unit': unit,
            'copy_button': self.copy_button,
        }


class ChoiceAttr(ObjectAttribute):
    """
    A selection from a set of choices.

    The class calls get_FOO_display() on the terminal object resolved by the accessor
    to retrieve the human-friendly choice label. For example, accessor="interface.type"
    will call interface.get_type_display().
    If a get_FOO_color() method exists on that object, it will be used to render a
    background color for the attribute value.
    """
    template_name = 'ui/attrs/choice.html'

    def _resolve_target(self, obj):
        if not self.accessor or '.' not in self.accessor:
            return obj, self.accessor

        object_accessor, field_name = self.accessor.rsplit('.', 1)
        return resolve_attr_path(obj, object_accessor), field_name

    def get_value(self, obj):
        target, field_name = self._resolve_target(obj)
        if target is None:
            return None

        display = getattr(target, f'get_{field_name}_display', None)
        if callable(display):
            return display()

        return resolve_attr_path(target, field_name)

    def get_context(self, obj, attr, value, context):
        target, field_name = self._resolve_target(obj)
        if target is None:
            return {'bg_color': None}

        get_color = getattr(target, f'get_{field_name}_color', None)
        bg_color = get_color() if callable(get_color) else None

        return {
            'bg_color': bg_color,
        }


class BooleanAttr(ObjectAttribute):
    """
    A boolean attribute.

    Parameters:
         display_false (bool): If False, a placeholder will be rendered instead of the "False" indication
    """
    template_name = 'ui/attrs/boolean.html'

    def __init__(self, *args, display_false=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.display_false = display_false

    def get_value(self, obj):
        value = super().get_value(obj)
        if value is False and self.display_false is False:
            return None
        return value


class ColorAttr(ObjectAttribute):
    """
    An RGB color value.
    """
    template_name = 'ui/attrs/color.html'
    label = _('Color')


class ImageAttr(ObjectAttribute):
    """
    An attribute representing an image field on the model. Displays the uploaded image.

    Parameters:
        load_lazy (bool): If True, the image will be loaded lazily (default: True)
        decoding (str): Image decoding option ('async', 'sync', 'auto', None)
    """
    template_name = 'ui/attrs/image.html'

    def __init__(self, *args, load_lazy=True, decoding=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_lazy = load_lazy

        if decoding is not None and decoding not in IMAGE_DECODING_CHOICES:
            raise ValueError(
                _('Invalid decoding option: {decoding}! Must be one of {image_decoding_choices}').format(
                    decoding=decoding, image_decoding_choices=', '.join(IMAGE_DECODING_CHOICES)
                )
            )

        # Compute default decoding:
        # - lazy images: async decoding (performance-friendly hint)
        # - non-lazy images: omit decoding (browser default/auto)
        if decoding is None and load_lazy:
            decoding = 'async'
        self.decoding = decoding

    def get_context(self, obj, attr, value, context):
        return {
            'decoding': self.decoding,
            'load_lazy': self.load_lazy,
        }


class RelatedObjectAttr(ObjectAttribute):
    """
    An attribute representing a related object.

    Parameters:
         linkify (bool): If True, the rendered value will be hyperlinked to the related object's detail view
         grouped_by (str): A second-order object to annotate alongside the related object; for example, an attribute
              representing the dcim.Site model might specify grouped_by="region"
         colored (bool): If True, render the object as a colored badge when it exposes a `color` attribute
    """
    template_name = 'ui/attrs/object.html'

    def __init__(self, *args, linkify=None, grouped_by=None, colored=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.linkify = linkify
        self.grouped_by = grouped_by
        self.colored = colored

    def get_context(self, obj, attr, value, context):
        group = getattr(value, self.grouped_by, None) if self.grouped_by else None
        return {
            'linkify': self.linkify,
            'group': group,
            'colored': self.colored,
        }


class RelatedObjectListAttr(RelatedObjectAttr):
    """
    An attribute representing a list of related objects.

    The accessor may resolve to a related manager or queryset.

    Parameters:
        max_items (int): Maximum number of items to display
        overflow_indicator (str | None): Marker rendered as a final list item when
            additional objects exist beyond `max_items`; set to None to suppress it
    """

    template_name = 'ui/attrs/object_list.html'

    def __init__(self, *args, max_items=None, overflow_indicator='…', **kwargs):
        super().__init__(*args, **kwargs)

        if max_items is not None and (type(max_items) is not int or max_items < 1):
            raise ValueError(
                _('Invalid max_items value: {max_items}! Must be a positive integer or None.').format(
                    max_items=max_items
                )
            )

        self.max_items = max_items
        self.overflow_indicator = overflow_indicator

    def _get_items(self, items):
        """
        Retrieve items from the given object using the accessor path.

        Returns a tuple of (items, has_more) where items is a list of resolved objects
        and has_more indicates whether additional items exist beyond the max_items limit.
        """
        if items is None:
            return [], False

        if hasattr(items, 'all'):
            items = items.all()

        if self.max_items is None:
            return list(items), False

        items = list(items[:self.max_items + 1])
        has_more = len(items) > self.max_items

        return items[:self.max_items], has_more

    def get_context(self, obj, attr, value, context):
        items, has_more = self._get_items(value)

        return {
            'linkify': self.linkify,
            'colored': self.colored,
            'items': [
                {
                    'value': item,
                    'group': getattr(item, self.grouped_by, None) if self.grouped_by else None,
                }
                for item in items
            ],
            'overflow_indicator': self.overflow_indicator if has_more else None,
        }

    def render(self, obj, context):
        name = context['name']
        value = self.get_value(obj)
        context_data = self.get_context(obj, name, value, context)

        if not context_data['items']:
            return self.placeholder

        return render_to_string(self.template_name, {
            'name': name,
            **context_data,
        })


class NestedObjectAttr(ObjectAttribute):
    """
    An attribute representing a related nested object. Similar to `RelatedObjectAttr`, but includes the ancestors of the
    related object in the rendered output.

    Parameters:
         linkify (bool): If True, the rendered value will be hyperlinked to the related object's detail view
         max_depth (int): Maximum number of ancestors to display (default: all)
         colored (bool): If True, render the object as a colored badge when it exposes a `color` attribute
    """
    template_name = 'ui/attrs/nested_object.html'

    def __init__(self, *args, linkify=None, max_depth=None, colored=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.linkify = linkify
        self.max_depth = max_depth
        self.colored = colored

    def get_context(self, obj, attr, value, context):
        nodes = []
        if value is not None:
            nodes = value.get_ancestors(include_self=True)
            if self.max_depth:
                nodes = list(nodes)[-self.max_depth:]
        return {
            'nodes': nodes,
            'linkify': self.linkify,
            'colored': self.colored,
        }


class GenericForeignKeyAttr(ObjectAttribute):
    """
    An attribute representing a related generic relation object.

    This attribute is similar to `RelatedObjectAttr` but uses the
    ContentType of the related object to be displayed alongside the value.

    Parameters:
         linkify (bool): If True, the rendered value will be hyperlinked
              to the related object's detail view.
         nested (bool): If True and the related object exposes a callable
              `get_ancestors(include_self=True)`, render the object together
              with its ancestors as a breadcrumb, similar to `NestedObjectAttr`.
              Non-hierarchical objects continue to render normally.
         max_depth (int): Maximum number of ancestors to display when
              `nested` is enabled. Ignored otherwise.
    """
    template_name = 'ui/attrs/generic_object.html'

    def __init__(self, *args, linkify=None, nested=False, max_depth=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.linkify = linkify
        self.nested = nested
        self.max_depth = max_depth

    def _get_nodes(self, value):
        """
        Retrieves a list of nodes representing the hierarchical path to a given value.
        """
        if value is None:
            return None

        get_ancestors = getattr(value, 'get_ancestors', None)
        if not callable(get_ancestors):
            return None

        nodes = list(get_ancestors(include_self=True))

        if self.max_depth is not None:
            nodes = nodes[-self.max_depth:]

        return nodes

    def get_context(self, obj, attr, value, context):
        content_type = value._meta.verbose_name if value is not None else None
        nodes = self._get_nodes(value) if (self.nested and value is not None) else None

        return {
            'content_type': content_type,
            'linkify': self.linkify,
            'nodes': nodes,
        }


class AddressAttr(MapURLMixin, ObjectAttribute):
    """
    A physical or mailing address.

    Parameters:
         map_url (bool/str): The URL to use when rendering the address. If True, the address will render as a
              hyperlink using settings.MAPS_URL.
    """
    template_name = 'ui/attrs/address.html'

    def __init__(self, *args, map_url=True, **kwargs):
        super().__init__(*args, **kwargs)
        self._map_url = map_url

    def get_context(self, obj, attr, value, context):
        map_url = self.map_url
        # A coordinate-format MAPS_URL (containing {lat}/{lon}) cannot be used for address rendering
        if map_url and is_coordinate_map_url(map_url):
            map_url = None
        return {
            'map_url': map_url,
        }


class GPSCoordinatesAttr(MapURLMixin, ObjectAttribute):
    """
    A GPS coordinates pair comprising latitude and longitude values.

    Parameters:
         latitude_attr (float): The name of the field containing the latitude value
         longitude_attr (float): The name of the field containing the longitude value
         map_url (bool): If true, the address will render as a hyperlink using settings.MAPS_URL
    """
    template_name = 'ui/attrs/gps_coordinates.html'
    label = _('GPS coordinates')

    def __init__(self, latitude_attr='latitude', longitude_attr='longitude', map_url=True, **kwargs):
        super().__init__(accessor=latitude_attr, **kwargs)
        self.latitude_attr = latitude_attr
        self.longitude_attr = longitude_attr
        self._map_url = map_url

    def render(self, obj, context):
        latitude = resolve_attr_path(obj, self.latitude_attr)
        longitude = resolve_attr_path(obj, self.longitude_attr)
        if latitude is None or longitude is None:
            return self.placeholder
        map_url = self.map_url
        if map_url:
            map_url = build_coords_url(map_url, latitude, longitude)
        return render_to_string(self.template_name, {
            'name': context['name'],
            'latitude': latitude,
            'longitude': longitude,
            'map_url': map_url,
        })


class DateTimeAttr(ObjectAttribute):
    """
    A date or datetime attribute.

    Parameters:
        spec (str): Controls the rendering format. Use 'date' for date-only rendering,
                    or 'seconds'/'minutes' for datetime rendering with the given precision.
    """
    template_name = 'ui/attrs/datetime.html'

    def __init__(self, *args, spec='seconds', **kwargs):
        super().__init__(*args, **kwargs)
        self.spec = spec

    def get_context(self, obj, attr, value, context):
        return {
            'spec': self.spec,
        }


class TimezoneAttr(ObjectAttribute):
    """
    A timezone value. Includes the numeric offset from UTC.
    """
    template_name = 'ui/attrs/timezone.html'


class TemplatedAttr(ObjectAttribute):
    """
    Renders an attribute using a custom template.

    Parameters:
         template_name (str): The name of the template to render
         context (dict): Additional context to pass to the template when rendering
    """
    def __init__(self, *args, template_name, context=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_name = template_name
        self.context = context or {}

    def get_context(self, obj, attr, value, context):
        return {
            **context,
            **self.context,
            'object': obj,
        }


class UtilizationAttr(ObjectAttribute):
    """
    Renders the value of an attribute as a utilization graph.
    """
    template_name = 'ui/attrs/utilization.html'


IMPERIAL_WEIGHT = {'lb', 'oz'}
METRIC_WEIGHT = {'kg', 'g'}
IMPERIAL_DISTANCE = {'mi', 'ft'}
METRIC_DISTANCE = {'km', 'm'}


def compute_weight_display(weight, weight_unit, abs_weight, system):
    """
    Return (display_value, display_unit) for a weight, respecting the user's measurement system.
    abs_weight is in grams (from WeightMixin._abs_weight).
    oz and g pass through unchanged since there is no cross-system equivalent.
    """
    if system == 'metric' and weight_unit in IMPERIAL_WEIGHT and abs_weight is not None:
        return round(abs_weight / 1000, 2), 'kg'
    if system == 'imperial' and weight_unit in METRIC_WEIGHT and abs_weight is not None:
        lbs = round(abs_weight / 453.592, 2)
        return lbs, 'lb' if lbs == 1 else 'lbs'
    if weight_unit == 'lb':
        return weight, 'lb' if weight == 1 else 'lbs'
    return weight, weight_unit


def compute_distance_display(distance, distance_unit, abs_distance, system):
    """
    Return (display_value, display_unit) for a distance, respecting the user's measurement system.
    abs_distance is in metres (from DistanceMixin._abs_distance).
    Distances < 1 km are shown in metres; < 1 mi are shown in feet.
    """
    if system == 'metric' and distance_unit in IMPERIAL_DISTANCE and abs_distance is not None:
        abs_m = float(abs_distance)
        if abs_m >= 1000:
            return round(abs_m / 1000, 2), 'km'
        return round(abs_m, 2), 'm'
    if system == 'imperial' and distance_unit in METRIC_DISTANCE and abs_distance is not None:
        abs_m = float(abs_distance)
        if abs_m >= 1609.344:
            return round(abs_m / 1609.344, 2), 'mi'
        return round(abs_m / 0.3048, 2), 'ft'
    return distance, distance_unit


class WeightAttr(ObjectAttribute):
    """
    A weight attribute that converts to the user's preferred measurement system.

    Parameters:
        unit_attr (str): Name of the field holding the weight unit (default: 'weight_unit')
        abs_attr (str): The internal _abs_weight field name on WeightMixin (stored in grams).
            Accessed via Python — not subject to Django's template underscore restriction.
    """
    template_name = 'ui/attrs/numeric.html'

    def __init__(self, *args, unit_attr='weight_unit', abs_attr='_abs_weight', **kwargs):
        super().__init__(*args, **kwargs)
        self.unit_attr = unit_attr
        self.abs_attr = abs_attr

    def render(self, obj, context):
        weight = resolve_attr_path(obj, self.accessor)
        if weight is None:
            return self.placeholder

        system = (context.get('preferences') or {}).get('ui.measurement_system') or ''
        unit = resolve_attr_path(obj, self.unit_attr)
        abs_weight = resolve_attr_path(obj, self.abs_attr)
        display_value, display_unit = compute_weight_display(weight, unit, abs_weight, system)

        return render_to_string(self.template_name, {
            'name': context['name'],
            'value': display_value,
            'unit': display_unit,
        })


class DistanceAttr(ObjectAttribute):
    """
    A distance attribute that converts to the user's preferred measurement system.

    Parameters:
        unit_attr (str): Name of the field holding the distance unit (default: 'distance_unit')
        abs_attr (str): The internal _abs_distance field name on DistanceMixin (stored in metres).
            Accessed via Python — not subject to Django's template underscore restriction.
    """
    template_name = 'ui/attrs/numeric.html'

    def __init__(self, *args, unit_attr='distance_unit', abs_attr='_abs_distance', **kwargs):
        super().__init__(*args, **kwargs)
        self.unit_attr = unit_attr
        self.abs_attr = abs_attr

    def render(self, obj, context):
        distance = resolve_attr_path(obj, self.accessor)
        if distance is None:
            return self.placeholder

        system = (context.get('preferences') or {}).get('ui.measurement_system') or ''
        unit = resolve_attr_path(obj, self.unit_attr)
        abs_distance = resolve_attr_path(obj, self.abs_attr)
        display_value, display_unit = compute_distance_display(distance, unit, abs_distance, system)

        return render_to_string(self.template_name, {
            'name': context['name'],
            'value': display_value,
            'unit': display_unit,
        })
