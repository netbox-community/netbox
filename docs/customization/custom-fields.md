# Custom Fields

Each model in NetBox is represented in the database as a discrete table, and each attribute of a model exists as a column within its table. For example, sites are stored in the `dcim_site` table, which has columns named `name`, `facility`, `physical_address`, and so on. As new attributes are added to objects throughout the development of NetBox, tables are expanded to include new rows.

However, some users might want to store additional object attributes that are somewhat esoteric in nature, and that would not make sense to include in the core NetBox database schema. For instance, suppose your organization needs to associate each device with a ticket number correlating it with an internal support system record. This is certainly a legitimate use for NetBox, but it's not a common enough need to warrant including a field for _every_ NetBox installation. Instead, you can create a custom field to hold this data.

Within the database, custom fields are stored as JSON data directly alongside each object. This alleviates the need for complex queries when retrieving objects.

## Creating Custom Fields

Custom fields may be created by navigating to Customization > Custom Fields. NetBox supports many types of custom field:

* Text: Free-form text (intended for single-line use)
* Long text: Free-form of any length; supports Markdown rendering
* Integer: A whole number (positive or negative)
* Decimal: A fixed-precision decimal number (4 decimal places)
* Boolean: True or false
* Date: A date in ISO 8601 format (YYYY-MM-DD)
* Date & time: A date and time in ISO 8601 format (YYYY-MM-DD HH:MM:SS)
* URL: This will be presented as a link in the web UI. Values are restricted to the schemes permitted by [`ALLOWED_URL_SCHEMES`](../configuration/security.md#allowed_url_schemes). A value entered without a scheme (e.g. `example.com`) is assumed to use `https` and stored as an absolute URL (e.g. `https://example.com`).
* JSON: Arbitrary data stored in JSON format
* Selection: A selection of one of several pre-defined custom choices
* Multiple selection: A selection field which supports the assignment of multiple values
* Object: A single NetBox object of the type defined by `object_type`
* Multiple object: One or more NetBox objects of the type defined by `object_type`

Each custom field must have a name. This should be a simple database-friendly string (e.g. `tps_report`) and may contain only alphanumeric characters and underscores. You may also assign a corresponding human-friendly label (e.g. "TPS report"); the label will be displayed on web forms. A weight is also required: Higher-weight fields will be ordered lower within a form. (The default weight is 100.) If a description is provided, it will appear beneath the field in a form.

Marking a field as required will force the user to provide a value for the field when creating a new object or when saving an existing object. A default value for the field may also be provided. Use "true" or "false" for boolean fields, or the exact value of a choice for selection fields.

A custom field must be assigned to one or more object types, or models, in NetBox. Once created, custom fields will automatically appear as part of these models in the web UI and REST API. Note that not all models support custom fields.

!!! info "This behavior changed in NetBox v4.6.8."
    To improve performance when creating custom fields, empty field values are no longer pre-provisioned.

Unless the field has been assigned a default value, creating a custom field does not write a value to the objects which already exist. An object which has never been assigned a value simply stores nothing for the field, and reports the field as having no value in the web UI, REST API, GraphQL API, and exports, exactly as if it stored an explicit null.

This matters only if you query the underlying `custom_field_data` JSON directly, for example in a custom script. The field's key is absent from an object's data until a value is assigned to it, so read it with `obj.cf['field_name']` or `obj.custom_field_data.get('field_name')` rather than by direct subscript.

Assigning a default value, by contrast, does write that value to every existing object at the time the field is created, so that objects can be filtered by it immediately. Note that a default added to a field which already exists is _not_ backfilled: objects with no value continue to report none until they are next saved.

### Field Status

!!! info "This behavior was introduced in NetBox v4.7.0."

Creating a custom field with a default value, and deleting a custom field, both require rewriting the stored data of the objects the field applies to. Where the field is assigned to a large number of objects, this cannot be completed within the request, so it is handed to a background job instead and the field reports its status accordingly:

| Status | Meaning |
| ------ | ------- |
| Active | The field is live and available for use. |
| Provisioning | The field's default value is being written to existing objects. |
| Deleting | The field's data is being removed from existing objects. |

Whether a background job is required is determined by the total number of objects of the field's assigned object types, measured against the [`BULK_UPDATE_CHUNK_SIZE`](../configuration/system.md#bulk_update_chunk_size) configuration parameter — not by how many of those objects actually hold a value for the field. Deleting a field assigned to a large table is therefore deferred even where the field holds no data at all: NetBox cannot count the objects holding a value without scanning the entire table, which is the cost the threshold exists to avoid.

A field is live only while active. During provisioning or deletion it does not appear on objects, in forms, in filters, or in either API, and its stored data is read and written by nothing but the job responsible for it; it becomes available (or disappears entirely) once the job completes. Objects created in the meantime are unaffected — a field being provisioned still supplies its default to new objects.

A field which is not active cannot be modified while its job runs, as its configuration must not change under the job rewriting its data. This includes assigning it further object types, and unassigning those it already carries: such a change is rejected until the field is live again.

A field pending deletion continues to occupy its name until its data has been removed, so that a new field cannot be created — and an existing field cannot be renamed — to a name whose old values are still present on objects.

These operations require a running [background worker](../features/background-jobs.md) (`rqworker`). A field left mid-operation, for example because no worker was running or because its job failed, remains in its pending status until that job runs to completion.

Such a field can always be deleted, whichever status it holds. Deleting one already pending deletion queues a fresh job to finish removing its data. A field left provisioning has no equivalent in-application retry: requeue its job from the background queues (**Admin > System > Background Tasks**, which requires a staff account), or delete the field and create it again.

!!! note
    Unassigning an object type from a custom field still removes the field's data from those objects immediately, and remains subject to the request timeout on very large tables. The same applies to renaming a custom field.

### Filtering

The filter logic controls how values are matched when filtering objects by the custom field. Loose filtering (the default) matches on a partial value, whereas exact matching requires a complete match of the given string to a field's value. For example, exact filtering with the string "red" will only match the exact value "red", whereas loose filtering will match on the values "red", "red-orange", or "bored". Setting the filter logic to "disabled" disables filtering by the field entirely.

### Grouping

Related custom fields can be grouped together within the UI by assigning each the same group name. When at least one custom field for an object type has a group defined, it will appear under the group heading within the custom fields panel under the object view. All custom fields with the same group name will appear under that heading. (Note that the group names must match exactly, or each will appear as a separate heading.)

This parameter has no effect on the API representation of custom field data.

### Visibility & Editing

When creating a custom field, users can control the conditions under which it may be displayed and edited within the NetBox user interface. The following choices are available for controlling the display of a custom field on an object:

* **Always** (default): The custom field is included when viewing an object.
* **If Set**: The custom field is included only if a value has been defined for the object.
* **Hidden**: The custom field will never be displayed within the UI. This option is recommended for fields which are not intended for use by human users.

Additionally, the following options are available for controlling whether custom field values can be altered within the NetBox UI:

* **Yes** (default): The custom field's value may be modified when editing an object.
* **No**: The custom field is displayed for reference when editing an object, but its value may not be modified.
* **Hidden**: The custom field is not displayed when editing an object.

Note that this setting has no impact on the REST or GraphQL APIs: Custom field data will always be available via either API.

### Validation

NetBox supports limited custom validation for custom field values. Following are the types of validation enforced for each field type:

* Text: Regular expression (optional)
* Integer: Minimum and/or maximum value (optional)
* Selection: Must exactly match one of the prescribed choices
* JSON: Must adhere to the defined validation schema (if any)

### Custom Selection Fields

Each custom selection field must designate a [choice set](../models/extras/customfieldchoiceset.md) containing at least two choices. These are specified as a comma-separated list.

If a default value is specified for a selection field, it must exactly match one of the provided choices. The value of a multiple selection field will always return a list, even if only one value is selected.

### Custom Object Fields

An object or multi-object custom field can be used to refer to a particular NetBox object or objects as the "value" for a custom field. These custom fields must define an `object_type`, which determines the type of object to which custom field instances point.

By default, an object choice field will make all objects of that type available for selection in the drop-down. The list choices can be filtered to show only objects with certain values by providing a `query_params` dict in the Related Object Filter field, as a JSON value. More information about `query_params` can be found [here](./custom-scripts.md#objectvar).

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

Selection and multiple selection fields are returned as objects exposing both the stored value and its human-friendly label, following the same convention used by NetBox's built-in choice fields:

```json
    "custom_fields": {
        "site_type": {
            "value": "datacenter",
            "label": "Data Center"
        },
        "regions": [
            {
                "value": "us-east",
                "label": "US East"
            },
            {
                "value": "us-west",
                "label": "US West"
            }
        ]
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

As with built-in choice fields, selection custom fields are written by passing the raw value (e.g. `"site_type": "datacenter"`), not the `{value, label}` object returned on read.

The GraphQL API's `custom_fields` field resolves selection and multiple selection values to the same `{value, label}` representation.
