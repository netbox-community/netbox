from abc import ABC, ABCMeta, abstractmethod

from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs
from netbox.ui.attrs import Attr
from utilities.string import title

__all__ = (
    'NestedGroupObjectPanel',
    'ObjectPanel',
    'Panel',
)


class Panel(ABC):

    @abstractmethod
    def render(self, obj):
        pass


class ObjectPanelMeta(ABCMeta):

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


class ObjectPanel(Panel, metaclass=ObjectPanelMeta):
    template_name = 'ui/panels/object.html'

    def __init__(self, title=None):
        self.title = title

    def get_attributes(self, obj):
        return [
            {
                'label': attr.label or title(name),
                'value': attr.render(obj, {'name': name}),
            } for name, attr in self._attrs.items()
        ]

    def render(self, context):
        obj = context.get('object')
        return render_to_string(self.template_name, {
            'title': self.title,
            'attrs': self.get_attributes(obj),
        })


class NestedGroupObjectPanel(ObjectPanel, metaclass=ObjectPanelMeta):
    name = attrs.TextAttr('name', label=_('Name'))
    description = attrs.TextAttr('description', label=_('Description'))
    parent = attrs.NestedObjectAttr('parent', label=_('Parent'), linkify=True)
