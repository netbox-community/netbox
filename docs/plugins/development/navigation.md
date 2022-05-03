# Navigation

## Menu Items

To make its views easily accessible to users, a plugin can inject items in NetBox's navigation menu under the "Plugins" header. Menu items are added by defining a list of PluginMenuItem instances. By default, this should be a variable named `menu_items` in the file `navigation.py`. An example is shown below.

!!! tip
    The path to declared menu items can be modified by setting `menu_items` in the PluginConfig instance.

```python
from extras.plugins import PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_animal_sounds:random_animal',
        link_text='Random sound',
        buttons=(
            PluginMenuButton('home', 'Button A', 'fa fa-info', ButtonColorChoices.BLUE),
            PluginMenuButton('home', 'Button B', 'fa fa-warning', ButtonColorChoices.GREEN),
        )
    ),
)
```

A `PluginMenuItem` has the following attributes:

| Attribute     | Required | Description                                          |
|---------------|----------|------------------------------------------------------|
| `link`        | Yes      | Name of the URL path to which this menu item links   |
| `link_text`   | Yes      | The text presented to the user                       |
| `permissions` | -        | A list of permissions required to display this link  |
| `buttons`     | -        | An iterable of PluginMenuButton instances to include |

## Menu Buttons

A `PluginMenuButton` has the following attributes:

| Attribute     | Required | Description                                                        |
|---------------|----------|--------------------------------------------------------------------|
| `link`        | Yes      | Name of the URL path to which this button links                    |
| `title`       | Yes      | The tooltip text (displayed when the mouse hovers over the button) |
| `icon_class`  | Yes      | Button icon CSS class*                                             |
| `color`       | -        | One of the choices provided by `ButtonColorChoices`                |
| `permissions` | -        | A list of permissions required to display this button              |

*NetBox supports [Material Design Icons](https://materialdesignicons.com/).

!!! note
    Any buttons associated within a menu item will be shown only if the user has permission to view the link, regardless of what permissions are set on the buttons.
