from abc import ABC, abstractmethod

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from netbox.config import get_config


#
# Attributes
#

class Attr(ABC):
    template_name = None
    placeholder = mark_safe('<span class="text-muted">&mdash;</span>')

    def __init__(self, accessor, label=None, template_name=None):
        self.accessor = accessor
        self.label = label
        self.template_name = template_name or self.template_name

    @abstractmethod
    def render(self, obj, context=None):
        pass

    @staticmethod
    def _resolve_attr(obj, path):
        cur = obj
        for part in path.split('.'):
            if cur is None:
                return None
            cur = getattr(cur, part) if hasattr(cur, part) else cur.get(part) if isinstance(cur, dict) else None
        return cur


class TextAttr(Attr):
    template_name = 'components/attrs/text.html'

    def __init__(self, *args, style=None, copy_button=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = style
        self.copy_button = copy_button

    def render(self, obj, context=None):
        context = context or {}
        value = self._resolve_attr(obj, self.accessor)
        if value in (None, ''):
            return self.placeholder
        return render_to_string(self.template_name, {
            **context,
            'value': value,
            'style': self.style,
            'copy_button': self.copy_button,
        })


class ChoiceAttr(Attr):
    template_name = 'components/attrs/choice.html'

    def render(self, obj, context=None):
        context = context or {}
        try:
            value = getattr(obj, f'get_{self.accessor}_display')()
        except AttributeError:
            value = self._resolve_attr(obj, self.accessor)
        if value in (None, ''):
            return self.placeholder
        try:
            bg_color = getattr(obj, f'get_{self.accessor}_color')()
        except AttributeError:
            bg_color = None
        return render_to_string(self.template_name, {
            **context,
            'value': value,
            'bg_color': bg_color,
        })


class ObjectAttr(Attr):
    template_name = 'components/attrs/object.html'

    def __init__(self, *args, linkify=None, grouped_by=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.linkify = linkify
        self.grouped_by = grouped_by

    def render(self, obj, context=None):
        context = context or {}
        value = self._resolve_attr(obj, self.accessor)
        if value is None:
            return self.placeholder
        group = getattr(value, self.grouped_by, None) if self.grouped_by else None

        return render_to_string(self.template_name, {
            **context,
            'object': value,
            'group': group,
            'linkify': self.linkify,
        })


class NestedObjectAttr(Attr):
    template_name = 'components/attrs/nested_object.html'

    def __init__(self, *args, linkify=None, max_depth=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.linkify = linkify
        self.max_depth = max_depth

    def render(self, obj, context=None):
        context = context or {}
        value = self._resolve_attr(obj, self.accessor)
        if value is None:
            return self.placeholder
        nodes = value.get_ancestors(include_self=True)
        if self.max_depth:
            nodes = list(nodes)[-self.max_depth:]
        return render_to_string(self.template_name, {
            **context,
            'nodes': nodes,
            'linkify': self.linkify,
        })


class AddressAttr(Attr):
    template_name = 'components/attrs/address.html'

    def __init__(self, *args, map_url=True, **kwargs):
        super().__init__(*args, **kwargs)
        if map_url is True:
            self.map_url = get_config().MAPS_URL
        elif map_url:
            self.map_url = map_url
        else:
            self.map_url = None

    def render(self, obj, context=None):
        context = context or {}
        value = self._resolve_attr(obj, self.accessor)
        if value in (None, ''):
            return self.placeholder
        return render_to_string(self.template_name, {
            **context,
            'value': value,
            'map_url': self.map_url,
        })


class GPSCoordinatesAttr(Attr):
    template_name = 'components/attrs/gps_coordinates.html'

    def __init__(self, latitude_attr='latitude', longitude_attr='longitude', map_url=True, **kwargs):
        kwargs.setdefault('label', _('GPS Coordinates'))
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
        latitude = self._resolve_attr(obj, self.latitude_attr)
        longitude = self._resolve_attr(obj, self.longitude_attr)
        if latitude is None or longitude is None:
            return self.placeholder
        return render_to_string(self.template_name, {
            **context,
            'latitude': latitude,
            'longitude': longitude,
            'map_url': self.map_url,
        })


class TimezoneAttr(Attr):
    template_name = 'components/attrs/timezone.html'

    def render(self, obj, context=None):
        context = context or {}
        value = self._resolve_attr(obj, self.accessor)
        if value in (None, ''):
            return self.placeholder
        return render_to_string(self.template_name, {
            **context,
            'value': value,
        })


class TemplatedAttr(Attr):

    def __init__(self, *args, context=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = context or {}

    def render(self, obj, context=None):
        context = context or {}
        value = self._resolve_attr(obj, self.accessor)
        if value is None:
            return self.placeholder
        return render_to_string(
            self.template_name,
            {
                **context,
                **self.context,
                'object': obj,
                'value': value,
            }
        )


class UtilizationAttr(Attr):
    template_name = 'components/attrs/utilization.html'

    def render(self, obj, context=None):
        context = context or {}
        value = self._resolve_attr(obj, self.accessor)
        return render_to_string(self.template_name, {
            **context,
            'value': value,
        })
