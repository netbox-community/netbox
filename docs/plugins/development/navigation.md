# Navigation

## Menus

A plugin can register its own submenu as part of NetBox's navigation menu. This is done by defining a variable named `menu` in `navigation.py`, pointing to an instance of the `PluginMenu` class. Each menu must define a label and grouped menu items (discussed below), and may optionally specify an icon. An example is shown below.

```python title="navigation.py"
from netbox.plugins import PluginMenu

menu = PluginMenu(
    label='My Plugin',
    groups=(
        ('Foo', (item1, item2, item3)),
        ('Bar', (item4, item5)),
    ),
    icon_class='mdi mdi-router'
)
```

Note that each group is a two-tuple containing a label and an iterable of menu items. The group's label serves as the section header within the submenu. A group label is required even if you have only one group of items.

!!! tip
    The path to the menu class can be modified by setting `menu` in the PluginConfig instance.

A `PluginMenu` has the following attributes:

| Attribute    | Required | Description                                       |
|--------------|----------|---------------------------------------------------|
| `label`      | Yes      | The text displayed as the menu heading            |
| `groups`     | Yes      | An iterable of named groups containing menu items |
| `icon_class` | -        | The CSS name of the icon to use for the heading   |

!!! tip
    Supported icons can be found at [Material Design Icons](https://materialdesignicons.com/)

### The Default Menu

If your plugin has only a small number of menu items, it may be desirable to use NetBox's shared "Plugins" menu rather than creating your own. To do this, simply declare `menu_items` as a list of `PluginMenuItems` in `navigation.py`. The listed items will appear under a heading bearing the name of your plugin in the "Plugins" submenu.

```python title="navigation.py"
menu_items = (item1, item2, item3)
```

!!! tip
    The path to the menu items list can be modified by setting `menu_items` in the PluginConfig instance.

## Menu Items

Each menu item represents a link and (optionally) a set of buttons comprising one entry in NetBox's navigation menu. Menu items are defined as PluginMenuItem instances. An example is shown below.

```python title="navigation.py"
from netbox.choices import ButtonColorChoices
from netbox.plugins import PluginMenuButton, PluginMenuItem

item1 = PluginMenuItem(
    link='plugins:myplugin:myview',
    link_text='Some text',
    buttons=(
        PluginMenuButton('home', 'Button A', 'fa fa-info', ButtonColorChoices.BLUE),
        PluginMenuButton('home', 'Button B', 'fa fa-warning', ButtonColorChoices.GREEN),
    )
)
```

A `PluginMenuItem` has the following attributes:

| Attribute     | Required | Description                                                                                              |
|---------------|----------|----------------------------------------------------------------------------------------------------------|
| `link`        | Yes      | Name of the URL path to which this menu item links                                                       |
| `link_text`   | Yes      | The text presented to the user                                                                           |
| `permissions` | -        | A list of permissions required to display this link                                                      |
| `staff_only`  | -        | Display only for users who have `is_staff` set to true (any specified permissions will also be required) |
| `buttons`     | -        | An iterable of PluginMenuButton instances to include                                                     |

!!! info "The `staff_only` attribute was introduced in NetBox v3.6.1."

## Menu Buttons

Each menu item can include a set of buttons. These can be handy for providing shortcuts related to the menu item. For instance, most items in NetBox's navigation menu include buttons to create and import new objects.

A `PluginMenuButton` has the following attributes:

| Attribute     | Required | Description                                                        |
|---------------|----------|--------------------------------------------------------------------|
| `link`        | Yes      | Name of the URL path to which this button links                    |
| `title`       | Yes      | The tooltip text (displayed when the mouse hovers over the button) |
| `icon_class`  | Yes      | Button icon CSS class                                              |
| `color`       | -        | One of the choices provided by `ButtonColorChoices`                |
| `permissions` | -        | A list of permissions required to display this button              |

Any buttons associated within a menu item will be shown only if the user has permission to view the link, regardless of what permissions are set on the buttons.

!!! tip
    Supported icons can be found at [Material Design Icons](https://materialdesignicons.com/)
