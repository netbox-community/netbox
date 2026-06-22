from django.template.loader import render_to_string

from netbox.registry import registry
from utilities.data import resolve_attr_path

__all__ = (
    'Breadcrumb',
    'BreadcrumbTrail',
    'get_breadcrumbs',
    'register_breadcrumbs',
)


class Breadcrumb:
    """
    A navigation breadcrumb rendered at the top of an object view.

    Rather than wrapping a static value, a breadcrumb references an attribute on the object being viewed. This
    allows breadcrumbs to be declared once on a layout (alongside its panels) and rendered dynamically for each
    object. A breadcrumb whose resolved value is empty renders as an empty string and is omitted, which simplifies
    conditional breadcrumbs (e.g. where a device may or may not be assigned to a rack).

    Attributes:
        template_name (str): The name of the template used to render the breadcrumb

    Parameters:
        accessor: The dotted path to the related object on the viewed instance (e.g. "site" or "device.rack"),
            or a callable which accepts the instance and returns the related object. If the resolved value is an
            iterable of objects, a breadcrumb is rendered for each (e.g. to represent a hierarchy of ancestors).
        url: An optional URL for the breadcrumb's link. May be a string, or a callable which accepts the resolved
            object and returns a URL. If omitted, the object's `get_absolute_url()` is used when available.
    """
    template_name = 'ui/breadcrumb.html'

    def __init__(self, accessor, url=None):
        self.accessor = accessor
        self.url = url

    def resolve(self, instance):
        """
        Resolve the breadcrumb's accessor against the viewed instance and return the related object(s).
        """
        if callable(self.accessor):
            return self.accessor(instance)
        return resolve_attr_path(instance, self.accessor)

    def get_url(self, obj):
        """
        Return the URL to link the given object to, or None for an unlinked breadcrumb.
        """
        if self.url is not None:
            return self.url(obj) if callable(self.url) else self.url
        if hasattr(obj, 'get_absolute_url'):
            return obj.get_absolute_url()
        return None

    def render(self, context=None):
        instance = context.get('object') if context else None
        if instance is None:
            return ''
        value = self.resolve(instance)
        if value is None:
            return ''

        # A resolved iterable (e.g. a queryset of ancestors) yields one breadcrumb per object
        objects = value if self._is_iterable(value) else [value]

        return ''.join(
            render_to_string(self.template_name, {
                'url': self.get_url(obj),
                'label': str(obj),
            })
            for obj in objects if obj is not None
        )

    @staticmethod
    def _is_iterable(value):
        if isinstance(value, (str, bytes)):
            return False
        return hasattr(value, '__iter__')


class BreadcrumbTrail:
    """
    The ordered breadcrumb trail for a model, registered once and shared across all of that model's object
    views (its detail view and every peer/tabbed view). Defining the trail per-model rather than per-view
    ensures a consistent trail throughout an object's views without repeating breadcrumb declarations.

    Attributes:
        model: The model class to which this trail applies.
        items: An ordered iterable of `Breadcrumb` instances, rendered after the default breadcrumb linking
            to the object's list view.
    """
    model = None
    items = ()

    @classmethod
    def render(cls, context):
        return ''.join(item.render(context) for item in cls.items)


def register_breadcrumbs(cls):
    """
    Register a `BreadcrumbTrail` subclass for its model, so it can be resolved by any view of that model.
    """
    label = f'{cls.model._meta.app_label}.{cls.model._meta.model_name}'
    registry['breadcrumbs'][label] = cls
    return cls


def get_breadcrumbs(model):
    """
    Return the registered `BreadcrumbTrail` for the given model, or None if none has been registered.
    """
    label = f'{model._meta.app_label}.{model._meta.model_name}'
    return registry['breadcrumbs'].get(label)
