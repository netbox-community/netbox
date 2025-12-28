# Table Configs

This object represents the saved configuration of an object table in NetBox. Table configs can be crafted, saved, and shared among users to apply specific views within object lists. Each table config can specify which table columns to display, the order in which to display them, and which columns are used for sorting.

For example, you might wish to create a table config for the devices list to assist in inventory tasks. This view might show the device name, location, serial number, and asset tag, but omit operational details like IP addresses. Once applied, this table config can be saved for reuse in future audits.

!!! note
    Per‑user table preferences (columns and ordering remembered for an individual user) are distinct from Table Configs. If a list view fails to render due to outdated saved preferences, see [Clearing table preferences](../../features/user-preferences.md#clearing-table-preferences).

## Fields

### Name

A human-friendly name for the table config.

### User

The user to which this filter belongs. The current user will be assigned automatically when saving a table config via the UI, and cannot be changed.

### Object Type

The type of NetBox object to which the table config pertains.

### Table

The name of the specific table to which the table config pertains. (Some NetBox objects use multiple tables.)

### Weight

A numeric weight used to influence the order in which table configs are listed. Table configs with a lower weight will be listed before those with a higher weight. Table configs having the same weight will be ordered alphabetically.

### Enabled

Determines whether this table config can be used. Disabled table configs will not appear as options in the UI, however they will be included in API results.

### Shared

Determines whether this table config is intended for use by all users or only its owner. Note that deselecting this option does **not** hide the table config from other users; it is merely excluded from the list of available table configs in UI object list views.

### Ordering

A list of column names by which the table is to be ordered. If left blank, the table's default ordering will be used.

### Columns

A list of columns to be displayed in the table. The table will render these columns in the order they appear in the list. At least one column must be selected.
