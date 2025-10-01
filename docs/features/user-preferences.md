# User Preferences

NetBox stores per‑user options that control aspects of the web interface and data display. Preferences persist across sessions and can be managed under **User → Preferences**.

## Table configurations

When a list view is configured using **Configure**, NetBox records the selected columns and ordering as per‑user table preferences for that table. These preferences are applied automatically on subsequent visits.

### Clearing table preferences

Saved table preferences may need to be reset, for example, if a table fails to render or after an upgrade that changes available columns.

To clear saved preferences for one or more tables:

1. Click the username in the top‑right corner.
2. Select **Preferences** from the dropdown.
3. Scroll to the **Table Configurations** section.
4. Select the tables to reset.
5. Click **Submit** to clear the selected preferences.

After clearing preferences, reopen the list view and use **Configure** to set the desired columns and ordering.

!!! note
    Per‑user table preferences are distinct from **Table Configs**, which are named, reusable configurations managed under *Customization → Table Configs*. Clearing preferences does not delete any Table Configs. See [Table Configs](../models/extras/tableconfig.md) for details.

## Other preferences

### Language
Selects the user interface language from installed translations (subject to system configuration).

### Page length
Sets the default number of rows displayed on paginated tables.

### Paginator placement
Controls where pagination controls are rendered relative to a table.

### HTMX navigation (experimental)
Enables partial‑page navigation for supported views. Disable this preference if unexpected behavior is observed.

### Striped table rows
Toggles alternating row backgrounds on tables.

### Data format (raw views)
Sets the default format (JSON or YAML) when rendering raw data blocks.

### CSV delimiter
Overrides the delimiter used when exporting CSV data.

## Bookmarks

Users can bookmark frequently visited objects for convenient access. Bookmarks appear under the user menu and can be displayed on the personal dashboard using the bookmarks' widget. See [Bookmark](../models/extras/bookmark.md) for model details.

## Notifications and subscriptions

Users may subscribe to objects to receive notifications when changes occur. Notifications are listed under the user menu and can be marked as read or deleted. See [Features > Notifications](notifications.md) and the data‑model references for [Subscription](../models/extras/subscription.md) and [Notification](../models/extras/notification.md).

## Admin defaults

Administrators can define defaults for new users via [`DEFAULT_USER_PREFERENCES`](../configuration/default-values.md#default_user_preferences). Users may override these values under their own preferences.

## See also

- [Development > User Preferences](../development/user-preferences.md) (manifest of recognized preference keys)
