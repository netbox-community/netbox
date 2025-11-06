from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from netbox.config import get_config
from utilities.data import resolve_attr_path

__all__ = (
    'AddressAttr',
    'BooleanAttr',
    'ColorAttr',
    'ChoiceAttr',
    'GPSCoordinatesAttr',
    'ImageAttr',
    'NestedObjectAttr',
    'NumericAttr',
    'ObjectAttribute',
    'RelatedObjectAttr',
    'TemplatedAttr',
    'TextAttr',
    'TimezoneAttr',
    'UtilizationAttr',
)

PLACEHOLDER_HTML = '<span class="text-muted">&mdash;</span>'


#
# Attributes
#

class ObjectAttribute:
    """
    Base class for representing an attribute of an object.

    Attributes:
        template_name: The name of the template to render
        label: Human-friendly label for the rendered attribute
        placeholder: HTML to render for empty/null values
    """
    template_name = None
    label = None
    placeholder = mark_safe(PLACEHOLDER_HTML)

    def __init__(self, accessor, label=None):
        """
        Instantiate a new ObjectAttribute.

        Parameters:
             accessor: The dotted path to the attribute being rendered (e.g. "site.region.name")
             label: Human-friendly label for the rendered attribute
        """
        self.accessor = accessor
        if label is not None:
            self.label = label

    def get_value(self, obj):
        """
        Return the value of the attribute.

        Parameters:
            obj: The object for which the attribute is being rendered
        """
        return resolve_attr_path(obj, self.accessor)

    def get_context(self, obj, context):
        """
        Return any additional template context used to render the attribute value.

        Parameters:
            obj: The object for which the attribute is being rendered
            context: The root template context
        """
        return {}

    def render(self, obj, context):
        value = self.get_value(obj)

        # If the value is empty, render a placeholder
        if value in (None, ''):
            return self.placeholder

        return render_to_string(self.template_name, {
            **self.get_context(obj, context),
            'name': context['name'],
            'value': value,
        })


class TextAttr(ObjectAttribute):
    """
    A text attribute.
    """
    template_name = 'ui/attrs/text.html'

    def __init__(self, *args, style=None, format_string=None, copy_button=False, **kwargs):
        """
        Instantiate a new TextAttr.

        Parameters:
             accessor: The dotted path to the attribute being rendered (e.g. "site.region.name")
             label: Human-friendly label for the rendered attribute
             template_name: The name of the template to render
             style: CSS class to apply to the rendered attribute
             format_string: If specified, the value will be formatted using this string when rendering
             copy_button: Set to True to include a copy-to-clipboard button
        """
        super().__init__(*args, **kwargs)
        self.style = style
        self.format_string = format_string
        self.copy_button = copy_button

    def get_value(self, obj):
        value = resolve_attr_path(obj, self.accessor)
        # Apply format string (if any)
        if value and self.format_string:
            return self.format_string.format(value)
        return value

    def get_context(self, obj, context):
        return {
            'style': self.style,
            'copy_button': self.copy_button,
        }


class NumericAttr(ObjectAttribute):
    """
    An integer or float attribute.
    """
    template_name = 'ui/attrs/numeric.html'

    def __init__(self, *args, unit_accessor=None, copy_button=False, **kwargs):
        """
        Instantiate a new NumericAttr.

        Parameters:
             accessor: The dotted path to the attribute being rendered (e.g. "site.region.name")
             unit_accessor: Accessor for the unit of measurement to display alongside the value (if any)
             copy_button: Set to True to include a copy-to-clipboard button
             label: Human-friendly label for the rendered attribute
             template_name: The name of the template to render
        """
        super().__init__(*args, **kwargs)
        self.unit_accessor = unit_accessor
        self.copy_button = copy_button

    def get_context(self, obj, context):
        unit = resolve_attr_path(obj, self.unit_accessor) if self.unit_accessor else None
        return {
            'unit': unit,
            'copy_button': self.copy_button,
        }


class ChoiceAttr(ObjectAttribute):
    """
    A selection from a set of choices.

    The class calls get_FOO_display() on the object to retrieve the human-friendly choice label. If a get_FOO_color()
    method exists on the object, it will be used to render a background color for the attribute value.
    """
    template_name = 'ui/attrs/choice.html'

    def get_value(self, obj):
        try:
            return getattr(obj, f'get_{self.accessor}_display')()
        except AttributeError:
            return resolve_attr_path(obj, self.accessor)

    def get_context(self, obj, context):
        try:
            bg_color = getattr(obj, f'get_{self.accessor}_color')()
        except AttributeError:
            bg_color = None
        return {
            'bg_color': bg_color,
        }


