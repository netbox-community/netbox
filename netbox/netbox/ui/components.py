from abc import ABC, ABCMeta, abstractmethod
from functools import cached_property

from django.template.loader import render_to_string

from netbox.ui.attrs import Attr
from utilities.string import title


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


class ObjectPanel(Component, metaclass=ObjectDetailsPanelMeta):
    template_name = 'components/object_details_panel.html'

    def __init__(self, obj, title=None):
        self.object = obj
        self.title = title or obj._meta.verbose_name

    @cached_property
    def attributes(self):
        return [
            {
                'label': attr.label or title(name),
                'value': attr.render(self.object, {'name': name}),
            } for name, attr in self._attrs.items()
        ]

    def render(self):
        return render_to_string(self.template_name, {
            'title': self.title,
            'attrs': self.attributes,
        })

    def __str__(self):
        return self.render()
