# NetBox v3.2

## v3.2.9 (2022-08-16)

### Enhancements

* [#8595](https://github.com/netbox-community/netbox/issues/8595) - Add PON interface types
* [#8723](https://github.com/netbox-community/netbox/issues/8723) - Enable bulk renaming of devices
* [#9161](https://github.com/netbox-community/netbox/issues/9161) - Pretty print JSON custom field data when editing
* [#9505](https://github.com/netbox-community/netbox/issues/9505) - Display extra addressing details for IPv4 prefixes
* [#9625](https://github.com/netbox-community/netbox/issues/9625) - Add phone & email details to contacts panel
* [#9857](https://github.com/netbox-community/netbox/issues/9857) - Add clear button to quick search fields
* [#9933](https://github.com/netbox-community/netbox/issues/9933) - Add DOCSIS interface type

### Bug Fixes

* [#9491](https://github.com/netbox-community/netbox/issues/9491) - Remove button for adding inventory item templates to module type components
* [#9979](https://github.com/netbox-community/netbox/issues/9979) - Fix Markdown rendering for custom fields in table columns
* [#9986](https://github.com/netbox-community/netbox/issues/9986) - Workaround for upstream timezone data bug

---

## v3.2.8 (2022-08-08)

### Enhancements

* [#9062](https://github.com/netbox-community/netbox/issues/9062) - Add/edit {module} substitution to help text for component template name
* [#9637](https://github.com/netbox-community/netbox/issues/9637) - Add site group field to rack reservation form
* [#9762](https://github.com/netbox-community/netbox/issues/9762) - Add `nat_outside` column to the IPAddress table
* [#9825](https://github.com/netbox-community/netbox/issues/9825) - Add contacts column to virtual machines table
* [#9881](https://github.com/netbox-community/netbox/issues/9881) - Increase granularity in utilization graph values
* [#9882](https://github.com/netbox-community/netbox/issues/9882) - Add manufacturer column to modules table
* [#9883](https://github.com/netbox-community/netbox/issues/9883) - Linkify location column in power panels table
* [#9906](https://github.com/netbox-community/netbox/issues/9906) - Include `color` attribute in front & rear port YAML import/export

### Bug Fixes

* [#9827](https://github.com/netbox-community/netbox/issues/9827) - Fix assignment of module bay position during bulk creation
* [#9871](https://github.com/netbox-community/netbox/issues/9871) - Fix utilization graph value alignments
* [#9884](https://github.com/netbox-community/netbox/issues/9884) - Prevent querying assigned VRF on prefix object init
* [#9885](https://github.com/netbox-community/netbox/issues/9885) - Fix child prefix counts when editing/deleting aggregates in bulk
* [#9891](https://github.com/netbox-community/netbox/issues/9891) - Ensure consistent ordering for tags during object serialization
* [#9919](https://github.com/netbox-community/netbox/issues/9919) - Fix potential XSS avenue via linked objects in tables
* [#9948](https://github.com/netbox-community/netbox/issues/9948) - Fix TypeError exception when requesting API tokens list as non-authenticated user
* [#9949](https://github.com/netbox-community/netbox/issues/9949) - Fix KeyError exception resulting from invalid API token provisioning request
* [#9950](https://github.com/netbox-community/netbox/issues/9950) - Prevent redirection to arbitrary URLs via `next` parameter on login URL
* [#9952](https://github.com/netbox-community/netbox/issues/9952) - Prevent InvalidMove when attempting to assign a nested child object as parent

---

## v3.2.7 (2022-07-20)

### Enhancements

* [#9705](https://github.com/netbox-community/netbox/issues/9705) - Support filter expressions for the `serial` field on racks, devices, and inventory items
* [#9741](https://github.com/netbox-community/netbox/issues/9741) - Check for UserConfig instance during user login
* [#9745](https://github.com/netbox-community/netbox/issues/9745) - Add wireless LANs and links to global search

### Bug Fixes

* [#9437](https://github.com/netbox-community/netbox/issues/9437) - Standardize form submission buttons and behavior when using enter key
* [#9499](https://github.com/netbox-community/netbox/issues/9499) - Fix filtered bulk deletion of VM Interfaces
* [#9634](https://github.com/netbox-community/netbox/issues/9634) - Fix image URLs in rack elevations when using external storage
* [#9715](https://github.com/netbox-community/netbox/issues/9715) - Fix `SOCIAL_AUTH_PIPELINE` config parameter not taking effect
* [#9754](https://github.com/netbox-community/netbox/issues/9754) - Fix regression introduced by #9632
* [#9746](https://github.com/netbox-community/netbox/issues/9746) - Permit filtering interfaces by arbitrary speed value in UI
* [#9749](https://github.com/netbox-community/netbox/issues/9749) - Retain original slug values when modifying object names
* [#9775](https://github.com/netbox-community/netbox/issues/9775) - Fix exception when viewing a report with no description

---

## v3.2.6 (2022-07-11)

### Enhancements

* [#7702](https://github.com/netbox-community/netbox/issues/7702) - Enable dynamic configuration for default powerfeed attributes
* [#9396](https://github.com/netbox-community/netbox/issues/9396) - Allow filtering modules by bay ID
* [#9403](https://github.com/netbox-community/netbox/issues/9403) - Enable modifying virtual chassis properties when creating/editing a device
* [#9540](https://github.com/netbox-community/netbox/issues/9540) - Add filters for assigned device & VM to IP addresses list
* [#9686](https://github.com/netbox-community/netbox/issues/9686) - Add tenant group column for all object tables with tenant assignments

### Bug Fixes

* [#8854](https://github.com/netbox-community/netbox/issues/8854) - Fix `REMOTE_AUTH_DEFAULT_GROUPS` for social-auth backends
* [#9575](https://github.com/netbox-community/netbox/issues/9575) - Fix AttributeError exception for FHRP group with an IP address assigned
* [#9597](https://github.com/netbox-community/netbox/issues/9597) - Include `installed_module` in module bay REST API serializer
* [#9632](https://github.com/netbox-community/netbox/issues/9632) - Automatically focus on search box when expanding dropdowns
* [#9657](https://github.com/netbox-community/netbox/issues/9657) - Fix filtering for custom fields and webhooks in the UI
* [#9682](https://github.com/netbox-community/netbox/issues/9682) - Fix bulk assignment of ASNs to sites
* [#9687](https://github.com/netbox-community/netbox/issues/9687) - Don't restrict custom text field lengths when entering via UI form
* [#9704](https://github.com/netbox-community/netbox/issues/9704) - Include `last_updated` field on JournalEntry REST API serializer

---

## v3.2.5 (2022-06-20)

### Enhancements

* [#8704](https://github.com/netbox-community/netbox/issues/8704) - Shift-click to select multiple objects in a list
* [#8882](https://github.com/netbox-community/netbox/issues/8882) - Support filtering IP addresses by multiple parent prefixes
* [#8893](https://github.com/netbox-community/netbox/issues/8893) - Include count of IP ranges under tenant view
* [#9417](https://github.com/netbox-community/netbox/issues/9417) - Initialize manufacturer selection when inserting a new module
* [#9501](https://github.com/netbox-community/netbox/issues/9501) - Add support for custom Jinja2 filters
* [#9517](https://github.com/netbox-community/netbox/issues/9517) - Linkify related power port on power outlet view
* [#9525](https://github.com/netbox-community/netbox/issues/9525) - Provide one-click edit link for objects in tables
* [#9533](https://github.com/netbox-community/netbox/issues/9533) - Move Markdown reference to local documentation
* [#9534](https://github.com/netbox-community/netbox/issues/9534) - Add VLAN group selector to interface bulk edit forms
* [#9556](https://github.com/netbox-community/netbox/issues/9556) - Leave dropdown open upon selection for multi-select fields

### Bug Fixes

* [#8944](https://github.com/netbox-community/netbox/issues/8944) - Fix rendering of Markdown links with colons
* [#9108](https://github.com/netbox-community/netbox/issues/9108) - Fix rendering of bracketed Markdown links
* [#9374](https://github.com/netbox-community/netbox/issues/9374) - Improve performance when retrieving devices/VMs with config context data
* [#9466](https://github.com/netbox-community/netbox/issues/9466) - Avoid sending webhooks after script/report failure
* [#9480](https://github.com/netbox-community/netbox/issues/9480) - Fix sorting services & service templates by port numbers
* [#9484](https://github.com/netbox-community/netbox/issues/9484) - Include services listening on "all IPs" under IP address view
* [#9486](https://github.com/netbox-community/netbox/issues/9486) - Fix redirect URL when adding device components from the module view
* [#9495](https://github.com/netbox-community/netbox/issues/9495) - Correct link to contacts in contact groups table column
* [#9503](https://github.com/netbox-community/netbox/issues/9503) - Hyperlinks in rack elevation SVGs must always use absolute URLs
* [#9512](https://github.com/netbox-community/netbox/issues/9512) - Fix duplicate site results when searching by ASN
* [#9524](https://github.com/netbox-community/netbox/issues/9524) - Correct order of VLAN fields under VM interface creation form
* [#9537](https://github.com/netbox-community/netbox/issues/9537) - Ensure consistent use of placeholder tag throughout UI
* [#9549](https://github.com/netbox-community/netbox/issues/9549) - Fix device counts for rack list under rack role view

---

## v3.2.4 (2022-05-31)

### Enhancements

* [#8374](https://github.com/netbox-community/netbox/issues/8374) - Display device type and asset tag if name is blank but asset tag is populated
* [#8922](https://github.com/netbox-community/netbox/issues/8922) - Add service list to IP address view
* [#9098](https://github.com/netbox-community/netbox/issues/9098) - Add "other" types for power ports/outlets, pass-through ports
* [#9239](https://github.com/netbox-community/netbox/issues/9239) - Enable filtering by contact group for all models which support contact assignment
* [#9277](https://github.com/netbox-community/netbox/issues/9277) - Introduce `CSRF_COOKIE_NAME` configuration parameter
* [#9347](https://github.com/netbox-community/netbox/issues/9347) - Include services in global search
* [#9379](https://github.com/netbox-community/netbox/issues/9379) - Redirect to virtual chassis view after adding a member device
* [#9451](https://github.com/netbox-community/netbox/issues/9451) - Add `export_raw` argument for TemplateColumn

### Bug Fixes

* [#9094](https://github.com/netbox-community/netbox/issues/9094) - Fix partial address search within Prefix and Aggregate filters
* [#9291](https://github.com/netbox-community/netbox/issues/9291) - Improve data validation for MultiObjectVar script fields
* [#9358](https://github.com/netbox-community/netbox/issues/9358) - Annotate circuit count for providers list under ASN view
* [#9387](https://github.com/netbox-community/netbox/issues/9387) - Ensure ActionsColumn `extra_buttons` are always displayed
* [#9402](https://github.com/netbox-community/netbox/issues/9402) - Fix custom field population when creating a virtual chassis
* [#9407](https://github.com/netbox-community/netbox/issues/9407) - Clean up display of prefixes values when exporting prefixes list
* [#9420](https://github.com/netbox-community/netbox/issues/9420) - Fix custom script class inheritance
* [#9425](https://github.com/netbox-community/netbox/issues/9425) - Fix bulk import for object and multi-object custom fields
* [#9430](https://github.com/netbox-community/netbox/issues/9430) - Fix passing of initial form data for DynamicModelChoiceFields

---

## v3.2.3 (2022-05-12)

### Enhancements

* [#8805](https://github.com/netbox-community/netbox/issues/8805) - Add "mixed" option for device airflow indication
* [#8894](https://github.com/netbox-community/netbox/issues/8894) - Include full names when listing users
* [#8998](https://github.com/netbox-community/netbox/issues/8998) - Enable filtering racks & reservations by site group
* [#9122](https://github.com/netbox-community/netbox/issues/9122) - Introduce `clearcache` management command & clear cache during upgrade
* [#9221](https://github.com/netbox-community/netbox/issues/9221) - Add definition list support for Markdown
* [#9260](https://github.com/netbox-community/netbox/issues/9260) - Apply user preferences to tables under object detail views
* [#9278](https://github.com/netbox-community/netbox/issues/9278) - Linkify device types count under manufacturers list
* [#9280](https://github.com/netbox-community/netbox/issues/9280) - Allow adopting existing components when installing a module
* [#9314](https://github.com/netbox-community/netbox/issues/9314) - Add device and VM filters for FHRP group assignments
* [#9340](https://github.com/netbox-community/netbox/issues/9340) - Introduce support for error reporting via Sentry
* [#9343](https://github.com/netbox-community/netbox/issues/9343) - Add Ubiquiti SmartPower power outlet type

### Bug Fixes

* [#9190](https://github.com/netbox-community/netbox/issues/9190) - Prevent exception when attempting to instantiate module components which already exist on the parent device
* [#9267](https://github.com/netbox-community/netbox/issues/9267) - Remove invalid entry in IP address role choices
* [#9296](https://github.com/netbox-community/netbox/issues/9296) - Improve Markdown link sanitization
* [#9306](https://github.com/netbox-community/netbox/issues/9306) - Include VC master interfaces when selecting a LAG/bridge for a VC member interface
* [#9311](https://github.com/netbox-community/netbox/issues/9311) - Permit creating contact assignment without a priority via the REST API
* [#9313](https://github.com/netbox-community/netbox/issues/9313) - Remove HTML code from CSV output of many-to-many relationships
* [#9330](https://github.com/netbox-community/netbox/issues/9330) - Add missing `module_type` field to REST API serializers for modular device component templates

---

## v3.2.2 (2022-04-28)

### Enhancements

* [#9060](https://github.com/netbox-community/netbox/issues/9060) - Add device type filters for device bays, module bays, and inventory items
* [#9152](https://github.com/netbox-community/netbox/issues/9152) - Annotate related object type under custom field view
* [#9192](https://github.com/netbox-community/netbox/issues/9192) - Add Ubiquiti SmartPower connector type
* [#9214](https://github.com/netbox-community/netbox/issues/9214) - Linkify cluster counts in cluster type & group tables

### Bug Fixes

* [#4264](https://github.com/netbox-community/netbox/issues/4264) - Treat 0th IP as unusable for IPv6 prefixes (excluding /127s)
* [#8941](https://github.com/netbox-community/netbox/issues/8941) - Fix dynamic dropdown behavior when browser is zoomed
* [#8959](https://github.com/netbox-community/netbox/issues/8959) - Prevent exception when refreshing scripts list (avoid race condition)
* [#9132](https://github.com/netbox-community/netbox/issues/9132) - Limit location options by selected site when creating a wireless link
* [#9133](https://github.com/netbox-community/netbox/issues/9133) - Upgrade script should require Python 3.8 or later
* [#9138](https://github.com/netbox-community/netbox/issues/9138) - Avoid inadvertent form submission when utilizing quick search field on object lists
* [#9151](https://github.com/netbox-community/netbox/issues/9151) - Child prefix counts not annotated on aggregates list under RIR view
* [#9156](https://github.com/netbox-community/netbox/issues/9156) - Fix loading UserConfig data from fixtures
* [#9158](https://github.com/netbox-community/netbox/issues/9158) - Do not list tags field for CSV forms which do not support tag assignment
* [#9194](https://github.com/netbox-community/netbox/issues/9194) - Support position assignment when add module bays to multiple devices
* [#9206](https://github.com/netbox-community/netbox/issues/9206) - Show header for comments field under module & module type creation views
* [#9222](https://github.com/netbox-community/netbox/issues/9222) - Fix circuit ID display under cable view
* [#9227](https://github.com/netbox-community/netbox/issues/9227) - Fix related object assignment when recording change record for interfaces

---

## v3.2.1 (2022-04-14)

### Enhancements

* [#5479](https://github.com/netbox-community/netbox/issues/5479) - Allow custom job timeouts for scripts & reports
* [#8543](https://github.com/netbox-community/netbox/issues/8543) - Improve filtering for wireless LAN VLAN selection
* [#8920](https://github.com/netbox-community/netbox/issues/8920) - Limit number of non-racked devices displayed
* [#8956](https://github.com/netbox-community/netbox/issues/8956) - Retain old script/report results for configured lifetime
* [#8973](https://github.com/netbox-community/netbox/issues/8973) - Display VLAN group count under site view
* [#9081](https://github.com/netbox-community/netbox/issues/9081) - Add `fhrpgroup_id` filter for IP addresses
* [#9099](https://github.com/netbox-community/netbox/issues/9099) - Enable display of installed module serial & asset tag in module bays list
* [#9110](https://github.com/netbox-community/netbox/issues/9110) - Add Neutrik proprietary power connectors
* [#9123](https://github.com/netbox-community/netbox/issues/9123) - Improve appearance of SSO login providers

### Bug Fixes

* [#8931](https://github.com/netbox-community/netbox/issues/8931) - Copy assigned tenant when cloning a location
* [#9055](https://github.com/netbox-community/netbox/issues/9055) - Restore ability to move inventory item to other device
* [#9057](https://github.com/netbox-community/netbox/issues/9057) - Fix missing instance counts for module types
* [#9061](https://github.com/netbox-community/netbox/issues/9061) - Fix general search for device components
* [#9065](https://github.com/netbox-community/netbox/issues/9065) - Min/max VID should not be required when filtering VLAN groups
* [#9079](https://github.com/netbox-community/netbox/issues/9079) - Fail validation when an inventory item is assigned as its own parent
* [#9096](https://github.com/netbox-community/netbox/issues/9096) - Remove duplicate filter tag when filtering by "none"
* [#9100](https://github.com/netbox-community/netbox/issues/9100) - Include position field in module type YAML export
* [#9116](https://github.com/netbox-community/netbox/issues/9116) - `assigned_to_interface` filter for IP addresses should not match FHRP group assignments
* [#9118](https://github.com/netbox-community/netbox/issues/9118) - Fix validation error when importing VM child interfaces
* [#9128](https://github.com/netbox-community/netbox/issues/9128) - Resolve component labels per module bay position when installing modules

---

## v3.2.0 (2022-04-05)

!!! warning "Python 3.8 or Later Required"
    NetBox v3.2 requires Python 3.8 or later.

!!! warning "Deletion of Legacy Data"
    This release includes a database migration that will remove the `asn`, `contact_name`, `contact_phone`, and `contact_email` fields from the site model. (These fields have been superseded by the ASN and contact models introduced in NetBox v3.1.) To protect against the accidental destruction of data, the upgrade process **will fail** if any sites still have data in any of these fields. To bypass this safeguard, set the `NETBOX_DELETE_LEGACY_DATA` environment variable when running the upgrade script, which will permit the destruction of legacy data.

!!! tip "Migration Scripts"
    A set of [migration scripts](https://github.com/netbox-community/migration-scripts) is available to assist with the migration of legacy site data.

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
* `NetBoxModelViewSet` and several base serializer classes now provide enhanced REST API functionality
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

Custom choices can be now added to most object status fields in NetBox. This is done by defining the [`FIELD_CHOICES`](../configuration/data-validation.md#field_choices) configuration parameter to map field identifiers to an iterable of custom choices an (optionally) colors. These choices are populated automatically when NetBox initializes. For example, the following configuration will add three custom choices for the site status field, each with a designated color:

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

A robust new mechanism for managing user preferences is included in this release. The user preferences form has been improved for better usability, and administrators can now define default preferences for all users with the [`DEFAULT_USER_PREFERENCES`](../configuration/default-values.md#default_user_preferences) configuration parameter. For example, this can be used to define the columns which appear by default in a table:

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
* [#8496](https://github.com/netbox-community/netbox/issues/8496) - Enable assigning multiple ASNs to a provider
* [#8572](https://github.com/netbox-community/netbox/issues/8572) - Add a `pre_run()` method for reports
* [#8593](https://github.com/netbox-community/netbox/issues/8593) - Add a `link` field for contacts
* [#8649](https://github.com/netbox-community/netbox/issues/8649) - Enable customization of configuration module using `NETBOX_CONFIGURATION` environment variable
* [#9006](https://github.com/netbox-community/netbox/issues/9006) - Enable custom fields, custom links, and tags for journal entries

### Bug Fixes (From Beta2)

* [#8658](https://github.com/netbox-community/netbox/issues/8658) - Fix display of assigned components under inventory item lists
* [#8838](https://github.com/netbox-community/netbox/issues/8838) - Fix FieldError exception during global search
* [#8845](https://github.com/netbox-community/netbox/issues/8845) - Correct default ASN formatting in table
* [#8869](https://github.com/netbox-community/netbox/issues/8869) - Fix NoReverseMatch exception when displaying tag w/assignments
* [#8872](https://github.com/netbox-community/netbox/issues/8872) - Enable filtering by custom object fields
* [#8970](https://github.com/netbox-community/netbox/issues/8970) - Permit nested inventory item templates on device types
* [#8976](https://github.com/netbox-community/netbox/issues/8976) - Add missing `object_type` field on CustomField REST API serializer
* [#8978](https://github.com/netbox-community/netbox/issues/8978) - Fix instantiation of front ports when provisioning a module
* [#9007](https://github.com/netbox-community/netbox/issues/9007) - Fix FieldError exception when instantiating a device type with nested inventory items

### Other Changes

* [#7731](https://github.com/netbox-community/netbox/issues/7731) - Require Python 3.8 or later
* [#7743](https://github.com/netbox-community/netbox/issues/7743) - Remove legacy ASN field from site model
* [#7748](https://github.com/netbox-community/netbox/issues/7748) - Remove legacy contact fields from site model
* [#8031](https://github.com/netbox-community/netbox/issues/8031) - Remove automatic redirection of legacy slug-based URLs
* [#8195](https://github.com/netbox-community/netbox/issues/8195), [#8454](https://github.com/netbox-community/netbox/issues/8454) - Use 64-bit integers for all primary keys
* [#8509](https://github.com/netbox-community/netbox/issues/8509) - `CSRF_TRUSTED_ORIGINS` is now a discrete configuration parameter (rather than being populated from `ALLOWED_HOSTS`)
* [#8684](https://github.com/netbox-community/netbox/issues/8684) - Change custom link template context variable `obj` to `object` (backward-compatible)

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
* circuits.Provider
    * Added `asns` field
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
* extras.JournalEntry
    * Added `custom_fields` and `tags` fields
* ipam.ASN
    * Added `provider_count` field
* ipam.VLANGroup
    * Added the `/availables-vlans/` endpoint
    * Added `min_vid` and `max_vid` fields
* tenancy.Contact
    * Added `link` field
* virtualization.VMInterface
    * Added `vrf` field
