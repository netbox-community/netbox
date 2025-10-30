from abc import ABC, ABCMeta, abstractmethod
from functools import cached_property

from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs
from netbox.ui.attrs import Attr
from utilities.string import title


class Component(ABC):

    @abstractmethod
    def render(self):
        pass

    def __str__(self):
        return self.render()


class ObjectDetailsPanelMeta(ABCMeta):

    def __new__(mcls, name, bases, namespace, **kwargs):
        declared = {}

        # Walk MRO parents (excluding `object`) for declared attributes
        for base in reversed([b for b in bases if hasattr(b, "_attrs")]):
            for key, attr in getattr(base, '_attrs', {}).items():
                if key not in declared:
                    declared[key] = attr

        # Add local declarations in the order they appear in the class body
        for key, attr in namespace.items():
            if isinstance(attr, Attr):
                declared[key] = attr

        namespace['_attrs'] = declared

        # Remove Attrs from the class namespace to keep things tidy
        local_items = [key for key, attr in namespace.items() if isinstance(attr, Attr)]
        for key in local_items:
            namespace.pop(key)

        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        return cls


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


class NestedGroupObjectPanel(ObjectPanel, metaclass=ObjectDetailsPanelMeta):
    name = attrs.TextAttr('name', label=_('Name'))
    description = attrs.TextAttr('description', label=_('Description'))
    parent = attrs.NestedObjectAttr('parent', label=_('Parent'), linkify=True)
