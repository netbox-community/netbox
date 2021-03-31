# Custom Fields

Each model in NetBox is represented in the database as a discrete table, and each attribute of a model exists as a column within its table. For example, sites are stored in the `dcim_site` table, which has columns named `name`, `facility`, `physical_address`, and so on. As new attributes are added to objects throughout the development of NetBox, tables are expanded to include new rows.

However, some users might want to store additional object attributes that are somewhat esoteric in nature, and that would not make sense to include in the core NetBox database schema. For instance, suppose your organization needs to associate each device with a ticket number correlating it with an internal support system record. This is certainly a legitimate use for NetBox, but it's not a common enough need to warrant including a field for _every_ NetBox installation. Instead, you can create a custom field to hold this data.

Within the database, custom fields are stored as JSON data directly alongside each object. This alleviates the need for complex queries when retrieving objects.

## Creating Custom Fields

Custom fields must be created through the admin UI under Extras > Custom Fields. NetBox supports six types of custom field:

* Text: Free-form text (up to 255 characters)
* Integer: A whole number (positive or negative)
* Boolean: True or false
* Date: A date in ISO 8601 format (YYYY-MM-DD)
* URL: This will be presented as a link in the web UI
* Selection: A selection of one of several pre-defined custom choices
* Multiple selection: A selection field which supports the assignment of multiple values

Each custom field must have a name; this should be a simple database-friendly string, e.g. `tps_report`. You may also assign a corresponding human-friendly label (e.g. "TPS report"); the label will be displayed on web forms. A weight is also required: Higher-weight fields will be ordered lower within a form. (The default weight is 100.) If a description is provided, it will appear beneath the field in a form.

Marking a field as required will force the user to provide a value for the field when creating a new object or when saving an existing object. A default value for the field may also be provided. Use "true" or "false" for boolean fields, or the exact value of a choice for selection fields.

The filter logic controls how values are matched when filtering objects by the custom field. Loose filtering (the default) matches on a partial value, whereas exact matching requires a complete match of the given string to a field's value. For example, exact filtering with the string "red" will only match the exact value "red", whereas loose filtering will match on the values "red", "red-orange", or "bored". Setting the filter logic to "disabled" disables filtering by the field entirely.

A custom field must be assigned to one or object types, or models, in NetBox. Once created, custom fields will automatically appear as part of these models in the web UI and REST API. Note that not all models support custom fields.

### Custom Field Validation

NetBox supports limited custom validation for custom field values. Following are the types of validation enforced for each field type:

* Text: Regular expression (optional)
* Integer: Minimum and/or maximum value (optional)
* Selection: Must exactly match one of the prescribed choices

### Custom Selection Fields

Each custom selection field must have at least two choices. These are specified as a comma-separated list. Choices appear in forms in the order they are listed. Note that choice values are saved exactly as they appear, so it's best to avoid superfluous punctuation or symbols where possible.

If a default value is specified for a selection field, it must exactly match one of the provided choices. The value of a multiple selection field will always return a list, even if only one value is selected.

## Custom Fields in Templates

Several features within NetBox, such as export templates and webhooks, utilize Jinja2 templating. For convenience, objects which support custom field assignment expose custom field data through the `cf` property. This is a bit cleaner than accessing custom field data through the actual field (`custom_field_data`).

For example, a custom field named `foo123` on the Site model is accessible on an instance as `{{ site.cf.foo123 }}`.

## Custom Fields and the REST API

When retrieving an object via the REST API, all of its custom data will be included within the `custom_fields` attribute. For example, below is the partial output of a site with two custom fields defined:

```json
{
    "id": 123,
    "url": "http://localhost:8000/api/dcim/sites/123/",
    "name": "Raleigh 42",
    ...
    "custom_fields": {
        "deployed": "2018-06-19",
        "site_code": "US-NC-RAL42"
    },
    ...
```

To set or change these values, simply include nested JSON data. For example:

```json
{
    "name": "New Site",
    "slug": "new-site",
    "custom_fields": {
        "deployed": "2019-03-24"
    }
}
```
