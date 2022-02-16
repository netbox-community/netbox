# NetBox v3.2

## v3.2.0 (FUTURE)

!!! warning "Python 3.8 or Later Required"
    NetBox v3.2 requires Python 3.8 or later.

### Breaking Changes

* Automatic redirection of legacy slug-based URL paths has been removed. URL-based slugs were changed to use numeric IDs in v2.11.0.
* The `asn` field has been removed from the site model. Please replicate any site ASN assignments to the ASN model introduced in NetBox v3.1 prior to upgrading.
* The `asn` query filter for sites now matches against the AS number of assigned ASN objects.
* The `contact_name`, `contact_phone`, and `contact_email` fields have been removed from the site model. Please replicate any data remaining in these fields to the contact model introduced in NetBox v3.1 prior to upgrading.
* The `created` field of all change-logged models now conveys a full datetime object, rather than only a date. (Previous date-only values will receive a timestamp of 00:00.) While this change is largely unconcerning, strictly-typed API consumers may need to be updated.
* A `pre_run()` method has been added to the base Report class. Although unlikely to affect most installations, you may need to alter any reports which already use this name for a method.
* Webhook URLs now support Jinja2 templating. Although this is unlikely to introduce any issues, it's possible that an unusual URL might trigger a Jinja2 rendering error, in which case the URL would need to be properly escaped.

### New Features

#### Plugins Framework Extensions ([#8333](https://github.com/netbox-community/netbox/issues/8333))

NetBox's plugins framework has been extended considerably in this release. Additions include:

* Officially-supported generic view classes for common CRUD operations:
    * `ObjectView`
    * `ObjectEditView`
    * `ObjectDeleteView`
    * `ObjectListView`
    * `BulkImportView`
    * `BulkEditView`
    * `BulkDeleteView`
* The `NetBoxModel` base class, which enables various NetBox features, including:
    * Change logging
    * Custom fields
    * Custom links
    * Custom validation
    * Export templates
    * Journaling
    * Tags
    * Webhooks
* Four base form classes for manipulating objects via the UI:
    * `NetBoxModelForm`
    * `NetBoxModelCSVForm`
    * `NetBoxModelBulkEditForm`
    * `NetBoxModelFilterSetForm`
* The `NetBoxModelFilterSet` base class for plugin filter sets
* The `NetBoxTable` base class for rendering object tables with `django-tables2`, as well as various custom column classes
* Function-specific templates (for generic views)
* Various custom template tags and filters
* Plugins can now extend NetBox's GraphQL API with their own schema

No breaking changes to previously supported components have been introduced in this release. However, plugin authors are encouraged to audit their existing code for misuse of unsupported components, as much of NetBox's internal code base has been reorganized.

#### Modules & Module Types ([#7844](https://github.com/netbox-community/netbox/issues/7844))

Several new models have been added to represent field-replaceable device modules, such as line cards installed within a chassis-based switch or router. Similar to devices, each module is instantiated from a user-defined module type, and can have components (interfaces, console ports, etc.) associated with it. These components become available to the parent device once the module has been installed within a module bay. This provides a convenient mechanism to effect the addition and deletion of device components as modules are installed and removed.

Automatic renaming of module components is also supported. When a new module is created, any occurrence of the string `{module}` in a component name will be replaced with the position of the module bay into which the module is being installed.

