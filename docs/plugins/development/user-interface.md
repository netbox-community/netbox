# User Interface

## Light & Dark Mode

The NetBox user interface supports toggling between light and dark versions of the theme. If needed, a plugin can determine the currently active color theme by inspecting `window.localStorage['netbox-color-mode']`, which will indicate either `light` or `dark`.

Additionally, when the color scheme is toggled by the user, a custom event `netbox.colorModeChanged` indicating the new scheme is dispatched. A plugin can listen for this event if needed to react to the change:

```typescript
window.addEventListener('netbox.colorModeChanged', e => {
  const customEvent = e as CustomEvent<ColorModeData>;
  console.log('New color mode:', customEvent.detail.netboxColorMode);
});
```

## User Preferences

Plugins can register their own user preferences, which are displayed in a dedicated "Plugins" section of each user's preferences page. To do so, create a file named `preferences.py` in your plugin and define a dictionary named `preferences` mapping each preference name to a `UserPreference` instance.

```python title="preferences.py"
from django.utils.translation import gettext_lazy as _
from users.preferences import UserPreference

preferences = {
    'default_view': UserPreference(
        label=_('Default view'),
        choices=(
            ('summary', _('Summary')),
            ('detail', _('Detail')),
        ),
        description=_('The default view for plugin objects'),
    ),
}
```

!!! tip
    The path to the preferences dictionary can be modified by setting `user_preferences` in the PluginConfig instance.

A `UserPreference` accepts the following arguments:

| Argument      | Required | Description                                                                       |
|---------------|----------|-----------------------------------------------------------------------------------|
| `label`       | Yes      | The human-friendly name of the preference                                         |
| `choices`     | Yes      | An iterable of `(value, label)` two-tuples                                        |
| `default`     | -        | The default value for the preference                                              |
| `description` | -        | A brief description of the preference                                             |
| `coerce`      | -        | A callable to convert the submitted value to the appropriate type (e.g. `int`)    |
| `warning`     | -        | A warning message to display alongside the preference                             |

Each preference is stored under the path `plugins.<plugin_name>.<preference_name>`, where `<plugin_name>` is the last component of the plugin's `PluginConfig.name` (e.g. `netbox_foo` for a plugin named `acme.netbox_foo`). Its value for the current user can be retrieved by calling `get()` on the user's config.
