# Custom Fields

NetBox administrators can extend NetBox's built-in data model by adding custom fields to most object types. See the [custom fields documentation](../../customization/custom-fields.md) for more information.

## Fields

### Model(s)

Select the NetBox object type or types to which this custom field applies.

### Name

The raw field name. This will be used in the database and API, and should consist only of alphanumeric characters and underscores. (Use the `label` field to designate a human-friendly name for the custom field.)

### Label

An optional human-friendly name for the custom field. If not defined, the field's `name` attribute will be used.

### Group Name

If this custom field should be grouped with others, specify the name of the group here. Custom fields with no group defined will be ordered only by weight and name.

### Type

The type of data this field holds. This must be one of the following:

| Type               | Description                                                        |
|--------------------|--------------------------------------------------------------------|
| Text               | Free-form text (intended for single-line use)                      |
| Long text          | Free-form of any length; supports Markdown rendering               |
| Integer            | A whole number (positive or negative)                              |
| Boolean            | True or false                                                      |
| Date               | A date in ISO 8601 format (YYYY-MM-DD)                             |
| URL                | This will be presented as a link in the web UI                     |
| JSON               | Arbitrary data stored in JSON format                               |
| Selection          | A selection of one of several pre-defined custom choices           |
| Multiple selection | A selection field which supports the assignment of multiple values |
| Object             | A single NetBox object of the type defined by `object_type`        |
| Multiple object    | One or more NetBox objects of the type defined by `object_type`    |

### Object Type

For object and multiple-object fields only. Designates the type of NetBox object being referenced.

### Weight

A numeric weight used to override alphabetic ordering of fields by name. Custom fields with a lower weight will be listed before those with a higher weight. (Note that weight applies within the context of a custom field group, if defined.)

### Required

If checked, this custom field must be populated with a valid value for the object to pass validation.

### Description

A brief description of the field's purpose (optional).

### Filter Logic

Defines how filters are evaluated against custom field values.

| Option   | Description                         |
|----------|-------------------------------------|
| Disabled | Filtering disabled                  |
| Loose    | Match any occurrence of the value   |
| Exact    | Match only the complete field value |

### UI Visible

Controls whether the custom field is displayed for objects within the NetBox user interface.

| Option | Description                                                    |
|--------|----------------------------------------------------------------|
| Always | The field is always displayed when viewing an object (default) |
| If set | The field is displayed only if a value has been defined        |
| Hidden | The field is not displayed when viewing an object              |

### UI Editable

Controls whether the custom field is editable on objects within the NetBox user interface.

| Option | Description                                                                  |
|--------|------------------------------------------------------------------------------|
| Yes    | The field's value may be changed when editing an object (default)            |
| No     | The field's value is displayed when editing an object but may not be altered |
| Hidden | The field is not displayed when editing an object                            |

### Default

The default value to populate for the custom field when creating new objects (optional). This value must be expressed as JSON. If this is a choice or multi-choice field, this must be one of the available choices.

### Choice Set

For selection and multi-select custom fields only, this is the [set of choices](./customfieldchoiceset.md) which are valid for the field.

### Cloneable

If enabled, values from this field will be automatically pre-populated when cloning existing objects.

### Minimum Value

For numeric custom fields only. The minimum valid value (optional).

### Maximum Value

For numeric custom fields only. The maximum valid value (optional).

### Validation Regex

For string-based custom fields only. A regular expression used to validate the field's value (optional).
