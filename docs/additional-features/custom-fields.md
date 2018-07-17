# Custom Fields

Each object in NetBox is represented in the database as a discrete table, and each attribute of an object exists as a column within its table. For example, sites are stored in the `dcim_site` table, which has columns named `name`, `facility`, `physical_address`, and so on. As new attributes are added to objects throughout the development of NetBox, tables are expanded to include new rows.

However, some users might want to associate with objects attributes that are somewhat esoteric in nature, and that would not make sense to include in the core NetBox database schema. For instance, suppose your organization needs to associate each device with a ticket number pointing to the support ticket that was opened to have it installed. This is certainly a legitimate use for NetBox, but it's perhaps not a common enough need to warrant expanding the internal data schema. Instead, you can create a custom field to hold this data.

Custom fields must be created through the admin UI under Extras > Custom Fields. To create a new custom field, select the object(s) to which you want it to apply, and the type of field it will be. NetBox supports six field types:

* Free-form text (up to 255 characters)
* Integer
* Boolean (true/false)
* Date
* URL
* Selection

Assign the field a name. This should be a simple database-friendly string, e.g. `tps_report`. You may optionally assign the field a human-friendly label (e.g. "TPS report") as well; the label will be displayed on forms. If a description is provided, it will appear beneath the field in a form.

Marking the field as required will require the user to provide a value for the field when creating a new object or when saving an existing object. A default value for the field may also be provided. Use "true" or "false" for boolean fields. (The default value has no effect for selection fields.)

When creating a selection field, you should create at least two choices. These choices will be arranged first by weight, with lower weights appearing higher in the list, and then alphabetically.

## Using Custom Fields

When a single object is edited, the form will include any custom fields which have been defined for the object type. These fields are included in the "Custom Fields" panel. On the backend, each custom field value is saved separately from the core object as an independent database call, so it's best to avoid adding too many custom fields per object.

When editing multiple objects, custom field values are saved in bulk. There is no significant difference in overhead when saving a custom field value for 100 objects versus one object. However, the bulk operation must be performed separately for each custom field.
