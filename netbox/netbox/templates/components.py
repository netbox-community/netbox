from abc import ABC, abstractmethod

from django.template.loader import render_to_string
from django.utils.html import escape
from django.utils.safestring import mark_safe

from netbox.config import get_config


class Component(ABC):

    @abstractmethod
    def render(self):
        pass

    def __str__(self):
        return self.render()


#
# Attributes
#

class Attr(Component):
    template_name = None
    placeholder = mark_safe('<span class="text-muted">&mdash;</span>')


class TextAttr(Attr):

    def __init__(self, value, style=None):
        self.value = value
        self.style = style

    def render(self):
        if self.value in (None, ''):
            return self.placeholder
        if self.style:
            return mark_safe(f'<span class="{self.style}">{escape(self.value)}</span>')
        return self.value


class ObjectAttr(Attr):
    template_name = 'components/object.html'

    def __init__(self, obj, linkify=None, grouped_by=None, template_name=None):
        self.object = obj
        self.linkify = linkify
        self.group = getattr(obj, grouped_by, None) if grouped_by else None
        self.template_name = template_name or self.template_name

    def render(self):
        if self.object is None:
            return self.placeholder

        # Determine object & group URLs
        # TODO: Add support for reverse() lookups
        if self.linkify and hasattr(self.object, 'get_absolute_url'):
            object_url = self.object.get_absolute_url()
        else:
            object_url = None
        if self.linkify and hasattr(self.group, 'get_absolute_url'):
            group_url = self.group.get_absolute_url()
        else:
            group_url = None

        return render_to_string(self.template_name, {
            'object': self.object,
            'object_url': object_url,
            'group': self.group,
            'group_url': group_url,
        })


class NestedObjectAttr(Attr):
    template_name = 'components/nested_object.html'

    def __init__(self, obj, linkify=None):
        self.object = obj
        self.linkify = linkify

    def render(self):
        if not self.object:
            return self.placeholder
        return render_to_string(self.template_name, {
            'nodes': self.object.get_ancestors(include_self=True),
            'linkify': self.linkify,
        })


class GPSCoordinatesAttr(Attr):
    template_name = 'components/gps_coordinates.html'

    def __init__(self, latitude, longitude, map_url=True):
        self.latitude = latitude
        self.longitude = longitude
        if map_url is True:
            self.map_url = get_config().MAPS_URL
        elif map_url:
            self.map_url = map_url
        else:
            self.map_url = None

    def render(self):
        if not (self.latitude and self.longitude):
            return self.placeholder
        return render_to_string(self.template_name, {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'map_url': self.map_url,
        })


#
# Components
#

class AttributesPanel(Component):
    template_name = 'components/attributes_panel.html'

    def __init__(self, title, attrs):
        self.title = title
        self.attrs = attrs

    def render(self):
        return render_to_string(self.template_name, {
            'title': self.title,
            'attrs': self.attrs,
        })


class EmbeddedTemplate(Component):

    def __init__(self, template_name, context=None):
        self.template_name = template_name
        self.context = context or {}

    def render(self):
        return render_to_string(self.template_name, self.context)