As with device types, the NetBox community offers a selection of curated real-world module type definitions in our [device type library](https://github.com/netbox-community/devicetype-library). These YAML files can be imported directly to NetBox for your convenience.

#### Custom Object Fields ([#7006](https://github.com/netbox-community/netbox/issues/7006))

Two new types of custom field have been introduced: object and multi-object. These can be used to associate an object in NetBox with some other arbitrary object(s) regardless of its type. For example, you might create a custom field named `primary_site` on the tenant model so that each tenant can have particular site designated as its primary. The multi-object custom field type allows for the assignment of multiple objects of the same type.

Custom field object assignment is fully supported in the REST API, and functions similarly to built-in foreign key relations. Nested representations are provided automatically for each custom field object.

#### Custom Status Choices ([#8054](https://github.com/netbox-community/netbox/issues/8054))

Custom choices can be now added to most object status fields in NetBox. This is done by defining the [`FIELD_CHOICES`](../configuration/optional-settings.md#field_choices) configuration parameter to map field identifiers to an iterable of custom choices an (optionally) colors. These choices are populated automatically when NetBox initializes. For example, the following configuration will add three custom choices for the site status field, each with a designated color:

```python
FIELD_CHOICES = {
    'dcim.Site.status': (
        ('foo', 'Foo', 'red'),
        ('bar', 'Bar', 'green'),
        ('baz', 'Baz', 'blue'),
    )
}
```

This will replace all default choices for this field with those listed. If instead the intent is to _extend_ the set of default choices, this can be done by appending a plus sign (`+`) to the end of the field identifier. For example, the following will add a single extra choice while retaining the defaults provided by NetBox:

```python
FIELD_CHOICES = {
    'dcim.Site.status+': (
        ('fubar', 'FUBAR', 'red'),
    )
}
```

#### Improved User Preferences ([#7759](https://github.com/netbox-community/netbox/issues/7759))

A robust new mechanism for managing user preferences is included in this release. The user preferences form has been improved for better usability, and administrators can now define default preferences for all users with the [`DEFAULT_USER_PREFERENCES`](../configuration/dynamic-settings.md##default_user_preferences) configuration parameter. For example, this can be used to define the columns which appear by default in a table:

```python
DEFAULT_USER_PREFERENCES = {
    'tables': {
        'IPAddressTable': {
            'columns': ['address', 'status', 'created', 'description']
        }
    }
}
```

Users can adjust their own preferences under their user profile. A complete list of supported preferences is available in NetBox's [developer documentation](../development/user-preferences.md).

#### Inventory Item Roles ([#3087](https://github.com/netbox-community/netbox/issues/3087))

A new model has been introduced to represent functional roles for inventory items, similar to device roles. The assignment of roles to inventory items is optional.

#### Inventory Item Templates ([#8118](https://github.com/netbox-community/netbox/issues/8118))

Inventory items can now be templatized on a device type similar to other components (such as interfaces or console ports). This enables users to better pre-model fixed hardware components such as power supplies or hard disks.

Inventory item templates can be arranged hierarchically within a device type, and may be assigned to other templated components. These relationships will be mirrored when instantiating inventory items on a newly-created device (see [#7846](https://github.com/netbox-community/netbox/issues/7846)). For example, if defining an optic assigned to an interface template on a device type, the instantiated device will mimic this relationship between the optic and interface.

#### Service Templates ([#1591](https://github.com/netbox-community/netbox/issues/1591))

A new service template model has been introduced to assist in standardizing the definition and association of applications with devices and virtual machines. As an alternative to manually defining a name, protocol, and port(s) each time a service is created, a user now has the option of selecting a pre-defined template from which these values will be populated.

#### Automatic Provisioning of Next Available VLANs ([#2658](https://github.com/netbox-community/netbox/issues/2658))

A new REST API endpoint has been added at `/api/ipam/vlan-groups/<id>/available-vlans/`. A GET request to this endpoint will return a list of available VLANs within the group. A POST request can be made specifying the name(s) of one or more VLANs to create within the group, and their VLAN IDs will be assigned automatically from the available pool.

Where it is desired to limit the range of available VLANs within a group, users can define a minimum and/or maximum VLAN ID per group (see [#8168](https://github.com/netbox-community/netbox/issues/8168)).

### Enhancements

* [#5429](https://github.com/netbox-community/netbox/issues/5429) - Enable toggling the placement of table pagination controls
* [#6954](https://github.com/netbox-community/netbox/issues/6954) - Remember users' table ordering preferences
* [#7650](https://github.com/netbox-community/netbox/issues/7650) - Expose `AUTH_PASSWORD_VALIDATORS` setting to enforce password validation for local accounts
* [#7679](https://github.com/netbox-community/netbox/issues/7679) - Add actions menu to all object tables
* [#7681](https://github.com/netbox-community/netbox/issues/7681) - Add `service_id` field for provider networks
* [#7784](https://github.com/netbox-community/netbox/issues/7784) - Support cluster type assignment for config contexts
* [#7846](https://github.com/netbox-community/netbox/issues/7846) - Enable associating inventory items with device components
* [#7852](https://github.com/netbox-community/netbox/issues/7852) - Enable the assignment of interfaces to VRFs
* [#7853](https://github.com/netbox-community/netbox/issues/7853) - Add `speed` and `duplex` fields to device interface model
* [#8168](https://github.com/netbox-community/netbox/issues/8168) - Add `min_vid` and `max_vid` fields to VLAN group
* [#8295](https://github.com/netbox-community/netbox/issues/8295) - Jinja2 rendering is now supported for webhook URLs
* [#8296](https://github.com/netbox-community/netbox/issues/8296) - Allow disabling custom links
* [#8307](https://github.com/netbox-community/netbox/issues/8307) - Add `data_type` indicator to REST API serializer for custom fields
* [#8463](https://github.com/netbox-community/netbox/issues/8463) - Change the `created` field on all change-logged models from date to datetime
* [#8572](https://github.com/netbox-community/netbox/issues/8572) - Add a `pre_run()` method for reports
* [#8649](https://github.com/netbox-community/netbox/issues/8649) - Enable customization of configuration module using `NETBOX_CONFIGURATION` environment variable

### Bug Fixes (From Beta)

* [#8655](https://github.com/netbox-community/netbox/issues/8655) - Fix AttributeError when viewing cabled interfaces

### Other Changes

* [#7731](https://github.com/netbox-community/netbox/issues/7731) - Require Python 3.8 or later
* [#7743](https://github.com/netbox-community/netbox/issues/7743) - Remove legacy ASN field from site model
* [#7748](https://github.com/netbox-community/netbox/issues/7748) - Remove legacy contact fields from site model
* [#8031](https://github.com/netbox-community/netbox/issues/8031) - Remove automatic redirection of legacy slug-based URLs
* [#8195](https://github.com/netbox-community/netbox/issues/8195), [#8454](https://github.com/netbox-community/netbox/issues/8454) - Use 64-bit integers for all primary keys
* [#8509](https://github.com/netbox-community/netbox/issues/8509) - `CSRF_TRUSTED_ORIGINS` is now a discrete configuration parameter (rather than being populated from `ALLOWED_HOSTS`)

### REST API Changes

* Added the following endpoints:
    * `/api/dcim/inventory-item-roles/`
    * `/api/dcim/inventory-item-templates/`
    * `/api/dcim/modules/`
    * `/api/dcim/module-bays/`
    * `/api/dcim/module-bay-templates/`
    * `/api/dcim/module-types/`
    * `/api/ipam/service-templates/`
    * `/api/ipam/vlan-groups/<id>/available-vlans/`
* circuits.ProviderNetwork
    * Added `service_id` field
* dcim.ConsolePort
    * Added `module` field
* dcim.ConsoleServerPort
    * Added `module` field
* dcim.FrontPort
    * Added `module` field
* dcim.Interface
    * Added `module`, `speed`, `duplex`, and `vrf` fields
* dcim.InventoryItem
    * Added `component_type`, `component_id`, and `role` fields
    * Added read-only `component` field (GFK)
* dcim.PowerPort
    * Added `module` field
* dcim.PowerOutlet
    * Added `module` field
* dcim.RearPort
    * Added `module` field
* dcim.Site
    * Removed the `asn`, `contact_name`, `contact_phone`, and `contact_email` fields
* extras.ConfigContext
    * Add `cluster_types` field
* extras.CustomField
    * Added `data_type` and `object_type` fields
* extras.CustomLink
    * Added `enabled` field
* ipam.VLANGroup
    * Added the `/availables-vlans/` endpoint
    * Added the `min_vid` and `max_vid` fields
* virtualization.VMInterface
    * Added `vrf` field
