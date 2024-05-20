# Dashboard Widgets

Each NetBox user can customize his or her personal dashboard by adding and removing widgets and by manipulating the size and position of each. Plugins can register their own dashboard widgets to complement those already available natively.

## The DashboardWidget Class

All dashboard widgets must inherit from NetBox's `DashboardWidget` base class. Subclasses must provide a `render()` method, and may override the base class' default characteristics.

Widgets which require configuration by a user must also include a `ConfigForm` child class which inherits from `WidgetConfigForm`. This form is used to render the user configuration options for the widget.

::: extras.dashboard.widgets.DashboardWidget

## Widget Registration

To register a dashboard widget for use in NetBox, import the `register_widget()` decorator and use it to wrap each `DashboardWidget` subclass:

```python
from extras.dashboard.widgets import DashboardWidget, register_widget

@register_widget
class MyWidget1(DashboardWidget):
    ...

@register_widget
class MyWidget2(DashboardWidget):
    ...
```

## Example

```python
from django import forms
from extras.dashboard.utils import register_widget
from extras.dashboard.widgets import DashboardWidget, WidgetConfigForm


@register_widget
class ReminderWidget(DashboardWidget):
    default_title = 'Reminder'
    description = 'Add a virtual sticky note'

    class ConfigForm(WidgetConfigForm):
        content = forms.CharField(
            widget=forms.Textarea()
        )

    def render(self, request):
        return self.config.get('content')
```

## Initialization

To register the widget, it becomes essential to import the widget module. The recommended approach is to accomplish this within the `ready` method situated in your `PluginConfig`:

```python
class FooBarConfig(PluginConfig):
    def ready(self):
        super().ready()
        from . import widgets  # point this to the above widget module you created
```
