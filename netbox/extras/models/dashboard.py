from django.contrib.auth import get_user_model
from django.db import models

__all__ = (
    'Dashboard',
)


class Dashboard(models.Model):
    user = models.OneToOneField(
        to=get_user_model(),
        on_delete=models.CASCADE,
        related_name='dashboard'
    )
    layout = models.JSONField()
    config = models.JSONField()

    class Meta:
        pass

    def add_widget(self, widget, x=None, y=None):
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
        del self.config[id]
        self.layout = [
            item for item in self.layout if item['id'] != id
        ]
