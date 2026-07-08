# UI Components

!!! note "New in NetBox v4.6"
    All UI components described here were introduced in NetBox v4.6. Be sure to set the minimum NetBox version to 4.6.0 for your plugin before incorporating any of these resources.

To simplify the process of designing your plugin's user interface, and to encourage a consistent look and feel throughout the entire application, NetBox provides a set of components that enable programmatic UI design. These make it possible to declare complex page layouts with little or no custom HTML.

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

## Breadcrumbs

Breadcrumbs are rendered at the top of an object's page to convey its position within a hierarchy and to provide quick navigation to related objects. By default, a single breadcrumb linking to the object's list view is shown. To add object-specific breadcrumbs, pass a list of `Breadcrumb` instances to your layout, just as you would its panels.

A `Breadcrumb` typically references an _accessor_ (rather than a static value), which is resolved against the object being viewed when the page is rendered. The accessor may be a dotted attribute path or a callable. (A breadcrumb may instead define a static `label`; see below.)

```python
from netbox.ui import layout
from netbox.ui.breadcrumbs import Breadcrumb
from netbox.views import generic

class MyView(generic.ObjectView):
    layout = layout.SimpleLayout(
        breadcrumbs=[
            Breadcrumb('site'),
            Breadcrumb('location'),
            Breadcrumb('rack'),
        ],
        left_panels=[...],
        right_panels=[...],
    )
```

Each breadcrumb renders as a label (the string representation of the resolved object) and an optional link. If no explicit `url` is provided, the object's `get_absolute_url()` is used when available. A breadcrumb whose accessor resolves to `None` (or an empty iterable) renders as an empty string and is omitted, which simplifies conditional breadcrumbs (e.g. where a device may or may not be assigned to a rack).

To link a breadcrumb somewhere other than the related object's own page (for example, to a filtered list view), pass a `url`. A callable `url` receives the resolved object:

```python
from django.urls import reverse

Breadcrumb('rir', url=lambda rir: f"{reverse('ipam:asn_list')}?rir_id={rir.pk}")
```

A callable accessor which returns an iterable renders one breadcrumb per object, which is useful for representing a hierarchy of ancestors:

```python
Breadcrumb(lambda obj: obj.get_ancestors())
```

To render a breadcrumb that isn't tied to a related object, omit the accessor and pass a `label`. This is useful for linking to a parent view that isn't reachable via an attribute on the object (e.g. a user's personal token list):

```python
from django.urls import reverse_lazy

Breadcrumb(label=_('My API Tokens'), url=reverse_lazy('account:usertoken_list'))
```

The `label` may also be a callable, which receives the relevant object (the resolved related object when an accessor is given, otherwise the viewed instance). This is useful for an unlinked descriptive crumb derived from the object:

```python
Breadcrumb(label=lambda obj: f"{_('Units')} {obj.unit_list}")
```

The default root breadcrumb (linking to the object's list view) is prepended to the trail automatically. Where that list view isn't an appropriate root—for example, the global token list is admin-only, so a user's personal token page links to their own token list instead—pass `root_breadcrumb=False` to the layout and supply a replacement as the first breadcrumb:

```python
SimpleLayout(
    root_breadcrumb=False,
    breadcrumbs=[
        Breadcrumb(label=_('My API Tokens'), url=reverse_lazy('account:usertoken_list')),
    ],
    ...
)
```

::: netbox.ui.breadcrumbs.Breadcrumb

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

    def should_render(self, context):
        return len(context['changes']) > 0
```

NetBox also includes a set of panels suited for specific uses, such as displaying object details or embedding a table of related objects. These are listed below.

::: netbox.ui.panels.Panel

::: netbox.ui.panels.ObjectPanel

::: netbox.ui.panels.ObjectAttributesPanel

::: netbox.ui.panels.OrganizationalObjectPanel

::: netbox.ui.panels.NestedGroupObjectPanel

::: netbox.ui.panels.CommentsPanel

::: netbox.ui.panels.JSONPanel

::: netbox.ui.panels.RelatedObjectsPanel

::: netbox.ui.panels.ObjectsTablePanel

::: netbox.ui.panels.TemplatePanel

::: netbox.ui.panels.TextCodePanel

::: netbox.ui.panels.ContextTablePanel

::: netbox.ui.panels.PluginContentPanel

### Panel Actions

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

## Object Attributes

The following classes are available to represent object attributes within an ObjectAttributesPanel. Additionally, plugins can subclass `netbox.ui.attrs.ObjectAttribute` to create custom classes.

| Class                                   | Description                                         |
|-----------------------------------------|-----------------------------------------------------|
| `netbox.ui.attrs.AddressAttr`           | A physical or mailing address.                      |
| `netbox.ui.attrs.ArrayAttr`             | An array of values, shown as a comma-separated list |
| `netbox.ui.attrs.BooleanAttr`           | A boolean value                                     |
| `netbox.ui.attrs.ChoiceAttr`            | A selection from a set of choices                   |
| `netbox.ui.attrs.ColorAttr`             | A color expressed in RGB                            |
| `netbox.ui.attrs.DateTimeAttr`          | A date or datetime value                            |
| `netbox.ui.attrs.GenericForeignKeyAttr` | A related object via a generic foreign key          |
| `netbox.ui.attrs.GPSCoordinatesAttr`    | GPS coordinates (latitude and longitude)            |
| `netbox.ui.attrs.ImageAttr`             | An attached image (displays the image)              |
| `netbox.ui.attrs.NestedObjectAttr`      | A related nested object (includes ancestors)        |
| `netbox.ui.attrs.NumericAttr`           | An integer or float value                           |
| `netbox.ui.attrs.RelatedObjectAttr`     | A related object                                    |
| `netbox.ui.attrs.RelatedObjectListAttr` | A list of related objects                           |
| `netbox.ui.attrs.TemplatedAttr`         | Renders an attribute using a custom template        |
| `netbox.ui.attrs.TextAttr`              | A string (text) value                               |
| `netbox.ui.attrs.TimezoneAttr`          | A timezone with annotated offset                    |
| `netbox.ui.attrs.UtilizationAttr`       | A numeric value expressed as a utilization graph    |

::: netbox.ui.attrs.ObjectAttribute

::: netbox.ui.attrs.AddressAttr

::: netbox.ui.attrs.ArrayAttr

::: netbox.ui.attrs.BooleanAttr

::: netbox.ui.attrs.ChoiceAttr

::: netbox.ui.attrs.ColorAttr

::: netbox.ui.attrs.DateTimeAttr

::: netbox.ui.attrs.GenericForeignKeyAttr

::: netbox.ui.attrs.GPSCoordinatesAttr

::: netbox.ui.attrs.ImageAttr

::: netbox.ui.attrs.NestedObjectAttr

::: netbox.ui.attrs.NumericAttr

::: netbox.ui.attrs.RelatedObjectAttr

::: netbox.ui.attrs.RelatedObjectListAttr

::: netbox.ui.attrs.TemplatedAttr

::: netbox.ui.attrs.TextAttr

::: netbox.ui.attrs.TimezoneAttr

::: netbox.ui.attrs.UtilizationAttr
