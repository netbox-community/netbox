from abc import ABC, ABCMeta, abstractmethod

from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs
from netbox.ui.attrs import Attr
from utilities.querydict import dict_to_querydict
from utilities.string import title
from utilities.templatetags.plugins import _get_registered_content

__all__ = (
    'CommentsPanel',
    'CustomFieldsPanel',
    'EmbeddedTablePanel',
    'ImageAttachmentsPanel',
    'NestedGroupObjectPanel',
    'ObjectPanel',
    'RelatedObjectsPanel',
    'Panel',
    'PluginContentPanel',
    'TagsPanel',
)


class Panel(ABC):

    def __init__(self, title=None):
        if title is not None:
            self.title = title

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


class CustomFieldsPanel(Panel):
    template_name = 'ui/panels/custom_fields.html'
    title = _('Custom Fields')

    def render(self, context):
        obj = context.get('object')
        custom_fields = obj.get_custom_fields_by_group()
        if not custom_fields:
            return ''
        return render_to_string(self.template_name, {
            'title': self.title,
            'custom_fields': custom_fields,
        })


class TagsPanel(Panel):
    template_name = 'ui/panels/tags.html'
    title = _('Tags')

    def render(self, context):
        return render_to_string(self.template_name, {
            'title': self.title,
            'object': context.get('object'),
        })


class CommentsPanel(Panel):
    template_name = 'ui/panels/comments.html'
    title = _('Comments')

    def render(self, context):
        obj = context.get('object')
        return render_to_string(self.template_name, {
            'title': self.title,
            'comments': obj.comments,
        })


class RelatedObjectsPanel(Panel):
    template_name = 'ui/panels/related_objects.html'
    title = _('Related Objects')

    def render(self, context):
        return render_to_string(self.template_name, {
            'title': self.title,
            'object': context.get('object'),
            'related_models': context.get('related_models'),
        })


class ImageAttachmentsPanel(Panel):
    template_name = 'ui/panels/image_attachments.html'
    title = _('Image Attachments')

    def render(self, context):
        return render_to_string(self.template_name, {
            'title': self.title,
            'request': context.get('request'),
            'object': context.get('object'),
        })


class EmbeddedTablePanel(Panel):
    template_name = 'ui/panels/embedded_table.html'
    title = None

    def __init__(self, viewname, url_params=None, **kwargs):
        super().__init__(**kwargs)
        self.viewname = viewname
        self.url_params = url_params or {}

    def render(self, context):
        obj = context.get('object')
        url_params = {
            k: v(obj) if callable(v) else v for k, v in self.url_params.items()
        }
        # url_params['return_url'] = return_url or context['request'].path
        return render_to_string(self.template_name, {
            'title': self.title,
            'viewname': self.viewname,
            'url_params': dict_to_querydict(url_params),
        })


class PluginContentPanel(Panel):

    def __init__(self, method, **kwargs):
        super().__init__(**kwargs)
        self.method = method

    def render(self, context):
        obj = context.get('object')
        return _get_registered_content(obj, self.method, context)
