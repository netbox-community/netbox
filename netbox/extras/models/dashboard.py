from django.db import models
from django.utils.translation import gettext_lazy as _

from extras.dashboard.utils import get_widget_class

__all__ = (
    'Dashboard',
)


class Dashboard(models.Model):
    user = models.OneToOneField(
        to='users.User',
        on_delete=models.CASCADE,
        related_name='dashboard'
    )
    layout = models.JSONField(
        verbose_name=_('layout'),
        default=list
    )
    config = models.JSONField(
        verbose_name=_('config'),
        default=dict
    )

    class Meta:
        verbose_name = _('dashboard')
        verbose_name_plural = _('dashboards')

    def get_widget(self, id):
        """
        Instantiate and return a widget by its ID
        """
        id = str(id)
        config = dict(self.config[id])  # Copy to avoid mutating instance data
        widget_class = get_widget_class(config.pop('class'))
        return widget_class(id=id, **config)

    def get_layout(self):
        """
        Return the dashboard's configured layout, suitable for rendering with gridstack.js.
        """
        widgets = []
        for grid_item in self.layout:
            widget = self.get_widget(grid_item['id'])
            widget.set_layout(grid_item)
            widgets.append(widget)
        return widgets

    def add_widget(self, widget, x=None, y=None):
        """
        Add a widget to the dashboard, optionally specifying its X & Y coordinates.
        """
        id = str(widget.id)
        self.config[id] = {
            'class': widget.name,
            'title': widget.title,
            'color': widget.color,
            'config': widget.config,
        }
        self.layout.append({
            'id': id,
            'h': widget.height,
            'w': widget.width,
            'x': x,
            'y': y,
        })

    def delete_widget(self, id):
        """
        Delete a widget from the dashboard.
        """
        id = str(id)
        del self.config[id]
        self.layout = [
            item for item in self.layout if item['id'] != id
        ]
