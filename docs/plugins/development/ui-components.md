# UI Components

!!! note "New in NetBox v4.5"
    All UI components described here were introduced in NetBox v4.5. Be sure to set the minimum NetBox version to 4.5.0 for your plugin before incorporating any of these resources.

!!! danger "Beta Feature"
    UI components are considered a beta feature, and are still under active development. Please be aware that the API for resources on this page is subject to change in future releases.

To simply the process of designing your plugin's user interface, and to encourage a consistent look and feel throughout the entire application, NetBox provides a set of components that enable programmatic UI design. These make it possible to declare complex page layouts with little or no custom HTML.

## Page Layout

A layout defines the general arrangement of content on a page into rows and columns. The layout is defined under the [view](./views.md) and declares a set of rows, each of which may have one or more columns. Below is an example layout.

```
+-------+-------+-------+
| Col 1 | Col 2 | Col 3 |
+-------+-------+-------+
|         Col 4         |
+-----------+-----------+
|   Col 5   |   Col 6   |
+-----------+-----------+
```

The above layout can be achieved with the following declaration under a view:

```python
from netbox.ui import layout
from netbox.views import generic

class MyView(generic.ObjectView):
    layout = layout.Layout(
        layout.Row(
            layout.Column(),
            layout.Column(),
            layout.Column(),
        ),
        layout.Row(
            layout.Column(),
        ),
        layout.Row(
            layout.Column(),
            layout.Column(),
        ),
    )
```

!!! note
    Currently, layouts are supported only for subclasses of [`generic.ObjectView`](./views.md#netbox.views.generic.ObjectView).

::: netbox.ui.layout.Layout

::: netbox.ui.layout.SimpleLayout

::: netbox.ui.layout.Row

::: netbox.ui.layout.Column

## Panels

Within each column, related blocks of content are arranged into panels. Each panel has a title and may have a set of associated actions, but the content within is otherwise arbitrary.

Plugins can define their own panels by inheriting from the base class `netbox.ui.panels.Panel`. Override the `get_context()` method to pass additional context to your custom panel template. An example is provided below.

```python
from django.utils.translation import gettext_lazy as _
from netbox.ui.panels import Panel

class RecentChangesPanel(Panel):
    template_name = 'my_plugin/panels/recent_changes.html'
    title = _('Recent Changes')

    def get_context(self, context):
        return {
            **super().get_context(context),
            'changes': get_changes()[:10],
        }
```

NetBox also includes a set of panels suite for specific uses, such as display object details or embedding a table of related objects. These are listed below.

::: netbox.ui.panels.Panel

::: netbox.ui.panels.ObjectPanel

::: netbox.ui.panels.ObjectAttributesPanel

#### Object Attributes

The following classes are available to represent object attributes within an ObjectAttributesPanel. Additionally, plugins can subclass `netbox.ui.attrs.ObjectAttribute` to create custom classes.

| Class                                | Description                                      |
|--------------------------------------|--------------------------------------------------|
| `netbox.ui.attrs.AddressAttr`        | A physical or mailing address.                   |
| `netbox.ui.attrs.BooleanAttr`        | A boolean value                                  |
| `netbox.ui.attrs.ColorAttr`          | A color expressed in RGB                         |
| `netbox.ui.attrs.ChoiceAttr`         | A selection from a set of choices                |
| `netbox.ui.attrs.GPSCoordinatesAttr` | GPS coordinates (latitude and longitude)         |
| `netbox.ui.attrs.ImageAttr`          | An attached image (displays the image)           |
| `netbox.ui.attrs.NestedObjectAttr`   | A related nested object                          |
| `netbox.ui.attrs.NumericAttr`        | An integer or float value                        |
| `netbox.ui.attrs.RelatedObjectAttr`  | A related object                                 |
| `netbox.ui.attrs.TemplatedAttr`      | Renders an attribute using a custom template     |
| `netbox.ui.attrs.TextAttr`           | A string (text) value                            |
| `netbox.ui.attrs.TimezoneAttr`       | A timezone with annotated offset                 |
| `netbox.ui.attrs.UtilizationAttr`    | A numeric value expressed as a utilization graph |

::: netbox.ui.panels.OrganizationalObjectPanel

::: netbox.ui.panels.NestedGroupObjectPanel

::: netbox.ui.panels.CommentsPanel

::: netbox.ui.panels.JSONPanel

::: netbox.ui.panels.RelatedObjectsPanel

::: netbox.ui.panels.ObjectsTablePanel

::: netbox.ui.panels.TemplatePanel

::: netbox.ui.panels.PluginContentPanel

## Panel Actions

Each panel may have actions associated with it. These render as links or buttons within the panel header, opposite the panel's title. For example, a common use case is to include an "Add" action on a panel which displays a list of objects. Below is an example of this.

```python
from django.utils.translation import gettext_lazy as _
from netbox.ui import actions, panels

panels.ObjectsTablePanel(
    model='dcim.Region',
    title=_('Child Regions'),
    filters={'parent_id': lambda ctx: ctx['object'].pk},
    actions=[
        actions.AddObject('dcim.Region', url_params={'parent': lambda ctx: ctx['object'].pk}),
    ],
),
```

::: netbox.ui.actions.PanelAction

::: netbox.ui.actions.LinkAction

::: netbox.ui.actions.AddObject

::: netbox.ui.actions.CopyContent
