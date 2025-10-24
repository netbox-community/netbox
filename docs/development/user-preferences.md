# User Preferences

The `users.UserConfig` model holds individual preferences for each user in the form of JSON data. This page serves as a manifest of all recognized user preferences in NetBox.

For end‑user guidance on resetting saved table layouts, see [Features > User Preferences](../features/user-preferences.md#clearing-table-preferences).

## Available Preferences

| Name                       | Description                                                   |
|----------------------------|---------------------------------------------------------------|
| `csv_delimiter`            | The delimiting character used when exporting CSV data         |
| `data_format`              | Preferred format when rendering raw data (JSON or YAML)       |
| `locale.language`          | The language selected for UI translation                      |
| `pagination.per_page`      | The number of items to display per page of a paginated table  |
| `pagination.placement`     | Where to display the paginator controls relative to the table |
| `tables.${table}.columns`  | The ordered list of columns to display when viewing the table |
| `tables.${table}.ordering` | A list of column names by which the table should be ordered   |
| `ui.copilot_enabled`       | Toggles the NetBox Copilot AI agent                           |
| `ui.tables.striping`       | Toggles visual striping of tables in the UI                   |
