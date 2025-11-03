from abc import ABC, ABCMeta

from django.apps import apps
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs
from utilities.querydict import dict_to_querydict
from utilities.string import title
from utilities.templatetags.plugins import _get_registered_content
from utilities.views import get_viewname

__all__ = (
    'CommentsPanel',
    'NestedGroupObjectPanel',
    'ObjectPanel',
    'ObjectsTablePanel',
    'OrganizationalObjectPanel',
    'RelatedObjectsPanel',
    'Panel',
    'PluginContentPanel',
    'TemplatePanel',
)


class Panel(ABC):
    template_name = None
    title = None
    actions = []

    def __init__(self, title=None, actions=None):
        if title is not None:
            self.title = title
        if actions is not None:
            self.actions = actions

    def get_context(self, context):
        return {
            'request': context.get('request'),
            'title': self.title,
            'actions': [action.get_context(context) for action in self.actions],
        }

    def render(self, context):
        return render_to_string(self.template_name, self.get_context(context))


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
            if isinstance(attr, attrs.Attr):
                declared[key] = attr

        namespace['_attrs'] = declared

        # Remove Attrs from the class namespace to keep things tidy
        local_items = [key for key, attr in namespace.items() if isinstance(attr, attrs.Attr)]
        for key in local_items:
            namespace.pop(key)

        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        return cls


class ObjectPanel(Panel, metaclass=ObjectPanelMeta):
    accessor = None
    template_name = 'ui/panels/object.html'

    def __init__(self, accessor=None, only=None, exclude=None, **kwargs):
        super().__init__(**kwargs)
        if accessor is not None:
            self.accessor = accessor

        # Set included/excluded attributes
        if only is not None and exclude is not None:
            raise ValueError("attrs and exclude cannot both be specified.")
        self.only = only or []
        self.exclude = exclude or []

    def get_context(self, context):
        # Determine which attributes to display in the panel based on only/exclude args
        attr_names = set(self._attrs.keys())
        if self.only:
            attr_names &= set(self.only)
        elif self.exclude:
            attr_names -= set(self.exclude)

        obj = getattr(context['object'], self.accessor) if self.accessor else context['object']

        return {
            **super().get_context(context),
            'object': obj,
            'attrs': [
                {
                    'label': attr.label or title(name),
                    'value': attr.render(obj, {'name': name}),
                } for name, attr in self._attrs.items() if name in attr_names
            ],
        }


class OrganizationalObjectPanel(ObjectPanel, metaclass=ObjectPanelMeta):
    name = attrs.TextAttr('name', label=_('Name'))
    description = attrs.TextAttr('description', label=_('Description'))


class NestedGroupObjectPanel(OrganizationalObjectPanel, metaclass=ObjectPanelMeta):
    parent = attrs.NestedObjectAttr('parent', label=_('Parent'), linkify=True)


class CommentsPanel(Panel):
    template_name = 'ui/panels/comments.html'
    title = _('Comments')


class RelatedObjectsPanel(Panel):
    template_name = 'ui/panels/related_objects.html'
    title = _('Related Objects')

    def get_context(self, context):
        return {
            **super().get_context(context),
            'related_models': context.get('related_models'),
        }


class ObjectsTablePanel(Panel):
    template_name = 'ui/panels/objects_table.html'
    title = None

    def __init__(self, model, filters=None, **kwargs):
        super().__init__(**kwargs)

        # Resolve the model class from its app.name label
        app_label, model_name = model.split('.')
        self.model = apps.get_model(app_label, model_name)
        self.filters = filters or {}
        if self.title is None:
            self.title = title(self.model._meta.verbose_name_plural)

    def get_context(self, context):
        url_params = {
            k: v(context) if callable(v) else v for k, v in self.filters.items()
        }
        if 'return_url' not in url_params and 'object' in context:
            url_params['return_url'] = context['object'].get_absolute_url()
        return {
            **super().get_context(context),
            'viewname': get_viewname(self.model, 'list'),
            'url_params': dict_to_querydict(url_params),
        }


class TemplatePanel(Panel):

    def __init__(self, template_name, **kwargs):
        super().__init__(**kwargs)
        self.template_name = template_name

    def render(self, context):
        # Pass the entire context to the template
        return render_to_string(self.template_name, context.flatten())


class PluginContentPanel(Panel):

    def __init__(self, method, **kwargs):
        super().__init__(**kwargs)
        self.method = method

    def render(self, context):
        obj = context.get('object')
        return _get_registered_content(obj, self.method, context)
