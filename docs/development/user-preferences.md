# User Preferences

The `users.UserConfig` model holds individual preferences for each user in the form of JSON data. This page serves as a manifest of all recognized user preferences in NetBox.

## Available Preferences

| Name                     | Description                                                   |
|--------------------------|---------------------------------------------------------------|
| data_format              | Preferred format when rendering raw data (JSON or YAML)       |
| pagination.per_page      | The number of items to display per page of a paginated table  |
| pagination.placement     | Where to display the paginator controls relative to the table |
| tables.${table}.columns  | The ordered list of columns to display when viewing the table |
| tables.${table}.ordering | A list of column names by which the table should be ordered   |
| ui.colormode             | Light or dark mode in the user interface                      |
