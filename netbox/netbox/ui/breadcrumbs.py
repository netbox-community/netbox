from django.template.loader import render_to_string
from django.urls import NoReverseMatch, reverse

from utilities.data import resolve_attr_path

__all__ = (
    'Breadcrumb',
    'filtered_list_url',
    'get_root_breadcrumb',
    'object_view_url',
)


def filtered_list_url(viewname, filter_param):
    """
    Return a callable suitable for a `Breadcrumb`'s `url`, linking to a list view filtered by the
    resolved object's primary key. For example, `filtered_list_url('dcim:rack_list', 'site_id')`
    produces a URL of the form `{rack_list}?site_id=<pk>`.
    """
    return lambda obj: f"{reverse(viewname)}?{filter_param}={obj.pk}"


def object_view_url(viewname):
    """
    Return a callable suitable for a `Breadcrumb`'s `url`, linking to a view keyed by the resolved
    object's primary key. For example, `object_view_url('dcim:device_interfaces')` produces the URL
    `reverse('dcim:device_interfaces', kwargs={'pk': <pk>})`.
    """
    return lambda obj: reverse(viewname, kwargs={'pk': obj.pk})


def get_root_breadcrumb(instance):
    """
    Return the default root `Breadcrumb` for a model instance: a link to the model's list view,
    labeled with the model's plural verbose name. This is prepended automatically to every object
    view's trail unless the view's layout opts out via `root_breadcrumb=False`.
    """
    from utilities.templatetags.builtins.filters import bettertitle
    from utilities.views import get_action_url

    label = bettertitle(instance._meta.verbose_name_plural)
    try:
        url = get_action_url(instance, 'list')
    except NoReverseMatch:
        url = None
    return Breadcrumb(label=label, url=url)


class Breadcrumb:
    """
    A navigation breadcrumb rendered at the top of an object view.

    Rather than wrapping a static value, a breadcrumb typically references an attribute on the object being viewed.
    This allows breadcrumbs to be declared once on a layout (alongside its panels) and rendered dynamically for each
    object. A breadcrumb whose resolved value is empty renders as an empty string and is omitted, which simplifies
    conditional breadcrumbs (e.g. where a device may or may not be assigned to a rack).

    A breadcrumb may instead define a static `label`, omitting the accessor entirely. This renders a single
    breadcrumb describing the viewed object directly (or a fixed destination) rather than a related object, which is
    useful for linking to a parent view that isn't a related object (e.g. a user's personal token list) or for an
    unlinked descriptive crumb (e.g. "Units 1-5" on a rack reservation).

    Attributes:
        template_name (str): The name of the template used to render the breadcrumb

    Parameters:
        accessor: The dotted path to the related object on the viewed instance (e.g. "site" or "device.rack"),
            or a callable which accepts the instance and returns the related object. If the resolved value is an
            iterable of objects, a breadcrumb is rendered for each (e.g. to represent a hierarchy of ancestors).
            Omit this (and pass `label`) to render a single breadcrumb describing the viewed object itself.
        label: A label for the breadcrumb. Required when `accessor` is omitted. May be a string, or a callable
            which accepts the relevant object (the resolved related object when an accessor is given, otherwise the
            viewed instance) and returns the label. When an accessor is given and no label is set, the resolved
            object's string representation is used.
        url: An optional URL for the breadcrumb's link. May be a string, or a callable which accepts the relevant
            object and returns a URL. When an accessor is given and no url is set, the resolved object's
            `get_absolute_url()` is used where available; an accessor-less breadcrumb is left unlinked instead.
    """
    template_name = 'ui/breadcrumb.html'

    def __init__(self, accessor=None, label=None, url=None):
        if accessor is None and label is None:
            raise ValueError("A Breadcrumb must define an accessor, a static label, or both.")
        self.accessor = accessor
        self.label = label
        self.url = url

    def resolve(self, instance):
        """
        Resolve the breadcrumb's accessor against the viewed instance and return the related object(s).
        """
        if callable(self.accessor):
            return self.accessor(instance)
        return resolve_attr_path(instance, self.accessor)

    def get_label(self, obj):
        """
        Return the breadcrumb's label for the given object, falling back to its string representation.
        """
        if callable(self.label):
            return self.label(obj) if obj is not None else None
        if self.label is not None:
            return self.label
        return str(obj) if obj is not None else None

    def get_url(self, obj, fallback=True):
        """
        Return the URL to link the given object to, or None for an unlinked breadcrumb. When `fallback` is True,
        an object's `get_absolute_url()` is used in the absence of an explicit url.
        """
        if self.url is not None:
            return self.url(obj) if callable(self.url) else self.url
        if fallback and obj is not None and hasattr(obj, 'get_absolute_url'):
            return obj.get_absolute_url()
        return None

    def render(self, context=None):
        instance = context.get('object') if context else None

        # A breadcrumb without an accessor describes the viewed object directly (or a fixed destination), rather
        # than a related object, and renders a single crumb. It is left unlinked unless an explicit url is given.
        if self.accessor is None:
            label = self.get_label(instance)
            if not label:
                return ''
            return render_to_string(self.template_name, {
                'url': self.get_url(instance, fallback=False),
                'label': label,
            })

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
                'label': self.get_label(obj),
            })
            for obj in objects if obj is not None
        )

    @staticmethod
    def _is_iterable(value):
        if isinstance(value, (str, bytes)):
            return False
        return hasattr(value, '__iter__')
