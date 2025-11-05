from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from netbox.config import get_config
from utilities.data import resolve_attr_path


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
    placeholder = mark_safe('<span class="text-muted">&mdash;</span>')

    def __init__(self, accessor, label=None, template_name=None):
        """
        Instantiate a new ObjectAttribute.

        Parameters:
             accessor: The dotted path to the attribute being rendered (e.g. "site.region.name")
             label: Human-friendly label for the rendered attribute
             template_name: The name of the template to render
        """
        self.accessor = accessor
        if template_name is not None:
            self.template_name = template_name
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
            context: The template context
        """
        return {}

    def render(self, obj, context):
        value = self.get_value(obj)
        if value in (None, ''):
            return self.placeholder
        context = self.get_context(obj, context)
        return render_to_string(self.template_name, {
            **context,
            'value': value,
        })


class TextAttr(ObjectAttribute):
    template_name = 'ui/attrs/text.html'

    def __init__(self, *args, style=None, format_string=None, copy_button=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = style
        self.format_string = format_string
        self.copy_button = copy_button

    def get_value(self, obj):
        value = resolve_attr_path(obj, self.accessor)
        # Apply format string (if any)
        if value and self.format_string:
            value = self.format_string.format(value)
        return value

    def get_context(self, obj, context):
        return {
            'style': self.style,
            'copy_button': self.copy_button,
        }


class NumericAttr(ObjectAttribute):
    template_name = 'ui/attrs/numeric.html'

    def __init__(self, *args, unit_accessor=None, copy_button=False, **kwargs):
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
    template_name = 'ui/attrs/color.html'
    label = _('Color')


class ImageAttr(ObjectAttribute):
    template_name = 'ui/attrs/image.html'


class ObjectAttr(ObjectAttribute):
    template_name = 'ui/attrs/object.html'

    def __init__(self, *args, linkify=None, grouped_by=None, **kwargs):
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
    template_name = 'ui/attrs/nested_object.html'

    def __init__(self, *args, linkify=None, max_depth=None, **kwargs):
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
    template_name = 'ui/attrs/address.html'

    def __init__(self, *args, map_url=True, **kwargs):
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
    template_name = 'ui/attrs/gps_coordinates.html'
    label = _('GPS coordinates')

    def __init__(self, latitude_attr='latitude', longitude_attr='longitude', map_url=True, **kwargs):
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
    template_name = 'ui/attrs/timezone.html'


class TemplatedAttr(ObjectAttribute):

    def __init__(self, *args, context=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = context or {}

    def get_context(self, obj, context):
        return {
            **self.context,
            'object': obj,
        }


class UtilizationAttr(ObjectAttribute):
    template_name = 'ui/attrs/utilization.html'
