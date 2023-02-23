import uuid

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from utilities.forms import BootstrapMixin
from utilities.templatetags.builtins.filters import render_markdown
from utilities.utils import content_type_identifier, content_type_name
from .utils import register_widget

__all__ = (
    'ChangeLogWidget',
    'DashboardWidget',
    'NoteWidget',
    'ObjectCountsWidget',
)


def get_content_type_labels():
    return [
        (content_type_identifier(ct), content_type_name(ct))
        for ct in ContentType.objects.order_by('app_label', 'model')
    ]


class DashboardWidget:
    default_title = None
    description = None
    width = 4
    height = 3

    class ConfigForm(forms.Form):
        pass

    def __init__(self, id=None, title=None, color=None, config=None, width=None, height=None, x=None, y=None):
        self.id = id or uuid.uuid4()
        self.config = config or {}
        self.title = title or self.default_title
        self.color = color
        if width:
            self.width = width
        if height:
            self.height = height
        self.x, self.y = x, y

    def __str__(self):
        return self.title or self.__class__.__name__

    def set_layout(self, grid_item):
        self.width = grid_item['w']
        self.height = grid_item['h']
        self.x = grid_item.get('x')
        self.y = grid_item.get('y')

    def render(self, request):
        raise NotImplementedError(f"{self.__class__} must define a render() method.")

    @property
    def name(self):
        return f'{self.__class__.__module__}.{self.__class__.__name__}'


@register_widget
class NoteWidget(DashboardWidget):
    description = _('Display some arbitrary custom content. Markdown is supported.')

    class ConfigForm(BootstrapMixin, forms.Form):
        content = forms.CharField(
            widget=forms.Textarea()
        )

    def render(self, request):
        return render_markdown(self.config.get('content'))


@register_widget
class ObjectCountsWidget(DashboardWidget):
    default_title = _('Objects')
    description = _('Display a set of NetBox models and the number of objects created for each type.')
    template_name = 'extras/dashboard/widgets/objectcounts.html'

    class ConfigForm(BootstrapMixin, forms.Form):
        models = forms.MultipleChoiceField(
            choices=get_content_type_labels
        )

    def render(self, request):
        counts = []
        for content_type_id in self.config['models']:
            app_label, model_name = content_type_id.split('.')
            model = ContentType.objects.get_by_natural_key(app_label, model_name).model_class()
            object_count = model.objects.restrict(request.user, 'view').count
            counts.append((model, object_count))

        return render_to_string(self.template_name, {
            'counts': counts,
        })


@register_widget
class ChangeLogWidget(DashboardWidget):
    default_title = _('Change Log')
    description = _('Display the most recent records from the global change log.')
    template_name = 'extras/dashboard/widgets/changelog.html'
    width = 12
    height = 4

    def render(self, request):
        return render_to_string(self.template_name, {})