class BooleanAttr(ObjectAttribute):
    """
    A boolean attribute.
    """
    template_name = 'ui/attrs/boolean.html'

    def __init__(self, *args, display_false=True, **kwargs):
        """
        Instantiate a new BooleanAttr.

        Parameters:
             accessor: The dotted path to the attribute being rendered (e.g. "site.region.name")
             display_false: If False, a placeholder will be rendered instead of the "False" indication
             label: Human-friendly label for the rendered attribute
             template_name: The name of the template to render
        """
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
    """
    template_name = 'ui/attrs/image.html'


class RelatedObjectAttr(ObjectAttribute):
    """
    An attribute representing a related object.
    """
    template_name = 'ui/attrs/object.html'

    def __init__(self, *args, linkify=None, grouped_by=None, **kwargs):
        """
        Instantiate a new RelatedObjectAttr.

        Parameters:
             accessor: The dotted path to the attribute being rendered (e.g. "site.region.name")
             linkify: If True, the rendered value will be hyperlinked to the related object's detail view
             grouped_by: A second-order object to annotate alongside the related object; for example, an attribute
                representing the dcim.Site model might specify grouped_by="region"
             label: Human-friendly label for the rendered attribute
             template_name: The name of the template to render
        """
        super().__init__(*args, **kwargs)
        self.linkify = linkify
        self.grouped_by = grouped_by

    def get_context(self, obj, context):
        value = self.get_value(obj)
        group = getattr(value, self.grouped_by, None) if self.grouped_by else None
        return {
            'linkify': self.linkify,
            'group': group,
        }


class NestedObjectAttr(ObjectAttribute):
    """
    An attribute representing a related nested object. Similar to `RelatedObjectAttr`, but includes the ancestors of the
    related object in the rendered output.
    """
    template_name = 'ui/attrs/nested_object.html'

    def __init__(self, *args, linkify=None, max_depth=None, **kwargs):
        """
        Instantiate a new NestedObjectAttr. Shows a related object as well as its ancestors.

        Parameters:
             accessor: The dotted path to the attribute being rendered (e.g. "site.region.name")
             linkify: If True, the rendered value will be hyperlinked to the related object's detail view
             max_depth: Maximum number of ancestors to display (default: all)
             label: Human-friendly label for the rendered attribute
             template_name: The name of the template to render
        """
        super().__init__(*args, **kwargs)
        self.linkify = linkify
        self.max_depth = max_depth

    def get_context(self, obj, context):
        value = self.get_value(obj)
        nodes = value.get_ancestors(include_self=True)
        if self.max_depth:
            nodes = list(nodes)[-self.max_depth:]
        return {
            'nodes': nodes,
            'linkify': self.linkify,
        }


class AddressAttr(ObjectAttribute):
    """
    A physical or mailing address.
    """
    template_name = 'ui/attrs/address.html'

    def __init__(self, *args, map_url=True, **kwargs):
        """
        Instantiate a new AddressAttr.

        Parameters:
             accessor: The dotted path to the attribute being rendered (e.g. "site.region.name")
             map_url: If true, the address will render as a hyperlink using settings.MAPS_URL
             label: Human-friendly label for the rendered attribute
             template_name: The name of the template to render
        """
        super().__init__(*args, **kwargs)
        if map_url is True:
            self.map_url = get_config().MAPS_URL
        elif map_url:
            self.map_url = map_url
        else:
            self.map_url = None

    def get_context(self, obj, context):
        return {
            'map_url': self.map_url,
        }


class GPSCoordinatesAttr(ObjectAttribute):
    """
    A GPS coordinates pair comprising latitude and longitude values.
    """
    template_name = 'ui/attrs/gps_coordinates.html'
    label = _('GPS coordinates')

    def __init__(self, latitude_attr='latitude', longitude_attr='longitude', map_url=True, **kwargs):
        """
        Instantiate a new GPSCoordinatesAttr.

        Parameters:
             latitude_attr: The name of the field containing the latitude value
             longitude_attr: The name of the field containing the longitude value
             map_url: If true, the address will render as a hyperlink using settings.MAPS_URL
             label: Human-friendly label for the rendered attribute
             template_name: The name of the template to render
        """
        super().__init__(accessor=None, **kwargs)
        self.latitude_attr = latitude_attr
        self.longitude_attr = longitude_attr
        if map_url is True:
            self.map_url = get_config().MAPS_URL
        elif map_url:
            self.map_url = map_url
        else:
            self.map_url = None

    def render(self, obj, context=None):
        context = context or {}
        latitude = resolve_attr_path(obj, self.latitude_attr)
        longitude = resolve_attr_path(obj, self.longitude_attr)
        if latitude is None or longitude is None:
            return self.placeholder
        return render_to_string(self.template_name, {
            **context,
            'latitude': latitude,
            'longitude': longitude,
            'map_url': self.map_url,
        })


class TimezoneAttr(ObjectAttribute):
    """
    A timezone value. Includes the numeric offset from UTC.
    """
    template_name = 'ui/attrs/timezone.html'


class TemplatedAttr(ObjectAttribute):
    """
    Renders an attribute using a custom template.
    """
    def __init__(self, *args, template_name, context=None, **kwargs):
        """
        Instantiate a new TemplatedAttr.

        Parameters:
             accessor: The dotted path to the attribute being rendered (e.g. "site.region.name")
             template_name: The name of the template to render
             context: Additional context to pass to the template when rendering
             label: Human-friendly label for the rendered attribute
             template_name: The name of the template to render
        """
        super().__init__(*args, **kwargs)
        self.template_name = template_name
        self.context = context or {}

    def get_context(self, obj, context):
        return {
            **self.context,
            'object': obj,
        }


class UtilizationAttr(ObjectAttribute):
    """
    Renders the value of an attribute as a utilization graph.
    """
    template_name = 'ui/attrs/utilization.html'
