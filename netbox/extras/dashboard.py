import uuid

from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from netbox.registry import registry


__all__ = (
    'ChangeLogWidget',
    'DashboardWidget',
    'ObjectCountsWidget',
    'StaticContentWidget',
    'register_widget',
)


def register_widget(cls):
    """
    Decorator for registering a DashboardWidget class.
    """
    label = f'{cls.__module__}.{cls.__name__}'
    registry['widgets'][label] = cls

    return cls


class DashboardWidget:
    width = 4
    height = 3

    def __init__(self, id=None, config=None, title=None, width=None, height=None, x=None, y=None):
        self.id = id or uuid.uuid4()
        self.config = config or {}
        if title:
            self.title = title
        if width:
            self.width = width
        if height:
            self.height = height
        self.x, self.y = x, y

    def render(self, request):
        raise NotImplementedError("DashboardWidget subclasses must define a render() method.")

    @property
    def name(self):
        return f'{self.__class__.__module__}.{self.__class__.__name__}'


@register_widget
class StaticContentWidget(DashboardWidget):

    def render(self, request):
        return self.config.get('content', 'Empty!')


@register_widget
class ObjectCountsWidget(DashboardWidget):
    title = _('Objects')
    template_name = 'extras/dashboard/widgets/objectcounts.html'

    def render(self, request):
        counts = []
        for model_name in self.config['models']:
            app_label, name = model_name.lower().split('.')
            model = ContentType.objects.get_by_natural_key(app_label, name).model_class()
            object_count = model.objects.restrict(request.user, 'view').count
            counts.append((model, object_count))

        return render_to_string(self.template_name, {
            'counts': counts,
        })


@register_widget
class ChangeLogWidget(DashboardWidget):
    width = 12
    height = 4
    title = _('Change log')
    template_name = 'extras/dashboard/widgets/changelog.html'

    def render(self, request):
        return render_to_string(self.template_name, {})
