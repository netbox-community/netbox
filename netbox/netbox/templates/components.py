from abc import ABC, ABCMeta, abstractmethod
from functools import cached_property

from django.template.loader import render_to_string
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from netbox.config import get_config
from utilities.string import title


#
# Attributes
#

class Attr:
    template_name = None
    placeholder = mark_safe('<span class="text-muted">&mdash;</span>')

    def __init__(self, accessor, label=None, template_name=None):
        self.accessor = accessor
        self.label = label
        self.template_name = template_name or self.template_name

    @staticmethod
    def _resolve_attr(obj, path):
        cur = obj
        for part in path.split('.'):
            if cur is None:
                return None
            cur = getattr(cur, part) if hasattr(cur, part) else cur.get(part) if isinstance(cur, dict) else None
        return cur


class TextAttr(Attr):

    def __init__(self, *args, style=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = style

    def render(self, obj):
        value = self._resolve_attr(obj, self.accessor)
        if value in (None, ''):
            return self.placeholder
        if self.style:
            return mark_safe(f'<span class="{self.style}">{escape(value)}</span>')
        return value


class ObjectAttr(Attr):
    template_name = 'components/object.html'

    def __init__(self, *args, linkify=None, grouped_by=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.linkify = linkify
        self.grouped_by = grouped_by

        # Derive label from related object if not explicitly set
        if self.label is None:
            self.label = title(self.accessor)

    def render(self, obj):
        value = self._resolve_attr(obj, self.accessor)
        if value is None:
            return self.placeholder
        group = getattr(value, self.grouped_by, None) if self.grouped_by else None

        return render_to_string(self.template_name, {
            'object': value,
            'group': group,
            'linkify': self.linkify,
        })


class NestedObjectAttr(Attr):
    template_name = 'components/nested_object.html'

    def __init__(self, *args, linkify=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.linkify = linkify

    def render(self, obj):
        value = self._resolve_attr(obj, self.accessor)
        if value is None:
            return self.placeholder
        return render_to_string(self.template_name, {
            'nodes': value.get_ancestors(include_self=True),
            'linkify': self.linkify,
        })


class GPSCoordinatesAttr(Attr):
    template_name = 'components/gps_coordinates.html'

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

    def render(self, obj):
        latitude = self._resolve_attr(obj, self.latitude_attr)
        longitude = self._resolve_attr(obj, self.longitude_attr)
        if latitude is None or longitude is None:
            return self.placeholder
        return render_to_string(self.template_name, {
            'latitude': latitude,
            'longitude': longitude,
            'map_url': self.map_url,
        })


class TemplatedAttr(Attr):

    def __init__(self, *args, context=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = context or {}

    def render(self, obj):
        return render_to_string(
            self.template_name,
            {
                **self.context,
                'object': obj,
                'value': self._resolve_attr(obj, self.accessor),
            }
        )


#
# Components
#

class Component(ABC):

    @abstractmethod
    def render(self):
        pass

    def __str__(self):
        return self.render()


class ObjectDetailsPanelMeta(ABCMeta):

    def __new__(mcls, name, bases, attrs):
        # Collect all declared attributes
        attrs['_attrs'] = {}
        for key, val in list(attrs.items()):
            if isinstance(val, Attr):
                attrs['_attrs'][key] = val
        return super().__new__(mcls, name, bases, attrs)


class ObjectDetailsPanel(Component, metaclass=ObjectDetailsPanelMeta):
    template_name = 'components/object_details_panel.html'

    def __init__(self, obj, title=None):
        self.object = obj
        self.title = title or obj._meta.verbose_name

    @cached_property
    def attributes(self):
        return [
            {
                'label': attr.label or title(name),
                'value': attr.render(self.object),
            } for name, attr in self._attrs.items()
        ]

    def render(self):
        return render_to_string(self.template_name, {
            'title': self.title,
            'attrs': self.attributes,
        })

    def __str__(self):
        return self.render()
